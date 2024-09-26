import random
from SyntheticErrandsScheduler.config import MAX_DAYS, WORK_START, WORK_END, SLA_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

def perturbation(schedule, perturbation_strength=0.2):
    """
    Perform perturbation on the current schedule to escape local optima.

    This function randomly applies one of several perturbation strategies:
    1. Random removal and reinsertion
    2. Block relocation
    3. Time window shifting
    4. Priority-based rescheduling

    Args:
        schedule (Schedule): The current schedule to perturb.
        perturbation_strength (float): The fraction of assignments to affect (0.0 to 1.0).

    Returns:
        Schedule: The perturbed schedule.
    """
    perturbation_strategies = [
        random_removal_reinsertion,
        block_relocation,
        time_window_shifting,
        priority_based_rescheduling
    ]
    
    strategy = random.choice(perturbation_strategies)
    return strategy(schedule, perturbation_strength)

def random_removal_reinsertion(schedule, perturbation_strength):
    """Randomly remove a subset of assignments and reinsert them."""
    all_assignments = []
    for day in range(MAX_DAYS):
        all_assignments.extend(schedule.assignments[day])
    
    num_to_remove = int(len(all_assignments) * perturbation_strength)
    assignments_to_remove = random.sample(all_assignments, num_to_remove)

    for assignment in assignments_to_remove:
        day = next(d for d in range(MAX_DAYS) if assignment in schedule.assignments[d])
        schedule.remove_assignment(day, assignment)

    for errand, _, _ in assignments_to_remove:
        schedule.unassigned_errands.add(errand)

    reinsert_unassigned_errands(schedule)

    return schedule

def block_relocation(schedule, perturbation_strength):
    """Relocate a block of assignments to a different day or contractor."""
    days = list(range(MAX_DAYS))
    random.shuffle(days)

    for day in days:
        if len(schedule.assignments[day]) > 1:
            block_size = max(2, int(len(schedule.assignments[day]) * perturbation_strength))
            start_idx = random.randint(0, len(schedule.assignments[day]) - block_size)
            block = schedule.assignments[day][start_idx:start_idx + block_size]

            for assignment in block:
                schedule.remove_assignment(day, assignment)

            new_day = random.choice([d for d in range(MAX_DAYS) if d != day])
            new_contractor = random.choice(schedule.contractors)

            for errand, _, _ in block:
                for start_time in range(WORK_START, WORK_END - errand.service_time + 1):
                    if schedule.assign_errand(new_contractor, errand, new_day, start_time):
                        break
                else:
                    schedule.unassigned_errands.add(errand)

            break

    reinsert_unassigned_errands(schedule)
    return schedule

def time_window_shifting(schedule, perturbation_strength):
    """Shift the start times of assignments within their time windows."""
    for day in range(MAX_DAYS):
        assignments_to_shift = random.sample(schedule.assignments[day], 
                                             int(len(schedule.assignments[day]) * perturbation_strength))
        
        for errand, contractor, start_time in assignments_to_shift:
            if errand.has_time_window():
                schedule.remove_assignment(day, (errand, contractor, start_time))
                
                new_start_time = random.randint(max(errand.start_time, WORK_START),
                                                min(errand.end_time - errand.service_time, WORK_END - errand.service_time))
                
                if not schedule.assign_errand(contractor, errand, day, new_start_time):
                    schedule.unassigned_errands.add(errand)

    reinsert_unassigned_errands(schedule)
    return schedule

