import matplotlib.pyplot as plt
import numpy as np
from SyntheticErrandsScheduler.utils import visualize_city_map
from SyntheticErrandsScheduler.config import GRID_SIZE, RESIDENTIAL, COMMERCIAL, PARK, INDUSTRIAL

# Define a color map for area types
AREA_COLORS = {
    RESIDENTIAL: '#FFF7BC',
    COMMERCIAL: '#7FCDBB',
    PARK: '#41B6C4',
    INDUSTRIAL: '#1D91C0'
}

def plot_problem(ax, errands, contractors):
    try:
        print("Visualizing city map...")
        visualize_city_map(ax=ax)
        
        print("Plotting errands...")
        for errand in errands:
            print(f"Plotting errand at ({errand.location.x}, {errand.location.y})")
            ax.plot(errand.location.x, errand.location.y, 'ro', markersize=5)
        
        print("Plotting contractors...")
        for contractor in contractors:
            print(f"Plotting contractor at ({contractor.start_location.x}, {contractor.start_location.y})")
            ax.plot(contractor.start_location.x, contractor.start_location.y, 'bo', markersize=7)

        ax.set_title("Problem Visualization")
        
        print("Creating legend elements...")
        legend_elements = [
            plt.Line2D([0], [0], color='r', marker='o', linestyle='', label='Errands'),
            plt.Line2D([0], [0], color='b', marker='o', linestyle='', label='Contractors'),
            plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[RESIDENTIAL], edgecolor='none', label='Residential'),
            plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[COMMERCIAL], edgecolor='none', label='Commercial'),
            plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[PARK], edgecolor='none', label='Park'),
            plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[INDUSTRIAL], edgecolor='none', label='Industrial')
        ]
        
        print("Getting existing legend handles and labels...")
        handles, labels = ax.get_legend_handles_labels()
        legend_elements.extend(handles)
        
        print("Creating combined legend...")
        ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5), fontsize='small')

        print("Adjusting plot layout...")
        plt.tight_layout()
        plt.subplots_adjust(right=0.75, bottom=0.1)
        
        print("Plot problem completed successfully.")
    except Exception as e:
        print(f"Error in plot_problem: {str(e)}")
        raise

def plot_solution(ax, solution):
    visualize_city_map(ax=ax)

    colors = plt.cm.rainbow(np.linspace(0, 1, len(solution.contractors)))

    for day in range(solution.num_days):
        for idx, contractor in enumerate(solution.contractors):
            route = [contractor.start_location] + [errand.location for errand, r, _ in solution.assignments[day] if r.id == contractor.id]
            if len(route) > 1:
                for i in range(len(route) - 1):
                    start = route[i]
                    end = route[i + 1]
                    ax.plot([start.x, end.x], [start.y, end.y], '-', color=colors[idx], alpha=0.5)
                ax.plot(route[0].x, route[0].y, 'bs', markersize=7)  # Start location
                for i in range(1, len(route)):
                    ax.plot(route[i].x, route[i].y, 'ro', markersize=5)  # Errand locations
                    ax.annotate(f"D{day+1}", (route[i].x, route[i].y), xytext=(3, 3), textcoords='offset points', fontsize='x-small')

    # Add legend for start location, errands, contractors, and area types
    legend_elements = [
        plt.Line2D([0], [0], marker='s', color='b', label='Start Location', markersize=7, linestyle=''),
        plt.Line2D([0], [0], marker='o', color='r', label='Errand', markersize=5, linestyle=''),
        plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[RESIDENTIAL], edgecolor='none', label='Residential'),
        plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[COMMERCIAL], edgecolor='none', label='Commercial'),
        plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[PARK], edgecolor='none', label='Park'),
        plt.Rectangle((0, 0), 1, 1, facecolor=AREA_COLORS[INDUSTRIAL], edgecolor='none', label='Industrial')
    ]
    
    for i, contractor in enumerate(solution.contractors):
        legend_elements.append(plt.Line2D([0], [0], color=colors[i], label=f"Contractor {contractor.id}"))
    
    # Get existing legend handles and labels
    handles, labels = ax.get_legend_handles_labels()
    legend_elements.extend(handles)
    
    # Create a combined legend
    ax.legend(handles=legend_elements, loc='center left', bbox_to_anchor=(1, 0.5), fontsize='x-small')

    ax.set_title("Solution Visualization")

    # Adjust the plot layout
    plt.tight_layout()
    plt.subplots_adjust(right=0.75, bottom=0.1)

def create_plot():
    """
    Create and return a new figure and axes for plotting.
    
    Returns:
        tuple: (fig, ax) matplotlib figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=(16, 12))  # Increased figure size
    return fig, ax