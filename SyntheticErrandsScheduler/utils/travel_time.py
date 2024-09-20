import math
from SyntheticErrandsScheduler.config import GRID_SIZE, SPEED, ROAD_NETWORK

def calculate_travel_time(start_location, end_location):
    """
    Calculate the travel time between two locations using A* pathfinding algorithm.

    Args:
        start_location (Location): The starting location.
        end_location (Location): The ending location.

    Returns:
        float: The travel time in minutes.
    """
    def heuristic(a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def get_neighbors(node):
        x, y = node
        neighbors = []
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < GRID_SIZE and 0 <= ny < GRID_SIZE and ROAD_NETWORK[ny, nx]:
                neighbors.append((nx, ny))
        return neighbors

    start = (start_location.x, start_location.y)
    goal = (end_location.x, end_location.y)

    open_set = {start}
    came_from = {}
    g_score = {start: 0}
    f_score = {start: heuristic(start, goal)}

    while open_set:
        current = min(open_set, key=lambda x: f_score[x])

        if current == goal:
            path = []
            while current in came_from:
                path.append(current)
                current = came_from[current]
            path.append(start)
            path.reverse()
            return len(path) / SPEED * 60  # Convert to minutes

        open_set.remove(current)

        for neighbor in get_neighbors(current):
            tentative_g_score = g_score[current] + 1

            if neighbor not in g_score or tentative_g_score < g_score[neighbor]:
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g_score
                f_score[neighbor] = g_score[neighbor] + heuristic(neighbor, goal)
                if neighbor not in open_set:
                    open_set.add(neighbor)

    # If we get here, there's no path
    return float('inf')

def manhattan_distance(start_location, end_location):
    """
    Calculate the Manhattan distance between two locations.

    Args:
        start_location (Location): The starting location.
        end_location (Location): The ending location.

    Returns:
        int: The Manhattan distance between the two locations.
    """
    return abs(start_location.x - end_location.x) + abs(start_location.y - end_location.y)

def euclidean_distance(start_location, end_location):
    """
    Calculate the Euclidean distance between two locations.

    Args:
        start_location (Location): The starting location.
        end_location (Location): The ending location.

    Returns:
        float: The Euclidean distance between the two locations.
    """
    return math.sqrt((start_location.x - end_location.x)**2 + (start_location.y - end_location.y)**2)

def estimate_travel_time(start_location, end_location):
    """
    Estimate travel time between two locations using Manhattan distance.
    This is faster than A* but less accurate, useful for quick estimates.

    Args:
        start_location (Location): The starting location.
        end_location (Location): The ending location.

    Returns:
        float: The estimated travel time in minutes.
    """
    distance = manhattan_distance(start_location, end_location)
    return distance / SPEED * 60  # Convert to minutes