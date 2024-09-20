import logging
from SyntheticErrandsScheduler.config import MAX_DAYS, WORK_START, WORK_END
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def local_search(schedule):
    """
    Perform local search to improve the current schedule.

    This function uses two main operations:
    1. Swap: Swap the positions of two errands.
    2. Move: Move an errand to a different position or contractor.

    Args:
        schedule (Schedule): The current schedule to improve.

    Returns:
        Schedule: The improved schedule.
    """
    logger.debug(f"Starting local search with schedule: {schedule}")
    improved = True
    while improved:
        improved = False
        
        # Try swapping errands
        logger.debug("Attempting to swap errands")
        improved |= swap_errands(schedule)
        
        # Try moving errands
        logger.debug("Attempting to move errands")
        improved |= move_errands(schedule)
    
    logger.debug(f"Local search completed. Final schedule: {schedule}")
    return schedule

def swap_errands(schedule):
    """
    Attempt to improve the schedule by swapping pairs of errands.

    Args:
        schedule (Schedule): The current schedule.

    Returns:
        bool: True if an improvement was made, False otherwise.
    """
    logger.debug(f"Entering swap_errands function")
    for day in range(MAX_DAYS):
        logger.debug(f"Checking day {day}")
        if day >= len(schedule.assignments):
            logger.warning(f"Day {day} is out of range for schedule assignments")
            continue
        for i, (errand1, contractor1, start_time1) in enumerate(schedule.assignments[day]):
            logger.debug(f"Checking errand {errand1} at position {i}")
            for j, (errand2, contractor2, start_time2) in enumerate(schedule.assignments[day][i+1:], start=i+1):
                logger.debug(f"Trying to swap with errand {errand2} at position {j}")
                if try_swap(schedule, day, i, j):
                    logger.debug(f"Successful swap between errands at positions {i} and {j}")
                    return True
    logger.debug("No successful swaps found")
    return False

def move_errands(schedule):
    """
    Attempt to improve the schedule by moving errands to different positions or contractors.

    Args:
        schedule (Schedule): The current schedule.

    Returns:
        bool: True if an improvement was made, False otherwise.
    """
    logger.debug(f"Entering move_errands function")
    for day in range(MAX_DAYS):
        logger.debug(f"Checking day {day}")
        if day >= len(schedule.assignments):
            logger.warning(f"Day {day} is out of range for schedule assignments")
            continue
        for i, (errand, _, _) in enumerate(schedule.assignments[day]):
            logger.debug(f"Checking errand {errand} at position {i}")
            for contractor in schedule.contractors:
                logger.debug(f"Trying to move to contractor {contractor}")
                for new_position in range(len(schedule.assignments[day]) + 1):
                    logger.debug(f"Trying to move to position {new_position}")
                    if try_move(schedule, day, i, contractor, new_position):
                        logger.debug(f"Successful move of errand from position {i} to {new_position} with contractor {contractor}")
                        return True
    logger.debug("No successful moves found")
    return False

def try_swap(schedule, day, i, j):
    """
    Try to swap two errands and check if it improves the schedule.

    Args:
        schedule (Schedule): The current schedule.
        day (int): The day of the errands.
        i (int): The index of the first errand.
        j (int): The index of the second errand.

    Returns:
        bool: True if the swap improved the schedule, False otherwise.
    """
    logger.debug(f"Attempting to swap errands at positions {i} and {j} on day {day}")
    errand1, contractor1, _ = schedule.assignments[day][i]
    errand2, contractor2, _ = schedule.assignments[day][j]
    
    # Calculate current profit
    current_profit = (errand1.calculate_profit(day, MAX_DAYS) +
                      errand2.calculate_profit(day, MAX_DAYS))
    
    # Try the swap
    schedule.remove_assignment(day, schedule.assignments[day][i])
    schedule.remove_assignment(day, schedule.assignments[day][j-1])  # j-1 because i was already removed
    
    new_start_time1 = calculate_new_start_time(schedule, day, contractor2, i, errand1)
    new_start_time2 = calculate_new_start_time(schedule, day, contractor1, j, errand2)
    
    if (new_start_time1 is not None and new_start_time2 is not None and
        schedule.assign_errand(contractor2, errand1, day, new_start_time1) and
        schedule.assign_errand(contractor1, errand2, day, new_start_time2)):
        
        # Calculate new profit
        new_profit = (errand1.calculate_profit(day, MAX_DAYS) +
                      errand2.calculate_profit(day, MAX_DAYS))
        
        if new_profit > current_profit:
            logger.debug(f"Swap successful. Profit improved from {current_profit} to {new_profit}")
            return True
    
    # If swap didn't work or didn't improve, revert
    schedule.remove_assignment(day, (errand1, contractor2, new_start_time1))
    schedule.remove_assignment(day, (errand2, contractor1, new_start_time2))
    schedule.assign_errand(contractor1, errand1, day, schedule.assignments[day][i][2])
    schedule.assign_errand(contractor2, errand2, day, schedule.assignments[day][j][2])
    
    logger.debug("Swap unsuccessful")
    return False

def try_move(schedule, day, i, new_contractor, new_position):
    """
    Try to move an errand to a new position and/or contractor and check if it improves the schedule.

    Args:
        schedule (Schedule): The current schedule.
        day (int): The day of the errand.
        i (int): The current index of the errand.
        new_contractor (Contractor): The contractor to move the errand to.
        new_position (int): The new position to move the errand to.

    Returns:
        bool: True if the move improved the schedule, False otherwise.
    """
    logger.debug(f"Attempting to move errand at position {i} to position {new_position} with contractor {new_contractor} on day {day}")
    errand, old_contractor, old_start_time = schedule.assignments[day][i]
    
    # Calculate current profit
    current_profit = errand.calculate_profit(day, MAX_DAYS)
    
    # Try the move
    schedule.remove_assignment(day, schedule.assignments[day][i])
    
    new_start_time = calculate_new_start_time(schedule, day, new_contractor, new_position, errand)
    
    if new_start_time is not None and schedule.assign_errand(new_contractor, errand, day, new_start_time):
        # Calculate new profit
        new_profit = errand.calculate_profit(day, MAX_DAYS)
        
        if new_profit > current_profit:
            logger.debug(f"Move successful. Profit improved from {current_profit} to {new_profit}")
            return True
    
    # If move didn't work or didn't improve, revert
    schedule.remove_assignment(day, (errand, new_contractor, new_start_time))
    schedule.assign_errand(old_contractor, errand, day, old_start_time)
    
    logger.debug("Move unsuccessful")
    return False

def calculate_new_start_time(schedule, day, contractor, position, errand):
    """
    Calculate the new start time for an errand in a given position.

    Args:
        schedule (Schedule): The current schedule.
        day (int): The day of the errand.
        contractor (Contractor): The contractor for the errand.
        position (int): The position to insert the errand.
        errand (Errand): The errand to insert.

    Returns:
        int or None: The new start time if possible, None if not possible.
    """
    logger.debug(f"Calculating new start time for errand {errand} at position {position} on day {day}")
    if position == 0:
        prev_location = contractor.start_location
        start_time = WORK_START
    else:
        prev_errand, _, prev_start_time = schedule.assignments[day][position-1]
        prev_location = prev_errand.location
        start_time = prev_start_time + prev_errand.service_time
    
    travel_time = calculate_travel_time(prev_location, errand.location)
    start_time += travel_time
    
    if start_time + errand.service_time > WORK_END:
        logger.debug(f"New start time {start_time} is not possible as it exceeds work end time {WORK_END}")
        return None
    
    logger.debug(f"New start time calculated: {start_time}")
    return start_time