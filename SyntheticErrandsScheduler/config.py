import numpy as np

# City and Grid Configuration
GRID_SIZE = 100
SPEED = 30  # km/h

# Work Hours
WORK_START = 8 * 60  # 8:00 AM in minutes
WORK_END = 17 * 60   # 5:00 PM in minutes

# Scheduling
MAX_DAYS = 10  # 2-week period
MAX_SOLVE_TIME = 60  # Maximum time (in seconds) for the solver to run

# Area Types
RESIDENTIAL = 0
COMMERCIAL = 1
PARK = 2
INDUSTRIAL = 3

# Errand Types and Details
ERRANDS = {
    'Delivery': {'charge': 10, 'time': 30, 'home_required': False, 'early_incentive': 5, 'late_penalty': 0.25},
    'Dog Walk': {'charge': 50, 'time': 60, 'home_required': True, 'early_incentive': 3, 'late_penalty': 0},
    'Detail Car': {'charge': 100, 'time': 90, 'home_required': True, 'early_incentive': 2.5, 'late_penalty': 0.1},
    'Cut Grass': {'charge': 80, 'time': 120, 'home_required': False, 'early_incentive': 2, 'late_penalty': 0},
    'Outing': {'charge': 300, 'time': 240, 'home_required': True, 'early_incentive': 3, 'late_penalty': 0.1},
    'Moving': {'charge': 5000, 'time': 480, 'home_required': True, 'early_incentive': 2, 'late_penalty': 300},
}

# City Map Configuration
def create_busyville_map(size=GRID_SIZE):
    map = np.zeros((size, size), dtype=int)
    
    # Create areas
    map[10:30, 10:30] = COMMERCIAL  # Downtown
    map[60:90, 60:90] = INDUSTRIAL  # Industrial area
    map[10:40, 60:90] = RESIDENTIAL # Residential area 1
    map[60:90, 10:40] = RESIDENTIAL # Residential area 2
    map[40:60, 40:60] = PARK        # Central park
    
    return map

BUSYVILLE_MAP = create_busyville_map()

# Road Network Configuration
def create_road_network(city_map):
    size = city_map.shape[0]
    roads = np.zeros((size, size), dtype=bool)
    
    # Main roads
    roads[::10, :] = True
    roads[:, ::10] = True
    
    # Secondary roads in residential and commercial areas
    for i in range(size):
        for j in range(size):
            if city_map[i, j] in [RESIDENTIAL, COMMERCIAL]:
                if i % 5 == 0 or j % 5 == 0:
                    roads[i, j] = True
    
    return roads

ROAD_NETWORK = create_road_network(BUSYVILLE_MAP)

# Algorithm Configuration
MILS_ITERATIONS = 1000  # Number of iterations for Modified Iterated Local Search