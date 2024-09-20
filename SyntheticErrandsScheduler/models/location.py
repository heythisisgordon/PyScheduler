import math
from SyntheticErrandsScheduler.config import GRID_SIZE, ROAD_NETWORK

class Location:
    def __init__(self, x, y):
        self.x, self.y = self.snap_to_road(x, y)
    
    def snap_to_road(self, x, y):
        """
        Snaps the given coordinates to the nearest road.
        """
        x, y = round(x), round(y)
        if ROAD_NETWORK[y, x]:
            return x, y
        
        # Find the nearest road
        nearest_x, nearest_y = x, y
        min_distance = float('inf')
        for i in range(max(0, y-5), min(GRID_SIZE, y+6)):
            for j in range(max(0, x-5), min(GRID_SIZE, x+6)):
                if ROAD_NETWORK[i, j]:
                    distance = abs(x-j) + abs(y-i)
                    if distance < min_distance:
                        min_distance = distance
                        nearest_x, nearest_y = j, i
        
        return nearest_x, nearest_y

    def distance_to(self, other):
        """
        Calculates the Manhattan distance to another location.
        """
        return abs(self.x - other.x) + abs(self.y - other.y)

    def euclidean_distance_to(self, other):
        """
        Calculates the Euclidean distance to another location.
        """
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

    def __eq__(self, other):
        if not isinstance(other, Location):
            return False
        return self.x == other.x and self.y == other.y

    def __hash__(self):
        return hash((self.x, self.y))

    def __str__(self):
        return f"Location({self.x}, {self.y})"

    def __repr__(self):
        return self.__str__()