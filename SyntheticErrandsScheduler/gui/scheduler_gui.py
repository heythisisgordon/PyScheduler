import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random
import threading
import io
import sys

from SyntheticErrandsScheduler.models import Location, Errand, Contractor, Schedule
from SyntheticErrandsScheduler.algorithms import modified_iterated_local_search, run_mils, generate_initial_solution
from SyntheticErrandsScheduler.utils import visualize_city_map, plot_route
from SyntheticErrandsScheduler.config import GRID_SIZE, ERRANDS, MAX_DAYS
from SyntheticErrandsScheduler.gui.plot_utils import plot_problem, plot_solution, create_plot
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

class SchedulerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Synthetic Errands Scheduler")

        # Create main frame
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create left frame for inputs
        self.left_frame = ttk.Frame(self.main_frame, width=300)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=10, pady=10)
        self.left_frame.pack_propagate(False)

        # Create right frame for output and plot
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_input_widgets()
        self.create_output_widgets()

    def create_input_widgets(self):
        # Instructions
        ttk.Label(self.left_frame, text="Instructions:", font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky="w", padx=5, pady=5)
        instructions = "1. Enter the problem parameters.\n2. Click 'Generate Problem' to create a new problem.\n3. Click 'Generate Initial Solution' to create a starting point.\n4. Configure algorithm settings.\n5. Click 'Solve' to find an optimized solution.\n6. Use 'Edit' to modify the initial conditions if needed."
        ttk.Label(self.left_frame, text=instructions, wraplength=280).grid(row=1, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        # Problem Parameters
        ttk.Label(self.left_frame, text="Problem Parameters", font=('Arial', 10, 'bold')).grid(row=2, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        ttk.Label(self.left_frame, text="Number of Errands:").grid(row=3, column=0, sticky="e", padx=5, pady=2)
        self.num_errands_entry = ttk.Entry(self.left_frame, width=10)
        self.num_errands_entry.grid(row=3, column=1, sticky="w", padx=5, pady=2)
        self.num_errands_entry.insert(0, "10")

        ttk.Label(self.left_frame, text="Number of Contractors:").grid(row=4, column=0, sticky="e", padx=5, pady=2)
        self.num_contractors_entry = ttk.Entry(self.left_frame, width=10)
        self.num_contractors_entry.grid(row=4, column=1, sticky="w", padx=5, pady=2)
        self.num_contractors_entry.insert(0, "2")

        ttk.Label(self.left_frame, text="Number of Days:").grid(row=5, column=0, sticky="e", padx=5, pady=2)
        self.num_days_entry = ttk.Entry(self.left_frame, width=10)
        self.num_days_entry.grid(row=5, column=1, sticky="w", padx=5, pady=2)
        self.num_days_entry.insert(0, str(MAX_DAYS))

        # Generate Problem button
        self.generate_button = ttk.Button(self.left_frame, text="Generate Problem", command=self.generate_problem)
        self.generate_button.grid(row=6, column=0, columnspan=2, pady=10)

        # Generate Initial Solution button
        self.generate_initial_solution_button = ttk.Button(self.left_frame, text="Generate Initial Solution", command=self.generate_initial_solution)
        self.generate_initial_solution_button.grid(row=7, column=0, columnspan=2, pady=10)
        self.generate_initial_solution_button.config(state=tk.DISABLED)

        # Algorithm Settings
        ttk.Label(self.left_frame, text="Algorithm Settings", font=('Arial', 10, 'bold')).grid(row=8, column=0, columnspan=2, sticky="w", padx=5, pady=5)

        ttk.Label(self.left_frame, text="Max Iterations:").grid(row=9, column=0, sticky="e", padx=5, pady=2)
        self.max_iterations_entry = ttk.Entry(self.left_frame, width=10)
        self.max_iterations_entry.grid(row=9, column=1, sticky="w", padx=5, pady=2)
        self.max_iterations_entry.insert(0, "1000")

        ttk.Label(self.left_frame, text="Max Time (seconds):").grid(row=10, column=0, sticky="e", padx=5, pady=2)
        self.max_time_entry = ttk.Entry(self.left_frame, width=10)
        self.max_time_entry.grid(row=10, column=1, sticky="w", padx=5, pady=2)
        self.max_time_entry.insert(0, "20")

        ttk.Label(self.left_frame, text="Initial Temperature:").grid(row=11, column=0, sticky="e", padx=5, pady=2)
        self.temperature_entry = ttk.Entry(self.left_frame, width=10)
        self.temperature_entry.grid(row=11, column=1, sticky="w", padx=5, pady=2)
        self.temperature_entry.insert(0, "100.0")

        ttk.Label(self.left_frame, text="Cooling Rate:").grid(row=12, column=0, sticky="e", padx=5, pady=2)
        self.cooling_rate_entry = ttk.Entry(self.left_frame, width=10)
        self.cooling_rate_entry.grid(row=12, column=1, sticky="w", padx=5, pady=2)
        self.cooling_rate_entry.insert(0, "0.995")

        ttk.Label(self.left_frame, text="Number of Runs:").grid(row=13, column=0, sticky="e", padx=5, pady=2)
        self.num_runs_entry = ttk.Entry(self.left_frame, width=10)
        self.num_runs_entry.grid(row=13, column=1, sticky="w", padx=5, pady=2)
        self.num_runs_entry.insert(0, "2")

        # Solve button
        self.solve_button = ttk.Button(self.left_frame, text="Solve", command=self.solve_problem)
        self.solve_button.grid(row=14, column=0, columnspan=2, pady=10)
        self.solve_button.config(state=tk.DISABLED)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.left_frame, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.grid(row=15, column=0, columnspan=2, pady=10)
        
        # Add a new frame for displaying initial conditions
        self.initial_conditions_frame = ttk.LabelFrame(self.left_frame, text="Initial Conditions")
        self.initial_conditions_frame.grid(row=16, column=0, columnspan=2, padx=5, pady=5, sticky="nsew")

        # Add a text widget to display initial conditions
        self.initial_conditions_text = scrolledtext.ScrolledText(self.initial_conditions_frame, wrap=tk.WORD, width=30, height=10)
        self.initial_conditions_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Add an Edit button
        self.edit_button = ttk.Button(self.initial_conditions_frame, text="Edit", command=self.edit_initial_conditions)
        self.edit_button.pack(pady=5)

    def create_output_widgets(self):
        # Create notebook for multiple tabs
        self.notebook = ttk.Notebook(self.right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Create tabs
        self.initial_solution_tab = ttk.Frame(self.notebook)
        self.results_tab = ttk.Frame(self.notebook)
        self.visualization_tab = ttk.Frame(self.notebook)
        self.details_tab = ttk.Frame(self.notebook)
        self.parameters_tab = ttk.Frame(self.notebook)

        self.notebook.add(self.initial_solution_tab, text="Initial Solution")
        self.notebook.add(self.results_tab, text="Optimized Results")
        self.notebook.add(self.visualization_tab, text="Visualization")
        self.notebook.add(self.details_tab, text="Details")
        self.notebook.add(self.parameters_tab, text="Problem Parameters")

        # Initial Solution tab
        self.initial_solution_text = scrolledtext.ScrolledText(self.initial_solution_tab, wrap=tk.WORD, width=60, height=20)
        self.initial_solution_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Results tab
        self.output_text = scrolledtext.ScrolledText(self.results_tab, wrap=tk.WORD, width=60, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Visualization tab
        self.fig, self.ax = create_plot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.visualization_tab)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Details tab
        self.details_text = scrolledtext.ScrolledText(self.details_tab, wrap=tk.WORD, width=60, height=20)
        self.details_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Parameters tab
        self.parameters_text = scrolledtext.ScrolledText(self.parameters_tab, wrap=tk.WORD, width=60, height=20)
        self.parameters_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def generate_problem(self):
        try:
            num_errands = int(self.num_errands_entry.get())
            num_contractors = int(self.num_contractors_entry.get())
            num_days = int(self.num_days_entry.get())

            if num_errands <= 0 or num_contractors <= 0 or num_days <= 0:
                raise ValueError("All inputs must be positive integers.")

            self.errands = [
                Errand(i, random.choice(list(ERRANDS.keys())), 
                       Location(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)))
                for i in range(num_errands)
            ]

            self.contractors = [
                Contractor(i, Location(random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)))
                for i in range(num_contractors)
            ]

            self.schedule = Schedule(self.contractors, self.errands)

            # Capture print output
            old_stdout = sys.stdout
            sys.stdout = buffer = io.StringIO()

            try:
                self.visualize_problem()
            except Exception as e:
                print(f"Error in visualize_problem: {str(e)}")
            finally:
                sys.stdout = old_stdout

            # Get the captured output
            debug_output = buffer.getvalue()

            self.display_initial_conditions()
            self.update_parameters_tab()

            # Display debug output in a message box
            messagebox.showinfo("Debug Output", debug_output)

            # Enable the Generate Initial Solution button
            self.generate_initial_solution_button.config(state=tk.NORMAL)

            # Switch to the Visualization tab
            self.notebook.select(self.visualization_tab)

            messagebox.showinfo("Success", "Problem generated successfully. You can now generate an initial solution.")

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def generate_initial_solution(self):
        if not hasattr(self, 'schedule'):
            messagebox.showerror("Error", "Please generate a problem first.")
            return

        try:
            # Generate initial solution
            self.schedule, initial_stats = generate_initial_solution(self.schedule)

            # Calculate total revenue and costs
            total_revenue = sum(ERRANDS[errand.type]['charge'] for errand in self.schedule.completed_errands)
            total_costs = sum(ERRANDS[errand.type]['time'] * 0.5 for errand in self.schedule.completed_errands)  # Assuming $0.5 per minute as cost

            # Display initial solution information
            self.initial_solution_text.delete(1.0, tk.END)
            self.initial_solution_text.insert(tk.END, f"Initial Greedy Solution Statistics:\n\n")
            self.initial_solution_text.insert(tk.END, f"Total Errands: {initial_stats['total_errands']}\n")
            self.initial_solution_text.insert(tk.END, f"Assigned Errands: {initial_stats['assigned_errands']}\n")
            self.initial_solution_text.insert(tk.END, f"Unassigned Errands: {initial_stats['total_errands'] - initial_stats['assigned_errands']}\n\n")
            self.initial_solution_text.insert(tk.END, f"Total Revenue: ${total_revenue:.2f}\n")
            self.initial_solution_text.insert(tk.END, f"Total Costs: ${total_costs:.2f}\n")
            self.initial_solution_text.insert(tk.END, f"Total Profit: ${initial_stats['total_profit']:.2f}\n")
            self.initial_solution_text.insert(tk.END, f"SLA Compliance: {initial_stats['sla_compliance']:.2%}\n")
            self.initial_solution_text.insert(tk.END, f"Resource Utilization: {initial_stats['resource_utilization']:.2%}\n")

            self.visualize_solution(self.schedule)
            self.update_details(self.schedule)
            self.update_parameters_tab()

            # Switch to the Initial Solution tab
            self.notebook.select(self.initial_solution_tab)

            messagebox.showinfo("Success", "Initial solution generated successfully. You can now solve the problem.")

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while generating the initial solution: {str(e)}")
        finally:
            # Enable the Solve button, even if an error occurred
            self.solve_button.config(state=tk.NORMAL)

    def solve_problem(self):
        if not hasattr(self, 'schedule'):
            messagebox.showerror("Error", "Please generate a problem and an initial solution first.")
            return

        try:
            max_iterations = int(self.max_iterations_entry.get())
            max_time = int(self.max_time_entry.get())
            temperature = float(self.temperature_entry.get())
            cooling_rate = float(self.cooling_rate_entry.get())
            num_runs = int(self.num_runs_entry.get())

            self.progress_bar.start()
            self.solve_button.config(state=tk.DISABLED)

            # Run the solver in a separate thread
            threading.Thread(target=self._solve_and_update, args=(max_iterations, max_time, temperature, cooling_rate, num_runs), daemon=True).start()

        except ValueError as e:
            messagebox.showerror("Input Error", "Please ensure all algorithm settings are valid numbers.")
            self.solve_button.config(state=tk.NORMAL)

    def _solve_and_update(self, max_iterations, max_time, temperature, cooling_rate, num_runs):
        try:
            solution = run_mils(self.schedule, num_runs=num_runs, max_iterations=max_iterations, 
                                max_time=max_time, temperature=temperature, cooling_rate=cooling_rate)
            self.master.after(0, self._update_solution, solution)
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
        finally:
            self.master.after(0, self.progress_bar.stop)
            self.master.after(0, self.solve_button.config, {'state': tk.NORMAL})

    def _update_solution(self, solution):
        self.output_text.delete(1.0, tk.END)
        if solution is None:
            self.output_text.insert(tk.END, "No valid solution found. Please try again with different parameters.\n")
            return

        self.schedule = solution  # Save the improved solution

        # Calculate total revenue and costs
        total_revenue = sum(ERRANDS[errand.type]['charge'] for errand in self.schedule.completed_errands)
        total_costs = sum(ERRANDS[errand.type]['time'] * 0.5 for errand in self.schedule.completed_errands)  # Assuming $0.5 per minute as cost

        self.output_text.insert(tk.END, f"Total Revenue: ${total_revenue:.2f}\n")
        self.output_text.insert(tk.END, f"Total Costs: ${total_costs:.2f}\n")
        self.output_text.insert(tk.END, f"Total Profit: ${solution.calculate_total_profit():.2f}\n")
        self.output_text.insert(tk.END, f"SLA Compliance: {solution.calculate_sla_compliance():.2%}\n")
        self.output_text.insert(tk.END, f"Resource Utilization: {solution.calculate_resource_utilization():.2%}\n\n")

        self.output_text.insert(tk.END, "Errand Types Summary:\n")
        errand_counts = {}
        for errand in solution.completed_errands:
            errand_counts[errand.type] = errand_counts.get(errand.type, 0) + 1
        for errand_type, count in errand_counts.items():
            self.output_text.insert(tk.END, f"{errand_type}: {count}\n")

        self.visualize_solution(solution)
        self.update_details(solution)
        self.update_parameters_tab()

        # Switch to the Optimized Results tab
        self.notebook.select(self.results_tab)

    def visualize_problem(self):
        self.ax.clear()
        plot_problem(self.ax, self.errands, self.contractors)
        self.fig.tight_layout()
        self.fig.subplots_adjust(right=0.75)  # Adjust the right margin to make room for the legend
        self.canvas.draw()

    def visualize_solution(self, solution):
        self.ax.clear()
        plot_solution(self.ax, solution)
        self.fig.tight_layout()
        self.fig.subplots_adjust(right=0.75)  # Adjust the right margin to make room for the legend
        self.canvas.draw()

    def update_details(self, solution):
        self.details_text.delete(1.0, tk.END)
        
        # Add overall statistics
        self.details_text.insert(tk.END, "Overall Statistics:\n")
        self.details_text.insert(tk.END, f"SLA Compliance Rate: {solution.calculate_sla_compliance():.2%}\n")
        self.details_text.insert(tk.END, f"Resource Utilization: {solution.calculate_resource_utilization():.2%}\n\n")

        # Add contractor schedules
        self.details_text.insert(tk.END, "Contractor Schedules:\n")
        for day in range(solution.num_days):
            self.details_text.insert(tk.END, f"Day {day + 1}:\n")
            self.details_text.insert(tk.END, "Contractor | Errand | Type | Transit Start | Transit End | Errand Start | Errand End\n")
            self.details_text.insert(tk.END, "-" * 80 + "\n")
            for errand, contractor, start_time in solution.assignments[day]:
                transit_time = calculate_travel_time(contractor.start_location, errand.location)
                transit_start = start_time - transit_time
                errand_duration = ERRANDS[errand.type]['time']
                errand_end = start_time + errand_duration
                self.details_text.insert(tk.END, f"{contractor.id:9d} | {errand.id:6d} | {errand.type:4s} | {self.format_time(transit_start):12s} | {self.format_time(start_time):10s} | {self.format_time(start_time):11s} | {self.format_time(errand_end):9s}\n")
            self.details_text.insert(tk.END, "\n")

    def format_time(self, minutes):
        hours, mins = divmod(int(minutes), 60)
        return f"{hours:02d}:{mins:02d}"

    def display_initial_conditions(self):
        self.initial_conditions_text.delete(1.0, tk.END)
        for i, errand in enumerate(self.errands):
            self.initial_conditions_text.insert(tk.END, f"Errand {i}: {errand.type} at ({errand.location.x}, {errand.location.y})\n")
        for i, contractor in enumerate(self.contractors):
            self.initial_conditions_text.insert(tk.END, f"Contractor {i}: Start at ({contractor.start_location.x}, {contractor.start_location.y})\n")

    def edit_initial_conditions(self):
        edit_window = tk.Toplevel(self.master)
        edit_window.title("Edit Initial Conditions")

        text_widget = scrolledtext.ScrolledText(edit_window, wrap=tk.WORD, width=40, height=20)
        text_widget.pack(padx=10, pady=10)
        text_widget.insert(tk.END, self.initial_conditions_text.get(1.0, tk.END))

        def save_changes():
            new_conditions = text_widget.get(1.0, tk.END).strip().split('\n')
            self.errands = []
            self.contractors = []
            for line in new_conditions:
                if line.startswith("Errand"):
                    parts = line.split()
                    errand_type = parts[2]
                    x, y = map(int, parts[-1][1:-1].split(','))
                    self.errands.append(Errand(len(self.errands), errand_type, Location(x, y)))
                elif line.startswith("Contractor"):
                    parts = line.split()
                    x, y = map(int, parts[-1][1:-1].split(','))
                    self.contractors.append(Contractor(len(self.contractors), Location(x, y)))
            
            self.schedule = Schedule(self.contractors, self.errands)
            self.display_initial_conditions()
            self.visualize_problem()
            self.update_parameters_tab()
            edit_window.destroy()

            # Reset the solution-related buttons
            self.generate_initial_solution_button.config(state=tk.NORMAL)
            self.solve_button.config(state=tk.DISABLED)

        save_button = ttk.Button(edit_window, text="Save Changes", command=save_changes)
        save_button.pack(pady=10)

    def update_parameters_tab(self):
        self.parameters_text.delete(1.0, tk.END)
        
        # General problem parameters
        self.parameters_text.insert(tk.END, "General Problem Parameters:\n")
        self.parameters_text.insert(tk.END, f"Number of Errands: {len(self.errands)}\n")
        self.parameters_text.insert(tk.END, f"Number of Contractors: {len(self.contractors)}\n")
        self.parameters_text.insert(tk.END, f"Number of Days: {self.schedule.num_days}\n")
        self.parameters_text.insert(tk.END, f"Grid Size: {GRID_SIZE}x{GRID_SIZE}\n\n")

        # Errand types and their details
        self.parameters_text.insert(tk.END, "Errand Types:\n")
        for errand_type, details in ERRANDS.items():
            self.parameters_text.insert(tk.END, f"{errand_type}:\n")
            self.parameters_text.insert(tk.END, f"  Duration: {details['time']} minutes\n")
            self.parameters_text.insert(tk.END, f"  Base Fee: ${details['charge']}\n")
            self.parameters_text.insert(tk.END, f"  Priority: {details['priority']}\n")
            self.parameters_text.insert(tk.END, f"  Early Incentive: ${details['early_incentive']}\n")
            self.parameters_text.insert(tk.END, f"  Late Penalty: {details['late_penalty'] * 100}%\n\n")

        # Contractor details
        self.parameters_text.insert(tk.END, "Contractors:\n")
        for contractor in self.contractors:
            self.parameters_text.insert(tk.END, f"Contractor {contractor.id}:\n")
            self.parameters_text.insert(tk.END, f"  Start Location: ({contractor.start_location.x}, {contractor.start_location.y})\n\n")

        # Errand details
        self.parameters_text.insert(tk.END, "Errands:\n")
        for errand in self.errands:
            self.parameters_text.insert(tk.END, f"Errand {errand.id}:\n")
            self.parameters_text.insert(tk.END, f"  Type: {errand.type}\n")
            self.parameters_text.insert(tk.END, f"  Location: ({errand.location.x}, {errand.location.y})\n")
            self.parameters_text.insert(tk.END, f"  Duration: {ERRANDS[errand.type]['time']} minutes\n")
            self.parameters_text.insert(tk.END, f"  Base Fee: ${ERRANDS[errand.type]['charge']}\n")
            self.parameters_text.insert(tk.END, f"  Priority: {ERRANDS[errand.type]['priority']}\n\n")

def main():
    root = tk.Tk()
    gui = SchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()