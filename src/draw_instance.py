"""Draw instance layout from XML data for publication style.
We recommend readers using https://vrp-rep.github.io/mapper to show the instances and optimized routes.
"""
import xml.etree.ElementTree as ET
import matplotlib.pyplot as plt
import numpy as np
import os

def read_xml_data(file_path):
    """Read XML file and extract node information"""
    tree = ET.parse(file_path)
    root = tree.getroot()
    
    nodes = {'depot': [], 'customers': [], 'charging_stations': []}
    
    # Parse node information
    for node in root.find('network').find('nodes').findall('node'):
        node_id = int(node.get('id'))
        node_type = int(node.get('type'))
        cx = float(node.find('cx').text)
        cy = float(node.find('cy').text)
        
        if node_type == 0:  # Depot
            nodes['depot'].append((node_id, cx, cy))
        elif node_type == 1:  # Customer nodes
            nodes['customers'].append((node_id, cx, cy))
        elif node_type == 2:  # Charging stations
            nodes['charging_stations'].append((node_id, cx, cy))
    
    return nodes

def plot_instance(nodes, instance_name):
    """Plot network diagram"""
    # Set figure size and DPI for high quality output
    plt.figure(figsize=(5, 4), dpi=200)
    
    # Set scientific publication style
    plt.style.use('default')
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.linewidth'] = 1.2
    
    # Plot depot
    if nodes['depot']:
        depot_coords = np.array([(x, y) for _, x, y in nodes['depot']])
        plt.scatter(depot_coords[:, 0], depot_coords[:, 1], 
                   c='red', marker='s', s=120, 
                   label='Depot', edgecolors='black', linewidth=1, zorder=3)
        
        # Add depot labels
        for node_id, x, y in nodes['depot']:
            plt.annotate(f'{node_id}', (x, y), ha='center', va='center',
                        fontsize=8, color='black')
    
    # Plot customer nodes
    if nodes['customers']:
        customer_coords = np.array([(x, y) for _, x, y in nodes['customers']])
        plt.scatter(customer_coords[:, 0], customer_coords[:, 1], 
                   c='orange', marker='o', s=100, 
                   label='Customer', edgecolors='black', linewidth=1, zorder=2)
        
        # Add customer node labels
        for node_id, x, y in nodes['customers']:
            plt.annotate(f'{node_id}', (x, y), ha='center', va='center',
                        fontsize=9, color='black')
    
    # Plot charging stations (BSS)
    if nodes['charging_stations']:
        cs_coords = np.array([(x, y) for _, x, y in nodes['charging_stations']])
        plt.scatter(cs_coords[:, 0], cs_coords[:, 1], 
                   c='green', marker='^', s=120, 
                   label='BSS', edgecolors='black', linewidth=1, zorder=2)
        
        # Add charging station labels
        for node_id, x, y in nodes['charging_stations']:
            plt.annotate(f'{node_id}', (x, y), ha='center', va='center',
                        fontsize=8, color='black')
    
    # Set axis labels and title
    plt.xlabel('X Coordinate (km)', fontsize=14, fontweight='bold')
    plt.ylabel('Y Coordinate (km)', fontsize=14, fontweight='bold')
    plt.title(f'Layout for Instance: {instance_name}', 
              fontsize=16, fontweight='bold', pad=20)
    
    # Set legend
    plt.legend(loc='upper left', frameon=True, fancybox=True, 
               shadow=False, fontsize=10, framealpha=0.9)
    
    # Add grid
    plt.grid(True, alpha=0.3, linestyle='--', linewidth=0.8)
    
    # Set axis range with appropriate margins
    all_x = []
    all_y = []
    for node_type in nodes.values():
        for _, x, y in node_type:
            all_x.append(x)
            all_y.append(y)
    
    if all_x and all_y:
        x_margin = (max(all_x) - min(all_x)) * 0.1
        y_margin = (max(all_y) - min(all_y)) * 0.1
        plt.xlim(min(all_x) - x_margin, max(all_x) + x_margin)
        plt.ylim(min(all_y) - y_margin, max(all_y) + y_margin)
    
    # Set axis ticks
    plt.xticks(fontsize=11)
    plt.yticks(fontsize=11)

    # Adjust layout
    plt.tight_layout()

    # # Save image
    # output_path = f'instance_plot_{instance_name}.png'
    # plt.savefig(output_path, dpi=300, bbox_inches='tight', 
    #             facecolor='white', edgecolor='none')
    # print(f"Image saved as: {output_path}")
    
    # Show image
    plt.show()

def main(path):
    """Main function to read XML and plot instance"""
    
    # Check if file exists
    if not os.path.exists(path):
        print(f"Error: File not found {path}")
        return
    
    try:
        # Read data
        nodes = read_xml_data(path)
        # Extract instance name
        instance_name = os.path.basename(path).replace('.xml', '')
        # Print node information
        print(f"Instance: {instance_name}")
        print(f"Number of depots: {len(nodes['depot'])}")
        print(f"Number of customers: {len(nodes['customers'])}")
        print(f"Number of charging stations: {len(nodes['charging_stations'])}")
        print("-" * 40)
        # Plot network
        plot_instance(nodes, instance_name)        
    except Exception as e:
        print(f"Error processing file: {e}")

if __name__ == "__main__":
    # XML file path
    path = '../data/tc0c10s2cf1.xml'
    main(path)