def priority_based_rescheduling(schedule, perturbation_strength):
    """Reschedule errands based on their priority and profit potential."""
    all_errands = []
    for day in range(MAX_DAYS):
        for errand, contractor, start_time in schedule.assignments[day]:
            all_errands.append((errand, day, contractor, start_time))
            schedule.remove_assignment(day, (errand, contractor, start_time))

    num_to_reschedule = int(len(all_errands) * perturbation_strength)
    errands_to_reschedule = random.sample(all_errands, num_to_reschedule)

    # Sort errands by priority and profit potential
    errands_to_reschedule.sort(key=lambda x: (x[0].priority, x[0].charge / x[0].service_time), reverse=True)

    for errand, old_day, old_contractor, old_start_time in errands_to_reschedule:
        best_score = float('-inf')
        best_assignment = None

        for day in range(MAX_DAYS):
            for contractor in schedule.contractors:
                for start_time in range(WORK_START, WORK_END - errand.service_time + 1):
                    if schedule.can_assign_errand(contractor, errand, day, start_time):
                        score = calculate_assignment_score(schedule, day, errand, contractor, start_time)
                        if score > best_score:
                            best_score = score
                            best_assignment = (contractor, day, start_time)

        if best_assignment:
            contractor, day, start_time = best_assignment
            schedule.assign_errand(contractor, errand, day, start_time)
        else:
            schedule.unassigned_errands.add(errand)

    # Reassign remaining errands
    for errand, day, contractor, start_time in all_errands:
        if errand not in schedule.unassigned_errands and not schedule.is_errand_assigned(errand):
            if not schedule.assign_errand(contractor, errand, day, start_time):
                schedule.unassigned_errands.add(errand)

    reinsert_unassigned_errands(schedule)
    return schedule

def reinsert_unassigned_errands(schedule):
    """Try to reinsert any unassigned errands back into the schedule."""
    unassigned = list(schedule.unassigned_errands)
    random.shuffle(unassigned)

    for errand in unassigned:
        best_score = float('-inf')
        best_assignment = None

        for day in range(MAX_DAYS):
            for contractor in schedule.contractors:
                current_time = get_resource_end_time(contractor, day)
                travel_time = calculate_travel_time(contractor.current_location, errand.location)
                start_time = current_time + travel_time

                if start_time + travel_time + errand.service_time <= WORK_END:
                    if errand.are_predecessors_completed(schedule.completed_errands):
                        if contractor.can_perform_errand(errand, day, start_time, travel_time):
                            score = calculate_assignment_score(schedule, day, errand, contractor, start_time)
                            if score > best_score:
                                best_score = score
                                best_assignment = (contractor, day, start_time)

        if best_assignment:
            contractor, day, start_time = best_assignment
            if schedule.assign_errand(contractor, errand, day, start_time):
                schedule.unassigned_errands.remove(errand)

def get_resource_end_time(contractor, day):
    if day not in contractor.schedule or not contractor.schedule[day]:
        return WORK_START
    last_errand, last_start_time = contractor.schedule[day][-1]
    return last_start_time + last_errand.service_time

def calculate_assignment_score(schedule, day, errand, contractor, start_time):
    profit = errand.calculate_profit(day, SLA_DAYS)
    early_completion_bonus = max(0, (SLA_DAYS - day) * 0.05 * profit)
    travel_time = calculate_travel_time(contractor.current_location, errand.location)
    
    return profit + early_completion_bonus - travel_time * 0.1

def adaptive_perturbation(schedule, iteration, max_iterations, min_strength=0.3, max_strength=0.7):
    """
    Perform adaptive perturbation on the current schedule.

    This function adjusts the perturbation strength based on the current iteration.
    It maintains a higher perturbation strength throughout the search process to
    increase the likelihood of escaping local optima.

    Args:
        schedule (Schedule): The current schedule to perturb.
        iteration (int): The current iteration number.
        max_iterations (int): The maximum number of iterations.
        min_strength (float): The minimum perturbation strength (increased from 0.1 to 0.3).
        max_strength (float): The maximum perturbation strength (increased from 0.5 to 0.7).

    Returns:
        Schedule: The perturbed schedule.
    """
    # Calculate progress, but use it to maintain a higher strength
    progress = iteration / max_iterations
    strength = max_strength - (max_strength - min_strength) * (progress ** 2)
    return perturbation(schedule, strength)