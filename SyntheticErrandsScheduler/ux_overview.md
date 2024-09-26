# User Experience Overview: Synthetic Errands Scheduling Optimizer

## Project Purpose
This UX design is tailored for an academic Capstone project aimed at studying and demonstrating solutions to the Synthetic Errands scheduling problem. The interface is designed to allow students, professors, and the project customer (Synthetic Errands Inc.) to interact with, analyze, and understand the developed scheduling algorithms.

## Key User Personas

1. Student Researchers: Members of the Capstone project team who need to configure, run, and analyze experiments.
2. Academic Advisor: Professor overseeing the project who needs to evaluate the approach and results.
3. Industry Sponsor: Representatives from Synthetic Errands Inc. who want to understand the potential real-world application.

## Main Interface Components

### 1. Configuration Panel

- Problem Instance Generation:
  - Input fields for number of errands, contractors, and days
  - Option to generate a new problem instance

- Algorithm Parameters:
  - Input fields for key algorithm parameters (e.g., max iterations, max time, temperature, cooling rate, number of runs)

### 2. Execution Control

- "Generate Problem" button to create a new problem instance based on the input parameters
- "Generate Initial Solution" button to create a starting point using a greedy algorithm
- "Solve" button to run the Modified Iterated Local Search (MILS) algorithm for optimization
- "Edit" button to modify the initial conditions of the problem

### 3. Results Dashboard

- Initial Solution Tab:
  - Total revenue, costs, and profit
  - SLA compliance rate
  - Resource utilization percentages
  - Table of contractor schedules listing errands performed each day for each contractor. Includes transit start time, transit end time, errand start time, and errand end time for each errand.

- Optimized Solution Tab:
  - Total revenue, costs, and profit
  - SLA compliance rate
  - Resource utilization percentages
  - Table of contractor schedules listing errands performed each day for each contractor. Includes transit start time, transit end time, errand start time, and errand end time for each errand.

- Visualization Tab:
  - Graphical representation of the problem setup and optimized solution
  - Visual display of contractor routes and errand locations

- Details Tab:
  - Detailed breakdown of the schedule for each day and contractor

- Problem Parameters Tab:
  - Table providing details of the generated problem, including errand types, locations, and contractor information

### 4. Initial Conditions Editor

- Text area for displaying and editing the initial problem conditions
- Ability to modify errand types, locations, and contractor starting positions

### 5. Progress Indicator

- Progress bar to show the status of problem generation, initial solution creation, and optimization processes

This user interface provides a comprehensive environment for generating, solving, and analyzing Synthetic Errands scheduling problems. It allows users to interact with the algorithm, visualize results, and gain insights into the optimization process.