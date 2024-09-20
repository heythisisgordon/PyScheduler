import numpy as np
import matplotlib.pyplot as plt
from SyntheticErrandsScheduler.config import GRID_SIZE, BUSYVILLE_MAP, ROAD_NETWORK, RESIDENTIAL, COMMERCIAL, PARK, INDUSTRIAL

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
        fig, ax = plt.subplots(figsize=(10, 10))
    else:
        fig = ax.figure

    # Create a custom colormap for the different area types
    cmap = plt.cm.colors.ListedColormap(['#FFF7BC', '#7FCDBB', '#41B6C4', '#1D91C0'])
    bounds = [RESIDENTIAL - 0.5, RESIDENTIAL + 0.5, COMMERCIAL + 0.5, PARK + 0.5, INDUSTRIAL + 0.5]
    norm = plt.cm.colors.BoundaryNorm(bounds, cmap.N)

    # Plot the city map
    im = ax.imshow(BUSYVILLE_MAP, cmap=cmap, norm=norm)

    # Add a color bar
    cbar = plt.colorbar(im, ax=ax, ticks=[RESIDENTIAL, COMMERCIAL, PARK, INDUSTRIAL])
    cbar.set_ticklabels(['Residential', 'Commercial', 'Park', 'Industrial'])

    # Overlay the road network if requested
    if show_roads:
        road_y, road_x = np.where(ROAD_NETWORK)
        ax.scatter(road_x, road_y, color='gray', s=1, alpha=0.5)

    ax.set_title('Busyville Map')
    ax.set_xlabel('X coordinate')
    ax.set_ylabel('Y coordinate')

    return fig

def plot_route(route, ax=None):
    """
    Plot a route on the city map.

    Args:
        route (list): List of Location objects representing the route.
        ax (matplotlib.axes.Axes, optional): The axes to plot on. If None, a new figure is created.

    Returns:
        matplotlib.figure.Figure: The figure object containing the plotted route.
    """
    if ax is None:
        fig, ax = plt.subplots(figsize=(10, 10))
        visualize_city_map(show_roads=True)
    else:
        fig = ax.figure

    x_coords, y_coords = zip(*[(loc.x, loc.y) for loc in route])
    ax.plot(x_coords, y_coords, 'ro-', linewidth=2, markersize=8, alpha=0.7)
    
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