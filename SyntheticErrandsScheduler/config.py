import numpy as np

# City and Grid Configuration
GRID_SIZE = 100
SPEED = 65  # km/h, updated to 65 km/h as requested

# Work Hours
WORK_START = 8 * 60  # 8:00 AM in minutes
WORK_END = 17 * 60   # 5:00 PM in minutes

# Scheduling
MAX_DAYS = 14  # 2-week period
MAX_SOLVE_TIME = 300  # Maximum time (in seconds) for the solver to run

# Area Types
RESIDENTIAL = 0
COMMERCIAL = 1
PARK = 2
INDUSTRIAL = 3

# Errand Types and Details
ERRANDS = {
    'Delivery': {
        'charge': 10, 
        'time': 30, 
        'home_required': False, 
        'early_incentive': 5, 
        'late_penalty': 0.25,
        'priority': 1,
        'tools_required': [],
        'parts_required': []
    },
    'Dog Walk': {
        'charge': 50, 
        'time': 60, 
        'home_required': True, 
        'early_incentive': 3, 
        'late_penalty': 0.5,
        'priority': 2,
        'tools_required': [],
        'parts_required': []
    },
    'Detail Car': {
        'charge': 100, 
        'time': 90, 
        'home_required': True, 
        'early_incentive': 2.5, 
        'late_penalty': 0.1,
        'priority': 3,
        'tools_required': [],
        'parts_required': []
    },
    'Cut Grass': {
        'charge': 80, 
        'time': 120, 
        'home_required': False, 
        'early_incentive': 2, 
        'late_penalty': 0.5,
        'priority': 2,
        'tools_required': [],
        'parts_required': []
    },
    'Outing': {
        'charge': 300, 
        'time': 240, 
        'home_required': True, 
        'early_incentive': 3, 
        'late_penalty': 0.1,
        'priority': 4,
        'tools_required': [],
        'parts_required': []
    },
    'Moving': {
        'charge': 5000, 
        'time': 360,  # Changed to 6 hours (360 minutes) as requested
        'home_required': True, 
        'early_incentive': 2, 
        'late_penalty': 0.9,
        'priority': 5,
        'tools_required': [],
        'parts_required': []
    },
}

# Priority Levels
PRIORITY_LEVELS = {
    1: "Low",
    2: "Medium-Low",
    3: "Medium",
    4: "Medium-High",
    5: "High"
}

# Tools and Spare Parts
TOOLS = ['Leash', 'Treats', 'Car Cleaning Kit', 'Lawnmower', 'Trimmer', 'Moving Dolly', 'Furniture Pads']
SPARE_PARTS = ['Cleaning Solution', 'Grass Bag', 'Packing Boxes']

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

# Traffic Factors (1.0 means normal speed, higher values mean slower traffic)
TRAFFIC_FACTORS = {
    'morning_rush': 1.5,
    'evening_rush': 1.5,
    'normal': 1.0,
    'night': 0.8
}

# Algorithm Configuration
MILS_ITERATIONS = 1000  # Number of iterations for Modified Iterated Local Search
PERTURBATION_STRENGTH = 0.2  # Initial perturbation strength
COOLING_RATE = 0.995  # Cooling rate for simulated annealing-like acceptance

# SLA Configuration
SLA_DAYS = 14  # Number of days within which all errands must be completed

# Depot Configuration
DEPOT_LOCATIONS = [
    (10, 10),  # Downtown depot
    (80, 80),  # Industrial area depot
]

# Visualization Configuration
ERRAND_COLORS = {
    'Delivery': 'red',
    'Dog Walk': 'blue',
    'Detail Car': 'green',
    'Cut Grass': 'yellow',
    'Outing': 'purple',
    'Moving': 'orange'
}