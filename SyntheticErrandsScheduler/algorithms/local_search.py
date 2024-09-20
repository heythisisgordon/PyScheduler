import time
import logging
from SyntheticErrandsScheduler.config import MAX_DAYS, WORK_START, WORK_END
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def local_search(schedule, max_time=10):
    """
    Perform local search to improve the current schedule.

    This function uses two main operations:
    1. Swap: Swap the positions of two errands.
    2. Move: Move an errand to a different position or contractor.

    Args:
        schedule (Schedule): The current schedule to improve.
        max_time (float): Maximum time (in seconds) to run the local search.

    Returns:
        Schedule: The improved schedule.
    """
    logger.debug(f"Starting local search with schedule: {schedule}")
    start_time = time.time()
    improved = True
    while improved and time.time() - start_time < max_time:
        improved = False
        
        # Try swapping errands
        logger.debug("Attempting to swap errands")
        improved |= swap_errands(schedule)
        
        # Try moving errands
        logger.debug("Attempting to move errands")
        improved |= move_errands(schedule)

        # Check if time limit is reached
        if time.time() - start_time >= max_time:
            logger.info("Time limit reached in local search.")
            break
    
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
    for day in range(schedule.num_days):
        for i, (errand1, contractor1, start_time1) in enumerate(schedule.assignments[day]):
            for j, (errand2, contractor2, start_time2) in enumerate(schedule.assignments[day][i+1:], start=i+1):
                if try_swap(schedule, day, i, j):
                    return True
    return False

def try_swap(schedule, day, i, j):
    errand1, contractor1, start_time1 = schedule.assignments[day][i]
    errand2, contractor2, start_time2 = schedule.assignments[day][j]

    # Calculate current profit before swapping
    current_profit = (errand1.calculate_profit(day, schedule.num_days) +
                      errand2.calculate_profit(day, schedule.num_days))

    # Try the swap
    schedule.remove_assignment(day, (errand1, contractor1, start_time1))
    schedule.remove_assignment(day, (errand2, contractor2, start_time2))

    if (schedule.assign_errand(contractor2, errand1, day, start_time1) and
        schedule.assign_errand(contractor1, errand2, day, start_time2)):

        # Calculate new profit after swapping
        new_profit = (errand1.calculate_profit(day, schedule.num_days) +
                      errand2.calculate_profit(day, schedule.num_days))

        if new_profit > current_profit:
            return True

    # If swap didn't work or didn't improve, revert
    schedule.remove_assignment(day, (errand1, contractor2, start_time1))
    schedule.remove_assignment(day, (errand2, contractor1, start_time2))
    schedule.assign_errand(contractor1, errand1, day, start_time1)
    schedule.assign_errand(contractor2, errand2, day, start_time2)

    return False