# Project Scope: Synthetic Errands Scheduling Optimizer

## Objective

Develop a scheduling algorithm for Synthetic Errands Inc. that maximizes revenue while satisfying all constraints and service level agreements.

## Problem Definition

- Implement an advanced algorithm that outperforms the current greedy algorithm
- Schedule 1 to 10 errands per customer
- Guaranteed completion date of 2 weeks from request, per service-level agreement
- Primary scheduling goal is to maximize profit
- Flat fee for each errand
- Incentives for early completion
- Penalties for late completion that violates the service-level agreement
- Appointments should be scheduled as soon as possible
- Optimizer and its algorithms need to run in a reasonable timeframe on a consumer laptop

## Constraints

1. Manhattan distance used to traverse city
2. Time windows
3. (deprecated, ignore)
4. Precedence relationships
5. Priority levels
6. Resource availability
7. Travel time and routing
8. Tools and spare parts availability

## Deliverables

1. Mathematical model of the problem
2. Scheduling program with GUI to:
   - Configure initial conditions (number of errands, contractors, and days)
   - Run solver (Modified Iterated Local Search algorithm)
   - View and compare initial and optimized solutions
   - Display detailed statistics (total revenue, costs, profit, SLA compliance, resource utilization)
   - Visualize problem setup and optimized solution
   - Edit initial conditions and re-run optimization

## Success Criteria

- All errands completed within 2-week SLA
- Profit maximized (considering incentives and discounts)
- SLA compliance
- Enhanced resource utilization
- User-friendly GUI for easy interaction and result analysis

## Algorithm

- Include an initial solution generator using a greedy approach
- Implement a Modified Iterated Local Search (MILS) algorithm for optimization
- Incorporate local search and perturbation techniques to escape local optima

## Out of Scope

- Real-time traffic updates
- Long-term workforce planning

## GUI Features

- Problem generation with customizable parameters
- Initial solution generation and visualization
- Optimization with adjustable algorithm settings
- Detailed results display, including:
  - Total revenue, costs, and profit for both initial and optimized solutions
  - SLA compliance rate and resource utilization percentages
  - Table view for contractor schedules
- Visualization of problem setup and optimized solution
- Ability to edit initial conditions and re-run optimization