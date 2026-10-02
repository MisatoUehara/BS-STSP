"""
B&C-DP-ACs Model for BS-STSP

This module implements a branch and check with dynamic programming (B&C-DP)
and analytical cuts (AC) for solving the battery swap stochastic traveling salesman problem (BS-STSP).

The dynamic programming is used to solve the second stage problem for each scenario.
The analytical cuts are improved optimality and feasibility cut based on the dynamic programming
structure.

Output file:
    result_B&C-DP-ACs.txt
Output file format:
    instance    obj (kilometer)    solving_time (seconds)    gap    optimal_route (for stage 1)
Output file note:
    INF: infeasible instance.
    inf: no feasible solution found in timelimit.
    Instance and optimal route can be load on https://vrp-rep.github.io/mapper/

"""
import networkx,sys
from gurobipy import *

sys.path.append("..")
from para import *
from functions import *
from DP import *


def model(V,scenarios,_,B):

    # Add subtour cut, feasibility cut and optimality cut
    def Cut(model,where):
        if where == GRB.Callback.MIPSOL:
            edges = [(i,j) for (i,j) in x if model.cbGetSolution(x[i,j]) > 0.5]
            G = networkx.Graph()
            G.add_edges_from(edges)
            Components = list(networkx.connected_components(G))
            x_val = {(i,j): model.cbGetSolution(x[i,j]) for (i,j) in arcs}
            # If no subtour, make route and add feasibility cut and optimality cut
            if len(Components) == 1:
                route = make_route(edges)
                route = route + [0]
                arc_routes=[(route[i],route[i+1]) for i in range(len(route)-1)]

                # Make SP_s for every scenario
                scenario_obj = []
                for s, (c_scenario, d_scenario, d__scenario, _) in enumerate(scenarios):

                    obj,SP_s_obj,MIS = DynamicProgramming(c_scenario, d_scenario, d__scenario, B, arc_routes)

                    if obj == float('inf'):  # if infeasible
                        scenario_obj.append(float('inf'))
                        MISs = lifting(c_scenario, d_scenario, d__scenario, B, arc_routes,initial_inf_subpath=MIS)
                        break # no need to solve other scenarios
                    else:
                        scenario_obj.append(SP_s_obj)

                # # Make equation for cuts
                # eq = 0
                # for i,j in arcs:
                #     if x_val[i,j] <= 0.5:
                #         eq += x[i,j]
                #     else:
                #         eq += 1 - x[i,j]

                # Add cuts
                if any(obj == float('inf') for obj in scenario_obj):

                    # # Analytical feasibility cut lifting
                    for k in range(len(MISs)):
                        model.cbLazy(quicksum(1-x[i,j] for (i,j) in MISs[k]) >= 1)
                else:
                    # Calculate eq by every senario
                    expected_obj = sum(prob * obj_val for obj_val, (_, _, _, prob) in zip(scenario_obj, scenarios))
                    eq = quicksum(
                        (1-x[i,j]) * sum(prob * (d_scenario[i,j] + d_scenario_[i,j] - c_scenario[i,j]) 
                                        for c_scenario, d_scenario, d_scenario_, prob in scenarios)
                        for (i,j) in edges)

                    # Analytical optimality cut
                    model.cbLazy(σ >= expected_obj - eq)
                return
            # Subtour cut
            for S in Components:
                model.cbLazy(quicksum(x[i,j] for i in S for j in S if j!=i) <= len(S)-1)

    MP = Model('MP')

    # Make variables
    arcs = [(i,j) for i in V for j in V if j!=i]
    x  = MP.addVars(arcs, vtype=GRB.BINARY, name='x')
    σ = MP.addVar(vtype=GRB.CONTINUOUS,name='σ')

    # Tour constraints
    MP.addConstrs(quicksum(x[i,j] for j in V if j != i) == 1 for i in V)
    MP.addConstrs(quicksum(x[j,i] for j in V if j != i) == 1 for i in V)

    # Calculate the cost of the first stage using the expected value
    expected_c = {}
    for (i,j) in arcs:
        expected_c[i,j] = sum(prob * c_scenario[i,j] for c_scenario, _, _, prob in scenarios)

    MP.setObjective(quicksum(x[i,j]*expected_c[i,j] for (i,j) in arcs)+σ, GRB.MINIMIZE)
    MP.Params.lazyConstraints = 1
    MP.Params.Threads = 12
    MP.Params.timeLimit = 1000
    MP.optimize(Cut)

    # Get optimal route
    try:
        edges = [(i,j) for (i,j) in arcs if x[i,j].X > 0.5]
        optimal_route = make_route(edges)
        optimal_route += [0]
        route_str = " ".join(map(str, optimal_route))
    except:
        route_str = "inf"
    with open('result_B&C-DP-ACs.txt', 'a') as f:
        if MP.Status == GRB.OPTIMAL or MP.Status == GRB.TIME_LIMIT:
            f.write(f"{xml_file}\t{MP.ObjVal:.2f}\t{MP.Runtime:.2f}\t-\t{route_str}\n")
        elif MP.Status == GRB.INFEASIBLE:
            f.write(f"{xml_file}\tINF\t{MP.Runtime:.2f}\tINF\tINF\n")
        else:
            f.write(f"{xml_file}\tOther\t{MP.Runtime:.2f}\tOther\tOther\n")

if __name__ == "__main__":

    # Make instances
    directory = "..\..\data"
    xml_files_list = get_file_names(read_xml_files(directory))
    B=300 #battery size (kilometer)

    # Loop through instances
    for scenario_size in [1, 10, 50]:
        for customer_size in ['10', '20', '40']:
            for xml_file in xml_files_list:
                if xml_file[4:6] == customer_size:
                    V,c,d,d_,n = read_xml_info(f"..\..\data\{xml_file}",copy_depot = False)
                    scenarios = generate_scenarios(c, d, d_, scenario_size)
                    model(V,scenarios,n,B)
        print("",file=open('result_B&C-DP-ACs.txt', 'a'))  # Add a blank line after each scenarios size