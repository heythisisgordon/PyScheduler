import random
from SyntheticErrandsScheduler.config import MAX_DAYS

def perturbation(schedule, perturbation_strength=0.2):
    """
    Perform perturbation on the current schedule to escape local optima.

    This function randomly removes a subset of assignments and adds them back
    to the pool of unassigned errands. The number of assignments removed is
    determined by the perturbation_strength parameter.

    Args:
        schedule (Schedule): The current schedule to perturb.
        perturbation_strength (float): The fraction of assignments to remove (0.0 to 1.0).

    Returns:
        Schedule: The perturbed schedule.
    """
    all_assignments = []
    for day in range(MAX_DAYS):
        all_assignments.extend(schedule.assignments[day])
    
    num_to_remove = int(len(all_assignments) * perturbation_strength)
    assignments_to_remove = random.sample(all_assignments, num_to_remove)

    for assignment in assignments_to_remove:
        day = next(d for d in range(MAX_DAYS) if assignment in schedule.assignments[d])
        schedule.remove_assignment(day, assignment)

    return schedule

def adaptive_perturbation(schedule, iteration, max_iterations, min_strength=0.1, max_strength=0.5):
    """
    Perform adaptive perturbation on the current schedule.

    This function adjusts the perturbation strength based on the current iteration.
    It starts with a higher perturbation strength and gradually decreases it as the
    algorithm progresses.

    Args:
        schedule (Schedule): The current schedule to perturb.
        iteration (int): The current iteration number.
        max_iterations (int): The maximum number of iterations.
        min_strength (float): The minimum perturbation strength.
        max_strength (float): The maximum perturbation strength.

    Returns:
        Schedule: The perturbed schedule.
    """
    progress = iteration / max_iterations
    strength = max_strength - (max_strength - min_strength) * progress
    return perturbation(schedule, strength)

def chain_perturbation(schedule, chain_length=3):
    """
    Perform a chain perturbation on the current schedule.

    This function selects a random errand and then creates a chain of reassignments,
    where each errand is moved to the next contractor in the chain.

    Args:
        schedule (Schedule): The current schedule to perturb.
        chain_length (int): The number of reassignments to make in the chain.

    Returns:
        Schedule: The perturbed schedule.
    """
    all_assignments = []
    for day in range(MAX_DAYS):
        all_assignments.extend(schedule.assignments[day])
    
    if not all_assignments:
        return schedule  # No assignments to perturb

    # Start the chain with a random assignment
    start_assignment = random.choice(all_assignments)
    day = next(d for d in range(MAX_DAYS) if start_assignment in schedule.assignments[d])
    current_errand, current_contractor, _ = start_assignment

    for _ in range(chain_length):
        # Find a new contractor for the current errand
        available_contractors = [c for c in schedule.contractors if c != current_contractor]
        if not available_contractors:
            break

        new_contractor = random.choice(available_contractors)

        # Remove the current assignment
        schedule.remove_assignment(day, (current_errand, current_contractor, _))

        # Try to assign the errand to the new contractor
        for start_time in range(schedule.work_start, schedule.work_end - current_errand.service_time + 1):
            if schedule.assign_errand(new_contractor, current_errand, day, start_time):
                break
        else:
            # If we couldn't assign to the new contractor, put it back with the original
            schedule.assign_errand(current_contractor, current_errand, day, _)

        # Move to the next errand in the chain
        next_assignment = next((a for a in schedule.assignments[day] if a[1] == new_contractor), None)
        if next_assignment is None:
            break

        current_errand, current_contractor, _ = next_assignment

    return schedule