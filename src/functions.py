"""
Functions used in models.
"""
import os,glob

def make_route(edges):
    """
    Construct a route from a list of edges starting from depot (node 0).
    
    Args:
        edges: List of edge tuples (i,j)
        
    Returns:
        route: Ordered list of nodes forming the route
    """
    routes = []
    current = 0  # start from 0(depot)
    visited = set()
    routes.append(current)
    visited.add(current)
    while len(visited) < len(edges):
        for (i,j) in edges:
            if i == current and j not in visited:
                current = j
                routes.append(current)
                visited.add(current)
                break
            elif j == current and i not in visited:
                current = i 
                routes.append(current)
                visited.add(current)
                break
    return routes

def read_xml_files(directory):
    xml_files = glob.glob(os.path.join(directory, "*.xml"))
    return xml_files

def get_file_names(file_paths):
    return [os.path.basename(file_path) for file_path in file_paths]
