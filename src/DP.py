"""
Dynamic Programming for the subproblem and infeasible subpath list detection (analytical feasibility cut lifting).
"""


def DynamicProgramming(c, d, d_, B, arc_routes, see_cal=False):
    """
    Solve the subproblem using dynamic programming to find minimum detour distance.

    Args:
        c: Direct distance dictionary
        d: Detour distance dictionary
        d_: Detour distance dictionary
        B: Battery capacity
        arc_routes: List of arcs in the route in order

    Returns:
        total_distance: Total distance including detours
        detour_mileage: Additional distance due to detours
        MIS: Minimal Infeasible Subsystem if any
        see_cal: Only true for illustration example in main()
    """

    # Special case check: sufficient battery to reach destination directly
    direct_mileage=0
    for arc in arc_routes:
        direct_mileage+=c[arc]
    if direct_mileage<=B:
        total_distance=direct_mileage
        detour_mileage=0
        return total_distance, detour_mileage, None

    # Construct reachability variable g
    g=[[] for arc in arc_routes]  # g[0] represents direct reachability to destination
    # Points that need charging to reach destination
    for arc in arc_routes:
        sum_mileage=d_[arc]
        # Check reachable subsequent points
        for i in arc_routes[arc_routes.index(arc)+1:]:
            sum_mileage+=d[i]
            i_at=arc_routes.index(i)
            if sum_mileage<B:
                g[arc_routes.index(arc)].append(i_at)
                sum_mileage-=d[i]
                sum_mileage+=c[i]
            # Early termination
            elif sum_mileage-d[i]+c[i]>B:
                break
            # Skip this point
            else:
                sum_mileage-=d[i]
                sum_mileage+=c[i]
    # Points that can reach destination directly after charging
    for arc in arc_routes[::-1]:
        sum_mileage=d_[arc]
        for i in arc_routes[arc_routes.index(arc)+1:]:
            sum_mileage+=c[i]
        # Check if can reach destination directly
        if sum_mileage<=B:
            g[arc_routes.index(arc)].append("D")

    # Dynamic programming calculation
    # Backward pass for route planning, forward pass for distance calculation
    H=[[] for arc in arc_routes]  # Distance dictionary
    q=[[] for arc in arc_routes]  # Next charging point
    h=[float('inf') for arc in arc_routes]  # Minimum distance from each point
    for arc in arc_routes[::-1]:

        arc_at=arc_routes.index(arc)
        for i in g[arc_at]:
            sum_mileage=d[arc]+d_[arc]
            if i=="D":
                # Direct to destination
                for j in arc_routes[arc_at+1:]:
                    sum_mileage+=c[j]
            else:
                # Reachable point
                for j in arc_routes[arc_at+1:i]:
                    sum_mileage+=c[j]
                sum_mileage+=h[i]
            H[arc_at].append(sum_mileage)
        if H[arc_at]!=[]:  # Skip infeasible segments
            min_mileage=min(H[arc_at])
            h[arc_at]=min_mileage
            if min_mileage!=float('inf'):
                q[arc_at]=g[arc_at][H[arc_at].index(min_mileage)]

    # Virtual starting point calculation
    dummy_g=[]
    dummy_H=[]
    sum_mileage=0
    for arc in arc_routes:
        arc_at=arc_routes.index(arc)
        sum_mileage+=d[arc]
        if sum_mileage<B:
            dummy_g.append(arc_routes.index(arc))
            sum_mileage-=d[arc]
            dummy_H.append(sum_mileage)
            sum_mileage+=c[arc]
        # Early termination
        elif sum_mileage-d[arc]+c[arc]>B:
            break
        # Skip this point
        else:
            sum_mileage-=d[arc]
            sum_mileage+=c[arc]

    # Calculate total distance from starting point
    for idx, i in enumerate(dummy_g):
        dummy_H[idx] += h[i]

    try:
        total_distance=min(dummy_H)
        dummy_q=dummy_g[dummy_H.index(total_distance)]
    except:
        total_distance=float('inf')

    # Find infeasible subpath when infeasible
    if total_distance == float('inf'):
        end_of_subpath_idx = -1
        for k in range(len(arc_routes) - 1, -1, -1):
            if h[k] == float('inf'):
                end_of_subpath_idx = k
                break
        MIS=arc_routes[end_of_subpath_idx:]
    else:
        MIS=None

    # # See calculation
    if see_cal==True:
        print("")
        print("g:",g) #g_0 to g_n
        print("dummy_g:",dummy_g) #g_-1
        print("")
        print("h:",H) #h_0 to h_n
        print("dummy_h:",total_distance) #h_-1
        print("")

    return total_distance,total_distance-direct_mileage,MIS

def find_critical_paths(paths):
    """
    Args:
        paths: List of paths to filter
        
    Returns:
        critical_paths: List of critical (non-dominated) paths
    """
    # Deduplication and filter None values
    unique_paths = list({tuple(path): path for path in paths if path is not None}.values())
    
    if not unique_paths:
        return []
    
    # Sort by length
    unique_paths.sort(key=len)
    
    critical_paths = []
    processed_sets = []  # Cache processed sets
    
    for _, path in enumerate(unique_paths):
        path_set = set(path)
        is_critical = True
        
        # Only compare with shorter paths
        for other_set in processed_sets:
            if other_set.issubset(path_set):
                is_critical = False
                break
        
        if is_critical:
            critical_paths.append(path)
            processed_sets.append(path_set)
    
    return critical_paths

def lifting(c, d, d_, B, arc_routes,initial_inf_subpath):
    """
    Lifting the infeasible subpath for analytical feasibility cut.

    Args:
        c: Direct distance dictionary
        d: Detour distance dictionary
        d_: Detour distance dictionary
        B: Battery capacity
        arc_routes: List of arcs in the route in order
        inf_subpath: Initial infeasible subpath

    Returns:
        MISs: a set of MIS
    """
    MISs=[initial_inf_subpath]
    for k in range(len(arc_routes) - 1, -1, -1):
        _,_,initial_inf_subpath=DynamicProgramming(c, d, d_,B,arc_routes[:k])
        MISs.append(initial_inf_subpath)
    MISs=find_critical_paths(MISs)

    return MISs

if __name__ == "__main__":

    import sys
    sys.path.append("..") 
    from para import *

    # Load an example instance and route
    xml_file='tc0c10s2cf1.xml'
    _,c,d,d_,_ = read_xml_info(f"../Data/{xml_file}")
    route = [0, 2, 5, 9, 4, 3, 1, 6, 10, 8, 7, 0]

    # # Battery size in kilometers
    B=100 

    # Create arc routes
    arc_routes=[(route[i],route[i+1]) for i in range(len(route)-1)]

    # Round the dictionary values for the illustrative example
    c = {key: round(value) for key, value in c.items()}
    d = {key: round(value) for key, value in d.items()}
    d_ = {key: round(value) for key, value in d_.items()}

    # Solve the subproblem with Dynamic Programming
    obj,detour_mileage,MIS=DynamicProgramming(c, d, d_, B, arc_routes, see_cal=True)
    print("obj:",obj)
    print("SP_obj:",detour_mileage)
    print("MIS:",MIS)
    # Find MISs F for an infeasible case
    if obj==float('inf'):
        MISs=lifting(c, d, d_, B, arc_routes,initial_inf_subpath=MIS)
        print("MISs:",MISs)