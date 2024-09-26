import argparse
import logging
import random
import matplotlib.pyplot as plt
import tkinter as tk
from SyntheticErrandsScheduler.models import Location, Errand, Contractor, Schedule
from SyntheticErrandsScheduler.algorithms import run_mils, generate_initial_solution
from SyntheticErrandsScheduler.utils import visualize_city_map, plot_schedule
from SyntheticErrandsScheduler.config import GRID_SIZE, ERRANDS, MAX_DAYS, WORK_START, WORK_END
from SyntheticErrandsScheduler.gui.scheduler_gui import SchedulerGUI

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def generate_problem(num_errands, num_contractors, num_days):
    errands = [
        Errand(i, random.choice(list(ERRANDS.keys())), 
               Location(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)),
               start_time=WORK_START,
               end_time=WORK_END,
               days_since_request=random.randint(0, num_days // 2))
        for i in range(num_errands)
    ]

    # Log and verify time windows for each errand
    for errand in errands:
        logging.debug(f"Errand {errand.id} time window: {errand.start_time} - {errand.end_time}")
        if errand.start_time != WORK_START or errand.end_time != WORK_END:
            logging.warning(f"Errand {errand.id} does not have the expected wide-open time window!")

    contractors = [
        Contractor(i, Location(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)))
        for i in range(num_contractors)
    ]

    schedule = Schedule(contractors, errands)
    return schedule

def solve_and_display(schedule, max_iterations, max_time, temperature, cooling_rate, num_runs):
    logging.info("Generating initial solution...")
    schedule, initial_stats = generate_initial_solution(schedule)
    logging.info(f"Initial solution generated. Assigned errands: {initial_stats['assigned_errands']} / {initial_stats['total_errands']}")
    logging.info(f"Initial total profit: ${initial_stats['total_profit']:.2f}")
    logging.info(f"Initial SLA compliance: {initial_stats['sla_compliance']:.2%}")
    logging.info(f"Initial resource utilization: {initial_stats['resource_utilization']:.2%}")

    logging.info("Starting optimization process...")
    
    solution = run_mils(schedule, num_runs=num_runs, max_iterations=max_iterations, 
                        max_time=max_time, temperature=temperature, cooling_rate=cooling_rate)
    
    logging.info(f"Optimization completed. Total profit: ${solution.calculate_total_profit():.2f}")
    logging.info(f"SLA Compliance: {solution.calculate_sla_compliance():.2%}")
    logging.info(f"Resource Utilization: {solution.calculate_resource_utilization():.2%}")

    # Display summary of errand types
    errand_counts = {}
    for errand in solution.errands:
        errand_counts[errand.type] = errand_counts.get(errand.type, 0) + 1
    logging.info("Errand Types Summary:")
    for errand_type, count in errand_counts.items():
        logging.info(f"{errand_type}: {count}")

    # Plot the schedule for each day
    for day in range(solution.num_days):
        fig = plot_schedule(solution, day)
        plt.savefig(f"schedule_day_{day+1}.png", dpi=300, bbox_inches='tight')
        plt.close(fig)
        logging.info(f"Schedule for Day {day+1} saved as schedule_day_{day+1}.png")

    return solution

def run_gui():
    root = tk.Tk()
    gui = SchedulerGUI(root)
    root.mainloop()

def main():
    parser = argparse.ArgumentParser(description="Synthetic Errands Scheduler")
    parser.add_argument("--gui", action="store_true", help="Run the graphical user interface")
    parser.add_argument("--errands", type=int, default=10, help="Number of errands")
    parser.add_argument("--contractors", type=int, default=2, help="Number of contractors")
    parser.add_argument("--days", type=int, default=MAX_DAYS, help="Number of days")
    parser.add_argument("--iterations", type=int, default=1000, help="Maximum number of iterations")
    parser.add_argument("--time", type=int, default=20, help="Maximum time in seconds")
    parser.add_argument("--temperature", type=float, default=100.0, help="Initial temperature")
    parser.add_argument("--cooling-rate", type=float, default=0.995, help="Cooling rate")
    parser.add_argument("--runs", type=int, default=2, help="Number of runs")
    parser.add_argument("--generate-only", action="store_true", help="Only generate the problem without solving")

    args = parser.parse_args()

    if args.gui:
        run_gui()
    else:
        schedule = generate_problem(args.errands, args.contractors, args.days)
        logging.info("Problem generated successfully.")
        
        if not args.generate_only:
            logging.info("Generating initial solution and optimizing...")
            solve_and_display(schedule, args.iterations, args.time, args.temperature, args.cooling_rate, args.runs)
        else:
            logging.info("Problem generation complete. Use --generate-only flag to solve the problem.")

if __name__ == "__main__":
    main()