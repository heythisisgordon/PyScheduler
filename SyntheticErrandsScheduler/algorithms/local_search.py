import time
import random
import logging
from SyntheticErrandsScheduler.config import MAX_DAYS, WORK_START, WORK_END, SLA_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def local_search(schedule, max_time=10):
    logger.debug(f"Starting optimized local search with schedule: {schedule}")
    start_time = time.time()
    improved = True

    while improved and time.time() - start_time < max_time:
        improved = False
        
        improved |= optimize_errand_timing(schedule)
        improved |= swap_errands(schedule)
        improved |= relocate_errand(schedule)

        if time.time() - start_time >= max_time:
            logger.info("Time limit reached in optimized local search.")
            break
    
    logger.debug(f"Optimized local search completed. Final schedule: {schedule}")
    return schedule

def optimize_errand_timing(schedule):
    """Optimize the timing of errands to maximize early completion bonuses."""
    improved = False
    for day in range(schedule.num_days):
        assignments = schedule.assignments[day]
        for i, (errand, contractor, start_time) in enumerate(assignments):
            earliest_start = max(WORK_START, int(start_time - 60))  # Try up to 1 hour earlier
            latest_start = min(WORK_END - errand.service_time, int(start_time + 60))  # Try up to 1 hour later
            
            best_start = start_time
            best_score = calculate_assignment_score(schedule, day, errand, contractor, start_time)
            
            for new_start in range(earliest_start, latest_start + 1, 15):  # Check every 15 minutes
                if new_start != start_time:
                    new_score = calculate_assignment_score(schedule, day, errand, contractor, new_start)
                    if new_score > best_score:
                        best_start = new_start
                        best_score = new_score
            
            if best_start != start_time:
                schedule.remove_assignment(day, (errand, contractor, start_time))
                schedule.assign_errand(contractor, errand, day, best_start)
                improved = True
    
    return improved

def swap_errands(schedule):
    """Attempt to improve the schedule by swapping pairs of errands."""
    improved = False
    for day in range(schedule.num_days):
        assignments = schedule.assignments[day]
        for i in range(len(assignments)):
            for j in range(i + 1, len(assignments)):
                if try_swap(schedule, day, i, j):
                    improved = True
    
    # Try swapping errands between days
    for day1 in range(schedule.num_days):
        for day2 in range(day1 + 1, schedule.num_days):
            if try_swap_between_days(schedule, day1, day2):
                improved = True
    
    return improved

def try_swap(schedule, day, i, j):
    assignments = schedule.assignments[day]
    if i >= len(assignments) or j >= len(assignments):
        return False

    errand1, contractor1, start_time1 = assignments[i]
    errand2, contractor2, start_time2 = assignments[j]

    if not (errand1.are_predecessors_completed(schedule.completed_errands - {errand2}) and
            errand2.are_predecessors_completed(schedule.completed_errands - {errand1})):
        return False

    current_score = (calculate_assignment_score(schedule, day, errand1, contractor1, start_time1) +
                     calculate_assignment_score(schedule, day, errand2, contractor2, start_time2))

    travel_time1 = calculate_travel_time(contractor2.current_location, errand1.location)
    travel_time2 = calculate_travel_time(contractor1.current_location, errand2.location)

    # Check if the swap is valid before making any changes
    if (schedule.can_assign_errand(contractor2, errand1, day, start_time1 + travel_time1) and
        schedule.can_assign_errand(contractor1, errand2, day, start_time2 + travel_time2)):

        # Now it's safe to remove and reassign
        schedule.remove_assignment(day, (errand1, contractor1, start_time1))
        schedule.remove_assignment(day, (errand2, contractor2, start_time2))

        schedule.assign_errand(contractor2, errand1, day, start_time1 + travel_time1)
        schedule.assign_errand(contractor1, errand2, day, start_time2 + travel_time2)

        new_score = (calculate_assignment_score(schedule, day, errand1, contractor2, start_time1 + travel_time1) +
                     calculate_assignment_score(schedule, day, errand2, contractor1, start_time2 + travel_time2))

        if new_score > current_score:
            return True
        else:
            # Swap back if no improvement
            schedule.remove_assignment(day, (errand1, contractor2, start_time1 + travel_time1))
            schedule.remove_assignment(day, (errand2, contractor1, start_time2 + travel_time2))
            schedule.assign_errand(contractor1, errand1, day, start_time1)
            schedule.assign_errand(contractor2, errand2, day, start_time2)

    return False

