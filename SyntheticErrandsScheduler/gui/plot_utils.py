import matplotlib.pyplot as plt
import numpy as np
from SyntheticErrandsScheduler.utils import visualize_city_map
from SyntheticErrandsScheduler.config import GRID_SIZE

def plot_problem(ax, errands, contractors):
    visualize_city_map(ax=ax)
    
    for errand in errands:
        ax.plot(errand.location.x, errand.location.y, 'ro', markersize=5)
    
    for contractor in contractors:
        ax.plot(contractor.start_location.x, contractor.start_location.y, 'bo', markersize=7)

    ax.set_title("Problem Visualization")
    
    # Add legend
    ax.plot([], [], 'ro', label='Errands')
    ax.plot([], [], 'bo', label='Contractors')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

def plot_solution(ax, solution):
    visualize_city_map(ax=ax)

    colors = plt.cm.rainbow(np.linspace(0, 1, len(solution.contractors)))

    for day in range(solution.num_days):
        for contractor in solution.contractors:
            route = [contractor.start_location] + [errand.location for errand, c, _ in solution.assignments[day] if c.id == contractor.id]
            if len(route) > 1:
                for i in range(len(route) - 1):
                    start = route[i]
                    end = route[i + 1]
                    ax.plot([start.x, start.x, end.x], [start.y, end.y, end.y], '-', color=colors[contractor.id], alpha=0.5)
                ax.plot(route[0].x, route[0].y, 'bs', markersize=7)  # Start location
                for i in range(1, len(route)):
                    ax.plot(route[i].x, route[i].y, 'ro', markersize=5)  # Errand locations
                    ax.annotate(f"D{day+1}", (route[i].x, route[i].y), xytext=(3, 3), textcoords='offset points')

    # Add legend
    ax.plot([], [], 'bs', label='Contractor Start')
    ax.plot([], [], 'ro', label='Errand')
    for i, contractor in enumerate(solution.contractors):
        ax.plot([], [], '-', color=colors[i], label=f'Contractor {contractor.id}')
    ax.legend(loc='upper left', bbox_to_anchor=(1, 1))

    ax.set_title("Solution Visualization")

def create_plot():
    """
    Create and return a new figure and axes for plotting.
    
    Returns:
        tuple: (fig, ax) matplotlib figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    return fig, ax