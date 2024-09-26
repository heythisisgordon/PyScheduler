import time
import random
import math
import logging
from SyntheticErrandsScheduler.algorithms.initial_solution import generate_initial_solution
from SyntheticErrandsScheduler.algorithms.local_search import local_search
from SyntheticErrandsScheduler.algorithms.perturbation import adaptive_perturbation
from SyntheticErrandsScheduler.models.schedule import Schedule
from SyntheticErrandsScheduler.config import SLA_DAYS, WORK_START, WORK_END

# Set up logging
logging.basicConfig(filename='mils_log.log', level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

def modified_iterated_local_search(schedule, max_iterations=1000, max_time=300, temperature=100.0, cooling_rate=0.995):
    """
    Perform Modified Iterated Local Search to maximize profit while satisfying constraints.

    This version focuses on improving the profit through perturbation, local search,
    and simulated annealing acceptance criteria for worse solutions to escape local optima.
    It also considers SLA compliance, early completion incentives, and resource utilization.

    Args:
        schedule (Schedule): The initial schedule to optimize.
        max_iterations (int): The maximum number of iterations to perform.
        max_time (float): The maximum time (in seconds) to run the algorithm.
        temperature (float): The initial temperature for the acceptance criterion.
        cooling_rate (float): The rate at which the temperature cools down.

    Returns:
        Schedule: The best profit-maximized schedule found.
    """
    start_time = time.time()
    
    try:
        logging.info("Generating initial solution")
        current_solution, stats = generate_initial_solution(schedule)
        logging.debug(f"Initial solution generated: {current_solution}, Stats: {stats}")
        
        logging.info("Performing initial local search to maximize profit")
        current_solution = local_search(current_solution, max_time=30)
        logging.debug(f"After initial profit-maximizing local search: {current_solution}")
        
        best_solution = current_solution.copy()
        best_score = calculate_solution_score(best_solution)
        logging.info(f"Initial best score: {best_score}")

        iteration = 0
        plateau_counter = 0
        adaptive_temp = temperature

        while iteration < max_iterations and time.time() - start_time < max_time:
            try:
                logging.info(f"Starting iteration {iteration}")
                
                # Perturbation
                logging.info("Performing adaptive perturbation")
                perturbed_solution = adaptive_perturbation(current_solution.copy(), iteration, max_iterations)
                logging.debug(f"After perturbation: {perturbed_solution}")
                
                # Local search
                logging.info("Performing local search focused on profit maximization")
                improved_solution = local_search(perturbed_solution, max_time=10)
                logging.debug(f"After local search: {improved_solution}")
                
                # Solution evaluation
                current_score = calculate_solution_score(current_solution)
                improved_score = calculate_solution_score(improved_solution)

                logging.debug(f"Current score: {current_score}, Improved score: {improved_score}")

                # Acceptance criterion (simulated annealing-like with adaptive temperature)
                if improved_score > current_score:
                    current_solution = improved_solution
                    logging.debug("Accepted new solution (improvement)")
                    plateau_counter = 0
                elif random.random() < math.exp((improved_score - current_score) / adaptive_temp):
                    current_solution = improved_solution
                    logging.debug(f"Accepted new solution (probabilistic, temp: {adaptive_temp})")
                    plateau_counter = 0
                else:
                    logging.debug("Rejected new solution")
                    plateau_counter += 1
                
                # Update best solution if necessary
                if improved_score > best_score:
                    best_solution = improved_solution.copy()
                    best_score = improved_score
                    logging.info(f"New best score: {best_score}")
                    plateau_counter = 0
                
                # Adaptive mechanisms
                if plateau_counter > 50:
                    adaptive_temp *= 2  # Increase temperature to encourage exploration
                    plateau_counter = 0
                    logging.info(f"Increased temperature to {adaptive_temp}")
                else:
                    adaptive_temp *= cooling_rate
                
                # Increment iteration counter
                iteration += 1
                
                if iteration % 100 == 0:
                    logging.info(f"Iteration {iteration}: Best score = {best_score}")
            
            except Exception as e:
                logging.error(f"Error in iteration {iteration}: {str(e)}")
                logging.exception("Exception traceback:")
                continue

    except Exception as e:
        logging.error(f"Error in modified_iterated_local_search: {str(e)}")
        logging.exception("Exception traceback:")
        return schedule  # Return the original schedule if an error occurs
    
    logging.info("Finished modified_iterated_local_search")
    return best_solution

def calculate_solution_score(solution):
    """
    Calculate a comprehensive score for the solution, considering profit, SLA compliance,
    early completion incentives, and resource utilization.
    """
    profit = solution.calculate_total_profit()
    sla_compliance = solution.calculate_sla_compliance()
    early_completion_bonus = calculate_early_completion_bonus(solution)
    resource_utilization = calculate_resource_utilization(solution)
    
    # Combine the factors with appropriate weights
    score = (profit * 0.5 +
             sla_compliance * 0.3 +
             early_completion_bonus * 0.1 +
             resource_utilization * 0.1)
    
    logging.debug(f"Score breakdown - Profit: {profit}, SLA Compliance: {sla_compliance}, "
                  f"Early Completion Bonus: {early_completion_bonus}, "
                  f"Resource Utilization: {resource_utilization}")
    
    return score

def calculate_early_completion_bonus(solution):
    """Calculate the total early completion bonus for all errands in the solution."""
    total_bonus = 0
    for day in range(solution.num_days):
        for errand, _, _ in solution.assignments[day]:
            days_early = max(0, SLA_DAYS - (day - errand.days_since_request))
            total_bonus += days_early * 0.05 * errand.charge
    return total_bonus

def calculate_resource_utilization(solution):
    """Calculate the resource utilization score for the solution."""
    total_capacity = len(solution.contractors) * solution.num_days * (WORK_END - WORK_START)
    total_used = sum(
        sum(errand.service_time for errand, _, _ in day_assignments)
        for day_assignments in solution.assignments.values()
    )
    return total_used / total_capacity if total_capacity > 0 else 0

def verify_solution(solution):
    """
    Perform sanity checks on the solution to ensure it's valid.
    """
    # Check if all errands are assigned
    assigned_errands = set()
    for day_assignments in solution.assignments.values():
        for errand, _, _ in day_assignments:
            assigned_errands.add(errand.id)
    
    if len(assigned_errands) != len(solution.errands):
        logging.warning(f"Not all errands are assigned. Assigned: {len(assigned_errands)}, Total: {len(solution.errands)}")
    
    # Check for overlapping assignments
    for day, day_assignments in solution.assignments.items():
        contractor_schedules = {}
        for errand, contractor, start_time in day_assignments:
            if contractor.id not in contractor_schedules:
                contractor_schedules[contractor.id] = []
            contractor_schedules[contractor.id].append((start_time, start_time + errand.service_time))
        
        for contractor_id, schedule in contractor_schedules.items():
            schedule.sort()
            for i in range(len(schedule) - 1):
                if schedule[i][1] > schedule[i+1][0]:
                    logging.warning(f"Overlapping assignments for contractor {contractor_id} on day {day}")
    
    return True

def run_mils(schedule, num_runs=5, **kwargs):
    """
    Run the MILS algorithm multiple times and return the best result.

    Args:
        schedule (Schedule): The initial schedule to optimize.
        num_runs (int): The number of times to run the MILS algorithm.
        **kwargs: Additional arguments to pass to the MILS function.

    Returns:
        Schedule: The best schedule found across all runs.
    """
    best_solution = None
    best_score = float('-inf')

    for run in range(num_runs):
        logging.info(f"Starting run {run + 1}/{num_runs}")
        try:
            solution = modified_iterated_local_search(schedule, **kwargs)
            score = calculate_solution_score(solution)
            
            if score > best_score:
                best_solution = solution
                best_score = score
            
            logging.info(f"Run {run + 1} completed. Score: {score}")
            logging.info(f"Solution details - Profit: {solution.calculate_total_profit()}, "
                         f"SLA Compliance: {solution.calculate_sla_compliance()}, "
                         f"Resource Utilization: {calculate_resource_utilization(solution)}")
            
            verify_solution(solution)
        except Exception as e:
            logging.error(f"Error in run {run + 1}: {str(e)}")
            logging.exception("Exception traceback:")

    if best_solution:
        logging.info(f"Best overall score: {best_score}")
        logging.info(f"Best profit: {best_solution.calculate_total_profit()}")
        logging.info(f"Best SLA compliance: {best_solution.calculate_sla_compliance()}")
        logging.info(f"Best resource utilization: {calculate_resource_utilization(best_solution)}")
    else:
        logging.error("All runs failed.")
    
    return best_solution