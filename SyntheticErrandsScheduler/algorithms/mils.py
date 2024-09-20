import time
import random
import math
import logging
from SyntheticErrandsScheduler.algorithms.initial_solution import generate_initial_solution
from SyntheticErrandsScheduler.algorithms.local_search import local_search
from SyntheticErrandsScheduler.algorithms.perturbation import adaptive_perturbation

# Set up logging
logging.basicConfig(filename='mils_error.log', level=logging.DEBUG)

def modified_iterated_local_search(schedule, max_iterations=1000, max_time=60, temperature=1.0, cooling_rate=0.995):
    """
    Perform Modified Iterated Local Search to find a good schedule.

    This function implements the MILS algorithm, which combines local search with
    perturbation to escape local optima. It also includes a simulated annealing-like
    acceptance criterion for worse solutions.

    Args:
        schedule (Schedule): The initial schedule to optimize.
        max_iterations (int): The maximum number of iterations to perform.
        max_time (float): The maximum time (in seconds) to run the algorithm.
        temperature (float): The initial temperature for the acceptance criterion.
        cooling_rate (float): The rate at which the temperature cools down.

    Returns:
        Schedule: The best schedule found.
    """
    start_time = time.time()
    
    try:
        logging.info("Generating initial solution")
        current_solution = generate_initial_solution(schedule)
        logging.debug(f"Initial solution generated: {current_solution}")
        
        logging.info("Performing initial local search")
        current_solution = local_search(current_solution, max_time=10)  # Set a time limit for local search
        logging.debug(f"After initial local search: {current_solution}")
        
        best_solution = current_solution.copy()
        best_profit = best_solution.calculate_total_profit()
        logging.info(f"Initial best profit: {best_profit}")

        iteration = 0
        while iteration < max_iterations and time.time() - start_time < max_time:
            try:
                logging.info(f"Starting iteration {iteration}")
                
                # Perturbation
                logging.info("Performing adaptive perturbation")
                perturbed_solution = adaptive_perturbation(current_solution.copy(), iteration, max_iterations)
                logging.debug(f"After perturbation: {perturbed_solution}")
                
                # Local search
                logging.info("Performing local search")
                improved_solution = local_search(perturbed_solution, max_time=5)  # Set a time limit for local search
                logging.debug(f"After local search: {improved_solution}")
                
                # Calculate profits
                logging.info("Calculating profits")
                current_profit = current_solution.calculate_total_profit()
                improved_profit = improved_solution.calculate_total_profit()
                logging.debug(f"Current profit: {current_profit}, Improved profit: {improved_profit}")
                
                # Acceptance criterion (simulated annealing-like)
                if improved_profit > current_profit or \
                   random.random() < math.exp((improved_profit - current_profit) / temperature):
                    current_solution = improved_solution
                    current_profit = improved_profit
                    logging.debug("Accepted new solution")
                else:
                    logging.debug("Rejected new solution")
                
                # Update best solution if necessary
                if current_profit > best_profit:
                    best_solution = current_solution.copy()
                    best_profit = current_profit
                    logging.info(f"New best profit: {best_profit}")
                
                # Cool down the temperature
                temperature *= cooling_rate
                
                # Increment iteration counter
                iteration += 1
                
                # Optionally, print progress
                if iteration % 100 == 0:
                    logging.info(f"Iteration {iteration}: Best profit = {best_profit}")
            
            except Exception as e:
                logging.error(f"Error in iteration {iteration}: {str(e)}")
                logging.error(f"Current solution: {current_solution}")
                # Instead of raising, let's continue to the next iteration
                continue

            # Check if time limit is reached
            if time.time() - start_time >= max_time:
                logging.info("Time limit reached. Stopping MILS.")
                break
    
    except Exception as e:
        logging.error(f"Error in modified_iterated_local_search: {str(e)}")
        logging.exception("Exception traceback:")
        return schedule  # Return the original schedule if an error occurs
    
    logging.info("Finished modified_iterated_local_search")
    return best_solution

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
    best_profit = float('-inf')

    for run in range(num_runs):
        logging.info(f"Starting run {run + 1}/{num_runs}")
        try:
            solution = modified_iterated_local_search(schedule, **kwargs)
            profit = solution.calculate_total_profit()
            
            if profit > best_profit:
                best_solution = solution
                best_profit = profit
            
            logging.info(f"Run {run + 1} completed. Profit: {profit}")
        except Exception as e:
            logging.error(f"Error in run {run + 1}: {str(e)}")
            logging.error(f"Run {run + 1} failed.")
    
    if best_solution:
        logging.info(f"Best overall profit: {best_profit}")
    else:
        logging.error("All runs failed.")
    
    return best_solution