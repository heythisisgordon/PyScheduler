from SyntheticErrandsScheduler.gui.plot_utils import plot_problem, plot_solution, create_plot
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import random

from SyntheticErrandsScheduler.models import Location, Errand, Contractor, Schedule
from SyntheticErrandsScheduler.algorithms import modified_iterated_local_search
from SyntheticErrandsScheduler.utils import visualize_city_map, plot_route
from SyntheticErrandsScheduler.config import GRID_SIZE, ERRANDS

class SchedulerGUI:
    def __init__(self, master):
        self.master = master
        master.title("Synthetic Errands Scheduler")

        # Create main frame
        self.main_frame = ttk.Frame(master)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Create left frame for inputs
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Create right frame for output and plot
        self.right_frame = ttk.Frame(self.main_frame)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.create_input_widgets()
        self.create_output_widgets()

    def create_input_widgets(self):
        # Number of Errands
        ttk.Label(self.left_frame, text="Number of Errands:").grid(row=0, column=0, sticky="e", padx=5, pady=5)
        self.num_errands_entry = ttk.Entry(self.left_frame)
        self.num_errands_entry.grid(row=0, column=1, padx=5, pady=5)
        self.num_errands_entry.insert(0, "10")

        # Number of Contractors
        ttk.Label(self.left_frame, text="Number of Contractors:").grid(row=1, column=0, sticky="e", padx=5, pady=5)
        self.num_contractors_entry = ttk.Entry(self.left_frame)
        self.num_contractors_entry.grid(row=1, column=1, padx=5, pady=5)
        self.num_contractors_entry.insert(0, "3")

        # Number of Days
        ttk.Label(self.left_frame, text="Number of Days:").grid(row=2, column=0, sticky="e", padx=5, pady=5)
        self.num_days_entry = ttk.Entry(self.left_frame)
        self.num_days_entry.grid(row=2, column=1, padx=5, pady=5)
        self.num_days_entry.insert(0, "5")

        # Generate button
        self.generate_button = ttk.Button(self.left_frame, text="Generate Problem", command=self.generate_problem)
        self.generate_button.grid(row=3, column=0, columnspan=2, pady=10)

        # Solve button
        self.solve_button = ttk.Button(self.left_frame, text="Solve", command=self.solve_problem)
        self.solve_button.grid(row=4, column=0, columnspan=2, pady=10)

        # Progress bar
        self.progress_bar = ttk.Progressbar(self.left_frame, orient="horizontal", length=200, mode="indeterminate")
        self.progress_bar.grid(row=5, column=0, columnspan=2, pady=10)

    def create_output_widgets(self):
        # Create text area for output
        self.output_text = scrolledtext.ScrolledText(self.right_frame, wrap=tk.WORD, width=60, height=20)
        self.output_text.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

        # Create a figure for the plot
        self.fig, self.ax = create_plot()
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.right_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

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

            # Fix: Swap the order of arguments
            self.schedule = Schedule(self.contractors, self.errands)

            self.output_text.delete(1.0, tk.END)
            self.output_text.insert(tk.END, f"Generated problem with {num_errands} errands and {num_contractors} contractors.\n")
            
            self.visualize_problem()

        except ValueError as e:
            messagebox.showerror("Input Error", str(e))

    def solve_problem(self):
        if not hasattr(self, 'schedule'):
            messagebox.showerror("Error", "Please generate a problem first.")
            return

        self.progress_bar.start()
        self.solve_button.config(state=tk.DISABLED)

        # Run the solver in a separate thread
        import threading
        threading.Thread(target=self._solve_and_update, daemon=True).start()

    def _solve_and_update(self):
        try:
            solution = modified_iterated_local_search(self.schedule)
            
            self.master.after(0, self._update_solution, solution)
        except Exception as e:
            self.master.after(0, messagebox.showerror, "Error", str(e))
        finally:
            self.master.after(0, self.progress_bar.stop)
            self.master.after(0, self.solve_button.config, {'state': tk.NORMAL})

    def _update_solution(self, solution):
        self.output_text.delete(1.0, tk.END)
        self.output_text.insert(tk.END, f"Total profit: ${solution.calculate_total_profit():.2f}\n\n")

        for day in range(solution.num_days):
            self.output_text.insert(tk.END, f"Day {day + 1}:\n")
            for errand, contractor, start_time in solution.assignments[day]:
                self.output_text.insert(tk.END, f"  Contractor {contractor.id}: Errand {errand.id} ({errand.type}) at {start_time // 60:02d}:{start_time % 60:02d}\n")
            self.output_text.insert(tk.END, "\n")

        self.visualize_solution(solution)

    def visualize_problem(self):
        self.ax.clear()
        plot_problem(self.ax, self.errands, self.contractors)
        self.canvas.draw()

    def visualize_solution(self, solution):
        self.ax.clear()
        plot_solution(self.ax, solution)
        self.canvas.draw()

def main():
    root = tk.Tk()
    gui = SchedulerGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()