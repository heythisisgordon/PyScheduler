import random
from SyntheticErrandsScheduler.config import WORK_START, WORK_END, MAX_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

def generate_initial_solution(schedule):
    """
    Generate an initial solution for the scheduling problem.

    This function uses a simple greedy approach to assign errands to contractors.
    It goes through each day, each contractor, and tries to assign as many errands
    as possible while respecting time constraints.

    Args:
        schedule (Schedule): The schedule object to populate with initial assignments.

    Returns:
        Schedule: The schedule object with initial assignments.
    """
    for day in range(MAX_DAYS):
        for contractor in schedule.contractors:
            contractor.reset_day()
            current_time = WORK_START
            
            # Create a list of unassigned errands and shuffle it
            available_errands = list(schedule.unassigned_errands)
            random.shuffle(available_errands)
            
            for errand in available_errands:
                travel_time = calculate_travel_time(contractor.current_location, errand.location)
                arrival_time = current_time + travel_time
                
                if arrival_time + errand.service_time <= WORK_END:
                    if schedule.assign_errand(contractor, errand, day, current_time):
                        current_time = arrival_time + errand.service_time
                    
                    # If all errands are assigned, we're done
                    if not schedule.unassigned_errands:
                        return schedule
    
    return schedule