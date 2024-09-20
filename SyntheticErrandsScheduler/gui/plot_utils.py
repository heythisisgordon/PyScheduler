import matplotlib.pyplot as plt
import numpy as np
from SyntheticErrandsScheduler.utils import visualize_city_map
from SyntheticErrandsScheduler.config import GRID_SIZE

def plot_problem(ax, errands, contractors):
    """
    Plot the initial problem setup on the given axes.
    
    Args:
        ax (matplotlib.axes.Axes): The axes to plot on.
        errands (list): List of Errand objects.
        contractors (list): List of Contractor objects.
    """
    visualize_city_map(ax=ax)
    
    for errand in errands:
        ax.plot(errand.location.x, errand.location.y, 'ro', markersize=5)
    
    for contractor in contractors:
        ax.plot(contractor.start_location.x, contractor.start_location.y, 'bo', markersize=7)

    ax.set_title("Problem Visualization")

def plot_solution(ax, solution):
    """
    Plot the solution on the given axes.
    
    Args:
        ax (matplotlib.axes.Axes): The axes to plot on.
        solution (Schedule): The solved schedule.
    """
    visualize_city_map(ax=ax)

    colors = plt.cm.rainbow(np.linspace(0, 1, len(solution.contractors)))

    for day in range(solution.num_days):
        for contractor in solution.contractors:
            route = [contractor.start_location] + [errand.location for errand, c, _ in solution.assignments[day] if c.id == contractor.id]
            if len(route) > 1:
                x, y = zip(*[(loc.x, loc.y) for loc in route])
                ax.plot(x, y, '-', color=colors[contractor.id], alpha=0.5)
                ax.plot(x[0], y[0], 'bs', markersize=7)  # Start location
                for i in range(1, len(x)):
                    ax.plot(x[i], y[i], 'ro', markersize=5)  # Errand locations
                    ax.annotate(f"D{day+1}", (x[i], y[i]), xytext=(3, 3), textcoords='offset points')

    ax.set_title("Solution Visualization")

def create_plot():
    """
    Create and return a new figure and axes for plotting.
    
    Returns:
        tuple: (fig, ax) matplotlib figure and axes objects.
    """
    fig, ax = plt.subplots(figsize=(6, 6))
    return fig, ax