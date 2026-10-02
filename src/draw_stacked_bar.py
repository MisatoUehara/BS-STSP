"""Generate combined stacked bar chart and line plot for scientific publication."""
import matplotlib.pyplot as plt
import numpy as np

def create_combined_chart():
    """Create a combined stacked bar chart and line plot with scientific publication style"""
    # Data from the provided table
    categories = ['LBBD', 'B&C', 'B&C-DP', 'B&C-DP-ACs/AFC']
    values1 = [165, 167, 176, 176]  # First row
    values2 = [137, 137, 159, 172]  # Second row  
    values3 = [16, 20, 26, 137]     # Third row
    
    # Line plot data (average solving time)
    line_data = [606.9, 577.5, 508.4, 307.1]
    
    # Set figure size and DPI for high quality output
    fig, ax1 = plt.subplots(figsize=(8, 6), dpi=200)
    
    # Set scientific publication style
    plt.style.use('default')
    plt.rcParams['font.family'] = 'Times New Roman'
    plt.rcParams['font.size'] = 12
    plt.rcParams['axes.linewidth'] = 1.2
    
    # Set up the bar positions
    x = np.arange(len(categories))
    width = 0.6
    
    # Create stacked bars
    bar1 = ax1.bar(x, values1, width, label='best (B=300)', 
                   color='red', alpha=0.8, edgecolor='black', linewidth=1)
    bar2 = ax1.bar(x, values2, width, bottom=values1, label='best (B=200)',
                   color='orange', alpha=0.8, edgecolor='black', linewidth=1)
    
    # Calculate bottom for third series
    bottom2 = np.array(values1) + np.array(values2)
    bar3 = ax1.bar(x, values3, width, bottom=bottom2, label='best (B=100)',
                   color='green', alpha=0.8, edgecolor='black', linewidth=1)
    
    # Customize the first y-axis (for bars)
    ax1.set_xlabel('Models', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Number of Instances', fontsize=14, fontweight='bold')
    ax1.set_title('Performance Comparison: Instance Count and Average Solving Time', 
                  fontsize=16, fontweight='bold', pad=20)
    
    # Set x-axis labels
    ax1.set_xticks(x)
    ax1.set_xticklabels(categories, fontsize=12)
    ax1.tick_params(axis='y', labelsize=11)
    
    # Add grid for bars
    ax1.grid(True, alpha=0.3, linestyle='--', linewidth=0.8, axis='y')
    
    # Set y-axis limit for bars with some margin
    max_height = max(np.array(values1) + np.array(values2) + np.array(values3))
    ax1.set_ylim(0, max_height * 1.1)
    
    # Create second y-axis for line plot
    ax2 = ax1.twinx()
    
    # Create line plot
    line = ax2.plot(x, line_data, color='blue', marker='o', linewidth=3, 
                    markersize=8, label='Atime (All)', 
                    markerfacecolor='blue', markeredgecolor='black', 
                    markeredgewidth=1, alpha=0.9)
    
    # Customize the second y-axis (for line)
    ax2.set_ylim(300, 800)  # 或者根据需要调整上限
    ax2.set_ylabel('Solving Time (s)', fontsize=14, fontweight='bold')
    ax2.tick_params(axis='y', labelsize=11)
    
    # Add value labels on line points
    for i, value in enumerate(line_data):
        ax2.annotate(f'{value}', (i, value), textcoords="offset points", 
                    xytext=(15,0), ha='left', va='center', fontsize=10, 
                    fontweight='bold', color='blue')   
    
    # Add value labels on each bar segment
    for i, (v1, v2, v3) in enumerate(zip(values1, values2, values3)):
        # Label for first segment
        ax1.text(i, v1/2, str(v1), ha='center', va='center', 
                fontweight='bold', fontsize=10, color='white')
        # Label for second segment
        ax1.text(i, v1 + v2/2, str(v2), ha='center', va='center', 
                fontweight='bold', fontsize=10, color='white')
        # Label for third segment
        ax1.text(i, v1 + v2 + v3/2, str(v3), ha='center', va='center', 
                fontweight='bold', fontsize=10, color='white')
    
    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', 
               frameon=True, fancybox=True, shadow=False, 
               fontsize=10, framealpha=0.9)
    
    # Adjust layout
    plt.tight_layout()
    
    # Uncomment to save the figure
    # plt.savefig('combined_chart.png', dpi=300, bbox_inches='tight', 
    #             facecolor='white', edgecolor='none')
    # print("Chart saved as: combined_chart.png")
    
    # Show the plot
    plt.show()

if __name__ == "__main__":
    create_combined_chart()
