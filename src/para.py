"""
All the setting about parameters (distance metrics, scenarios) and reading instance from XML file.
"""
import xml.etree.ElementTree as ET
import os,math,random


def distance(x1,y1,x2,y2):
    """
    Calculate Euclidean distance and round to 2 decimal places.
    """
    return round(math.sqrt((x2-x1)**2 + (y2-y1)**2),2)

def read_xml_info(xml_file,copy_depot = False,strategy="nearest_BS"):
    """
    We only use the location data of depot, customer nodes and charge stations (battery swap station in our paper) to fit our problem.

    Args:
        copy_depot (bool): Defaults to False.
        strategy (str): Charging station assignment strategy. 
            Available options: "nearest_BS", "min_detour". Defaults to "min_detour".
    Returns:
        V: node range (depot and customer nodes).
        c: distance between i,j.
        d: distance between i and the assigned charging station.
        d_: distance between the assigned charging station and j.
        customer_num: number of customer nodes.
    """

    # Parse XML
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Print basic instance information
    print("\n=== Instance Information ===")
    print(f"Dataset: {root.find('.//dataset').text}")
    print(f"Instance Name: {root.find('.//name').text}")


    # Depot location
    depot = root.find('.//node[@type="0"]')
    k=0
    V_x = {k: float(depot.find('cx').text)}
    V_y = {k: float(depot.find('cy').text)}

    # Customer node location
    for node in root.findall('.//node[@type="1"]'):
        k+=1
        V_x[k] =  float(node.find('cx').text)
        V_y[k] =  float(node.find('cy').text)
    customer_num = k

    # Copy a depot for handle E[i] variables in model
    if copy_depot == True:
        k+=1
        V_x[k] = float(depot.find('cx').text)
        V_y[k] = float(depot.find('cy').text)

    # Node range (depot and customer nodes).
    V=range(0,k+1)

    c = {}
    for i in V:
        for j in V:
            if j != i:
                c[i,j] = distance(V_x[i],V_y[i],V_x[j],V_y[j])


    CS_x={}
    CS_y={}
    m=0
    for node in root.findall('.//node[@type="2"]'):
        m+=1
        CS_x[k+m] =  float(node.find('cx').text)
        CS_y[k+m] =  float(node.find('cy').text)
    CS = range(k+1,k+m+1)

    if strategy == "nearest_BS":
        d={}
        d_={}
        for (i,j) in c:
            d[i,j]=float("inf")
            for k in CS:
                dis=distance(V_x[i],V_y[i],CS_x[k],CS_y[k])
                if dis<d[i,j]:
                    d[i,j]=dis
                    d_[i,j]=distance(V_x[j],V_y[j],CS_x[k],CS_y[k])
    
    if strategy == "min_detour":
        d={}
        d_={}
        for (i,j) in c:
            min_total_detour = float("inf")
            for k in CS:
                dis_i=distance(V_x[i],V_y[i],CS_x[k],CS_y[k])
                dis_j=distance(V_x[j],V_y[j],CS_x[k],CS_y[k])
                total_detour = dis_i + dis_j
                if total_detour < min_total_detour:
                    min_total_detour = total_detour
                    d[i,j] = dis_i
                    d_[i,j] = dis_j

    return V,c,d,d_,customer_num


def generate_scenarios(c, d, d_, scenarios_size: int, min_factor=0.8, max_factor=1.2):
    """
    Scenarios_size=1时，return actual distances, otherwise return random distances in scenarios.
    Generate random scenarios, in each scenario c, d, d_ are multiplied by a random factor between [min_factor, max_factor].

    Parameters:
    - V: node range.
    - c: distance between i,j.
    - d: distance between i and the assigned charging station.
    - d_: distance between the assigned charging station and j.
    - scenarios_size: 
    - min_factor: 
    - max_factor: 

    Returns:
    - scenarios: Scenarios list, each Scenario includes (c_scenario, d_scenario, d_scenario, probability)
    """

    scenarios = []
    probability = 1.0 / scenarios_size  # Equal probability for each scenario

    # If only one scenario, set factor to 1.0 to return actual distances
    if scenarios_size == 1:
        min_factor = 1.0
        max_factor = 1.0

    for s in range(scenarios_size):
        c_scenario = {}
        d_scenario = {}
        d_scenario_ = {}

        # For each arc (i, j), generate a consistent random factor based on the arc length c[i,j] and scenario s.
        # This avoiding random issues caused by depot duplication and range V change.
        for (i, j) in c.keys():
            distance_hash = hash((round(c[(i,j)], 6), s))
            arc_seed = distance_hash % 100000
            random.seed(arc_seed)
            factor = random.uniform(min_factor, max_factor)

            c_scenario[(i, j)] = c[(i, j)] * factor
            d_scenario[(i, j)] = d[(i, j)] * factor
            d_scenario_[(i, j)] = d_[(i, j)] * factor

        scenarios.append((c_scenario, d_scenario, d_scenario_, probability))


    return scenarios

if __name__ == "__main__":

    xml_file = "../Data/tc0c10s2cf1.xml"

    if os.path.exists(xml_file):
        read_xml_info(xml_file)
    else:
        print(f"Error: File {xml_file} not found!")
