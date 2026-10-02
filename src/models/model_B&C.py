"""
B&C Model for BSS-TSP

This module implements a branch and check (B&C) algorithm
for solving the battery swap stochastic traveling salesman problem (BS-STSP).

Output file:
    result_B&C.txt
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


def model(V_,scenarios,n,B):

    # Add subtour cut, feasibility cut and optimality cut
    def Cut(model,where):
        if where == GRB.Callback.MIPSOL:
            edges = [(i,j) for (i,j) in x if model.cbGetSolution(x[i,j]) > 0.5]
            G = networkx.Graph()
            G.add_edges_from(edges)
            Components = list(networkx.connected_components(G))
            x_val = {(i,j): model.cbGetSolution(x[i,j]) for (i,j) in arcs_}
            # If no subtour, make route and add feasibility cut and optimality cut
            if len(Components) == 1:

                # Make SP_s for every scenario
                scenario_obj = []
                for s, (c_scenario, d_scenario, d_scenario_, _) in enumerate(scenarios):
                    SP = Model(f'SP_{s}')
                    y  = SP.addVars(arcs_, vtype=GRB.BINARY, name='y')
                    e  = SP.addVars(arcs_, vtype=GRB.CONTINUOUS, name='e')# Added mileage after a swap
                    E = SP.addVars([i for i in V_], vtype=GRB.CONTINUOUS,ub=B, name='E')

                    # xy constraints
                    SP.addConstrs(x_val[i,j] >= y[i,j]  for (i,j) in arcs_)

                    # Mileage flow constraints
                    SP.addConstr( E[0] == B)
                    SP.addConstrs(E[j] <= E[i] - c_scenario[i,j]*x_val[i,j] +B*(1-x_val[i,j]+y[i,j]) for (i,j) in arcs_)
                    SP.addConstrs(E[j] <= E[i] - (d_scenario[i,j]+d_scenario_[i,j])*y[i,j] + e[i,j] + B*(1-y[i,j]) for (i,j) in arcs_)

                    # Battery capacity constraints for a swap
                    SP.addConstrs(B>=E[i]-d_scenario[i,j]*y[i,j]+e[i,j] for (i,j) in arcs_)
                    SP.addConstrs(e[i,j]<=B*y[i,j] for (i,j) in arcs_)
                    # Mileage feasible constants
                    SP.addConstrs(E[i]-c_scenario[i,j]*(x_val[i,j]-y[i,j])>=0 for (i,j) in arcs_)
                    SP.addConstrs(E[i]-d_scenario[i,j]*y[i,j]>=0 for (i,j) in arcs_)

                    # Objective function minimize total detour distance
                    SP.setObjective(quicksum(y[i,j]*(d_scenario[i,j]+d_scenario_[i,j]-c_scenario[i,j]) for (i,j) in arcs_), GRB.MINIMIZE)

                    SP.Params.OutputFlag = 0 
                    SP.optimize()

                    if SP.Status == GRB.INFEASIBLE:
                        scenario_obj.append(float('inf'))
                        break # no need to solve other scenarios
                    else:
                        scenario_obj.append(SP.ObjVal)

                # Make equation for cuts
                eq = 0
                for i,j in arcs_:
                    if x_val[i,j] <= 0.5:
                        eq += x[i,j]
                    else:
                        eq += 1 - x[i,j]

                # Add cuts
                if any(obj == float('inf') for obj in scenario_obj):
                    # expected_obj=float('inf')
                    # feasibility cut
                    model.cbLazy(eq >= 1)
                else:
                    expected_obj = sum(prob * obj_val for obj_val, (_, _, _, prob) in zip(scenario_obj, scenarios))
                    # optimality cut
                    model.cbLazy(σ >= expected_obj * (1 - eq))
                return
            # Subtour cut
            for S in Components:
                model.cbLazy(quicksum(x[i,j] for i in S for j in S if j!=i) <= len(S)-1)

    MP = Model('MP')

    # Make variables
    arcs_ = [(i,j) for i in V_ for j in V_ if j!=i]
    x  = MP.addVars(arcs_, vtype=GRB.BINARY, name='x')
    σ = MP.addVar(vtype=GRB.CONTINUOUS,name='σ')

    # Tour constraints
    # Outdegree constraints
    MP.addConstrs((quicksum(x[i,j] for j in V_ if j != i) == 1) for i in V_ if i != n+1)  # All nodes except destination have outdegree 1
    MP.addConstr(quicksum(x[n+1,j] for j in V_ if j != n+1) == 0)  # Destination has outdegree 0
    # Indegree constraints
    MP.addConstrs((quicksum(x[i,j] for i in V_ if i != j) == 1) for j in V_ if j != 0)  # All nodes except origin have indegree 1
    MP.addConstr(quicksum(x[i,0] for i in V_ if i != 0) == 0)  # Origin has indegree 0

    # Calculate the cost of the first stage using the expected value
    expected_c = {}
    for (i,j) in arcs_:
        expected_c[i,j] = sum(prob * c_scenario[i,j] for c_scenario, _, _, prob in scenarios)

    MP.setObjective(quicksum(x[i,j]*expected_c[i,j] for (i,j) in arcs_)+σ, GRB.MINIMIZE)
    MP.Params.lazyConstraints = 1
    MP.Params.Threads = 12
    MP.Params.timeLimit = 1000
    MP.optimize(Cut)

    # Get optimal route
    try:
        edges = [(i,j) for (i,j) in arcs_ if x[i,j].X > 0.5]
        optimal_route = make_route(edges)
        optimal_route += [0]
        route_str = " ".join(map(str, optimal_route))
    except:
        route_str = "inf"
    with open('result_B&C.txt', 'a') as f:
        if MP.Status == GRB.OPTIMAL or MP.Status == GRB.TIME_LIMIT:
            f.write(f"{xml_file}\t{MP.ObjVal:.2f}\t{MP.Runtime:.2f}\t{MP.MIPGap*100:.1f}%\t{route_str}\n")
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
                    V_,c,d,d_,n = read_xml_info(f"..\..\data\{xml_file}",copy_depot = True)
                    scenarios = generate_scenarios(c, d, d_, scenario_size)
                    model(V_,scenarios,n,B)
        print("",file=open('result_B&C.txt', 'a'))  # Add a blank line after each scenarios size