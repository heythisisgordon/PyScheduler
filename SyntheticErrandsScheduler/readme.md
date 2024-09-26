# Synthetic Errands Scheduling Optimizer

This project develops an advanced scheduling algorithm to maximize profit for Synthetic Errands Inc., a company operating a managed service with constrained resources.

## Project Overview

Synthetic Errands Inc. offers various errand services with guaranteed completion within 2 weeks. The challenge is to create an optimized scheduler that considers staff availability, supplier availability, errand fulfillment proximities, errand timing, and costs to maximize revenue.

## Key Features

- Multi-period scheduling (up to 2 weeks)
- Time windows for task completion
- Priority levels for tasks
- Routing optimization
- Handling of precedence constraints
- Dynamic scheduling for new job requests
- Modified Iterated Local Search (MILS) algorithm for optimization
- Graphical User Interface (GUI) for easy interaction and visualization

## Project Structure

The project is organized into several modules:

### Main Module
- `main.py`: Orchestrates the program's execution
- `run.py`: Launches the GUI (SchedulerGUI)

### Models
- `models/__init__.py`: Imports classes for key entities
- `contractor.py`: Defines individual contractor properties and methods
- `errand.py`: Defines the properties and behavior of an errand
- `location.py`: Handles geographic data of errand locations
- `schedule.py`: Manages the scheduling process for all resources

### Algorithms
- `algorithms/__init__.py`: Imports scheduling algorithms
- `initial_solution.py`: Generates an initial schedule using a greedy approach
- `local_search.py`: Optimizes the schedule locally for small improvements
- `mils.py`: Implements the main Modified Iterated Local Search (MILS) for optimization
- `perturbation.py`: Perturbs the current solution to escape local optima

### GUI
- `gui/__init__.py`: Imports the graphical components
- `scheduler_gui.py`: Implements the graphical user interface using tkinter
- `plot_utils.py`: Helps plot the schedule and problem visualizations

### Utilities
- `utils/__init__.py`: Imports utility functions
- `city_map.py`: Visualizes and interacts with the city map and routes

### Configuration
- `config.py`: Defines constants like grid size, work hours, etc.

## How to Run

1. Ensure you have Python installed on your system.
2. Navigate to the project directory.
3. Run the following command:

   ```
   python SyntheticErrandsScheduler\run.py
   ```

This will launch the GUI, allowing you to interact with the scheduler, generate problems, and visualize solutions.

## GUI Features

The Graphical User Interface (GUI) provides a user-friendly way to interact with the scheduler. Key features include:

1. Problem generation with customizable parameters (number of errands, contractors, and days).
2. Initial solution generation and visualization.
3. Optimization with adjustable algorithm settings.
4. Detailed results display, including:
   - Total revenue, costs, and profit for both initial and optimized solutions.
   - Improved display of SLA compliance rate and resource utilization percentages.
   - A table view for contractor schedules, showing transit start time, transit end time, errand start time, and errand end time for each errand.
5. Visualization of the problem setup and optimized solution.
6. Ability to edit initial conditions and re-run the optimization.

## Additional Information

- The project uses a Modified Iterated Local Search (MILS) algorithm for optimization, which combines local search with perturbation techniques to escape local optima.
- The GUI provides options to generate problems, create initial solutions, and solve problems with various parameters.
- Visualization tools are available to display both the problem setup and the optimized solution.

## Testing

Two test files are included:
- `test_initial_scheduler.py`: Tests the initial solution generation
- `test_scheduler.py`: Tests the overall scheduling algorithm

Run these tests to ensure the correctness of the scheduling algorithms.

## License

[License information]

For more detailed information about the project scope and user experience, refer to `project_scope.md` and `ux_overview.md` in the project directory.