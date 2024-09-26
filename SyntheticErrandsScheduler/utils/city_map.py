import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch
from SyntheticErrandsScheduler.config import GRID_SIZE, BUSYVILLE_MAP, ROAD_NETWORK, RESIDENTIAL, COMMERCIAL, PARK, INDUSTRIAL, ERRAND_COLORS

def visualize_city_map(ax=None, show_roads=True):
    """
    Visualize the Busyville map with different area types and optionally show roads.

    Args:
        ax (matplotlib.axes.Axes, optional): The axes to plot on. If None, a new figure is created.
        show_roads (bool): If True, overlay the road network on the map.

    Returns:
        matplotlib.figure.Figure: The figure object containing the visualized map.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 10))
    else:
        fig = ax.figure

    # Create a custom colormap for the different area types
    colors = ['#FFF7BC', '#7FCDBB', '#41B6C4', '#1D91C0']
    cmap = ListedColormap(colors)
    bounds = [RESIDENTIAL - 0.5, RESIDENTIAL + 0.5, COMMERCIAL + 0.5, PARK + 0.5, INDUSTRIAL + 0.5]
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

    # Plot the city map
    im = ax.imshow(BUSYVILLE_MAP, cmap=cmap, norm=norm)

    # Create legend patches
    legend_elements = [
        Patch(facecolor=colors[0], edgecolor='black', label='Residential'),
        Patch(facecolor=colors[1], edgecolor='black', label='Commercial'),
        Patch(facecolor=colors[2], edgecolor='black', label='Park'),
        Patch(facecolor=colors[3], edgecolor='black', label='Industrial')
    ]

    # Add the legend
    legend = ax.legend(handles=legend_elements, loc='lower right', title="Map Legend", 
                       fontsize='medium', title_fontsize='large', bbox_to_anchor=(0.98, 0.02),
                       bbox_transform=ax.transAxes, frameon=True, fancybox=True, shadow=True)

    # Overlay the road network if requested
    if show_roads:
        road_y, road_x = np.where(ROAD_NETWORK)
        ax.scatter(road_x, road_y, color='gray', s=1, alpha=0.5)

    ax.set_title('Busyville Map')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')

    # Adjust the plot layout to accommodate the legend
    plt.tight_layout()
    plt.subplots_adjust(right=0.9, bottom=0.1)

    return fig

def plot_route(route, ax=None, color='red', alpha=0.7, linewidth=2, show_direction=True):
    """
    Plot a route on the city map.

    Args:
        route (list): List of Location objects representing the route.
        ax (matplotlib.axes.Axes, optional): The axes to plot on. If None, a new figure is created.
        color (str): Color of the route line.
        alpha (float): Transparency of the route line.
        linewidth (float): Width of the route line.
        show_direction (bool): If True, show arrowheads indicating direction.

    Returns:
        matplotlib.figure.Figure: The figure object containing the plotted route.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 10))
        visualize_city_map(ax=ax, show_roads=True)
    else:
        fig = ax.figure

    x_coords, y_coords = zip(*[(loc.x, loc.y) for loc in route])
    
    if show_direction:
        for i in range(len(x_coords) - 1):
            ax.annotate('', xy=(x_coords[i+1], y_coords[i+1]), xytext=(x_coords[i], y_coords[i]),
                        arrowprops=dict(arrowstyle='->', color=color, alpha=alpha, linewidth=linewidth))
    else:
        ax.plot(x_coords, y_coords, color=color, alpha=alpha, linewidth=linewidth)
    
    # Annotate start and end
    ax.annotate('Start', (x_coords[0], y_coords[0]), xytext=(5, 5), textcoords='offset points')
    ax.annotate('End', (x_coords[-1], y_coords[-1]), xytext=(5, 5), textcoords='offset points')

    return fig

def get_area_type(location):
    """
    Get the area type for a given location.

    Args:
        location (Location): The location to check.

    Returns:
        int: The area type (RESIDENTIAL, COMMERCIAL, PARK, or INDUSTRIAL).
    """
    return BUSYVILLE_MAP[location.y, location.x]

def is_valid_location(x, y):
    """
    Check if a given (x, y) coordinate is a valid location on the map.

    Args:
        x (int): The x-coordinate.
        y (int): The y-coordinate.

    Returns:
        bool: True if the location is valid, False otherwise.
    """
    return 0 <= x < GRID_SIZE and 0 <= y < GRID_SIZE

def is_on_road(location):
    """
    Check if a given location is on a road.

    Args:
        location (Location): The location to check.

    Returns:
        bool: True if the location is on a road, False otherwise.
    """
    return ROAD_NETWORK[location.y, location.x]

def find_nearest_road(location):
    """
    Find the nearest road to a given location.

    Args:
        location (Location): The location to start from.

    Returns:
        tuple: (x, y) coordinates of the nearest road location.
    """
    x, y = location.x, location.y
    
    if is_on_road(location):
        return (x, y)

    for d in range(1, GRID_SIZE):
        for dx, dy in [(0, d), (d, 0), (0, -d), (-d, 0)]:
            nx, ny = x + dx, y + dy
            if is_valid_location(nx, ny) and ROAD_NETWORK[ny, nx]:
                return (nx, ny)

    # If we get here, there's no road on the map (shouldn't happen in a normal city map)
    raise ValueError("No road found on the map")

def plot_schedule(schedule, day, ax=None):
    """
    Plot the schedule for a specific day on the city map.

    Args:
        schedule (Schedule): The schedule to plot.
        day (int): The day to plot.
        ax (matplotlib.axes.Axes, optional): The axes to plot on. If None, a new figure is created.

    Returns:
        matplotlib.figure.Figure: The figure object containing the plotted schedule.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(12, 10))
        visualize_city_map(ax=ax, show_roads=True)
    else:
        fig = ax.figure

    for errand, contractor, start_time in schedule.assignments[day]:
        color = ERRAND_COLORS.get(errand.type, 'black')
        plot_route([contractor.current_location, errand.location], ax=ax, color=color)
        
        ax.plot(errand.location.x, errand.location.y, 'o', color=color, markersize=8)
        ax.annotate(f"E{errand.id}", (errand.location.x, errand.location.y), xytext=(5, 5), textcoords='offset points')

    ax.set_title(f'Schedule for Day {day + 1}')
    
    # Create a legend for errand types
    legend_elements = [plt.Line2D([0], [0], marker='o', color='w', label=errand_type,
                                  markerfacecolor=color, markersize=8)
                       for errand_type, color in ERRAND_COLORS.items()]
    ax.legend(handles=legend_elements, title="Errand Types", loc='upper left', bbox_to_anchor=(1, 1), fontsize='small')

    # Adjust the plot layout to accommodate the legends
    plt.tight_layout()
    plt.subplots_adjust(right=0.85)

    return fig