def try_swap_between_days(schedule, day1, day2):
    if not schedule.assignments[day1] or not schedule.assignments[day2]:
        return False

    errand1, contractor1, start_time1 = schedule.assignments[day1][0]
    errand2, contractor2, start_time2 = schedule.assignments[day2][0]

    current_score = (calculate_assignment_score(schedule, day1, errand1, contractor1, start_time1) +
                     calculate_assignment_score(schedule, day2, errand2, contractor2, start_time2))

    if (schedule.can_assign_errand(contractor2, errand1, day2, start_time2) and
        schedule.can_assign_errand(contractor1, errand2, day1, start_time1)):

        schedule.remove_assignment(day1, (errand1, contractor1, start_time1))
        schedule.remove_assignment(day2, (errand2, contractor2, start_time2))

        schedule.assign_errand(contractor2, errand1, day2, start_time2)
        schedule.assign_errand(contractor1, errand2, day1, start_time1)

        new_score = (calculate_assignment_score(schedule, day2, errand1, contractor2, start_time2) +
                     calculate_assignment_score(schedule, day1, errand2, contractor1, start_time1))

        if new_score > current_score:
            return True
        else:
            # Swap back if no improvement
            schedule.remove_assignment(day2, (errand1, contractor2, start_time2))
            schedule.remove_assignment(day1, (errand2, contractor1, start_time1))
            schedule.assign_errand(contractor1, errand1, day1, start_time1)
            schedule.assign_errand(contractor2, errand2, day2, start_time2)

    return False

def relocate_errand(schedule):
    """Attempt to improve the schedule by moving an errand to a different position or contractor."""
    improved = False
    for day in range(schedule.num_days):
        assignments = schedule.assignments[day]
        for i, (errand, contractor, start_time) in enumerate(assignments):
            for new_day in range(schedule.num_days):
                if new_day != day:
                    if try_relocate(schedule, day, new_day, i):
                        improved = True
                        break
            
            if not improved:
                for new_contractor in schedule.contractors:
                    if new_contractor != contractor:
                        if try_relocate(schedule, day, day, i, new_contractor):
                            improved = True
                            break
            
            if improved:
                break
        if improved:
            break
    return improved

def try_relocate(schedule, old_day, new_day, index, new_contractor=None):
    assignments = schedule.assignments[old_day]
    errand, old_contractor, old_start_time = assignments[index]

    if not errand.are_predecessors_completed(schedule.completed_errands - {errand}):
        return False

    schedule.remove_assignment(old_day, (errand, old_contractor, old_start_time))

    new_contractor = new_contractor or old_contractor
    best_start_time = None
    best_score = float('-inf')

    for new_start_time in range(WORK_START, WORK_END - errand.service_time + 1, 15):  # Check every 15 minutes
        if schedule.can_assign_errand(new_contractor, errand, new_day, new_start_time):
            score = calculate_assignment_score(schedule, new_day, errand, new_contractor, new_start_time)
            if score > best_score:
                best_score = score
                best_start_time = new_start_time

    if best_start_time is not None:
        if schedule.assign_errand(new_contractor, errand, new_day, best_start_time):
            return True

    schedule.assign_errand(old_contractor, errand, old_day, old_start_time)
    return False

def calculate_assignment_score(schedule, day, errand, contractor, start_time):
    profit = errand.calculate_profit(day, SLA_DAYS)
    early_completion_bonus = max(0, (SLA_DAYS - day) * 0.1 * profit)  # Increased bonus for earlier completion
    travel_time = calculate_travel_time(contractor.current_location, errand.location)
    
    return profit + early_completion_bonus - travel_time * 0.05  # Reduced travel time penalty