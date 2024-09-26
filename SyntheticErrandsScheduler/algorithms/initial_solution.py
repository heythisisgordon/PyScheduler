import logging
from SyntheticErrandsScheduler.config import WORK_START, WORK_END, MAX_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

logging.basicConfig(level=logging.DEBUG)

def calculate_contractor_workload(contractor):
    return sum(
        sum(errand.service_time for errand, _ in day_schedule)
        for day_schedule in contractor.schedule.values()
    )

def find_next_available_time(contractor, day, current_time):
    if day not in contractor.schedule:
        return current_time

    day_schedule = sorted(contractor.schedule[day], key=lambda x: x[1])
    for scheduled_errand, start_time in day_schedule:
        if current_time < start_time:
            return current_time
        current_time = max(current_time, start_time + scheduled_errand.service_time)

    return current_time

def generate_initial_solution(schedule):
    logging.info("Generating initial solution")
    
    # Sort errands by priority (higher priority first) and then by service time (longer first)
    sorted_errands = sorted(schedule.unassigned_errands, key=lambda e: (-e.priority, -e.service_time))
    
    for day in range(MAX_DAYS):
        # Sort contractors by their current workload (least busy first)
        sorted_contractors = sorted(schedule.contractors, key=calculate_contractor_workload)
        
        for contractor in sorted_contractors:
            contractor.reset_day()
            current_time = WORK_START
            
            while current_time < WORK_END and sorted_errands:
                for errand in sorted_errands[:]:
                    travel_time = calculate_travel_time(contractor.current_location, errand.location)
                    start_time = find_next_available_time(contractor, day, current_time)
                    end_time = start_time + travel_time + errand.service_time
                    
                    if end_time <= WORK_END:
                        if schedule.assign_errand(contractor, errand, day, start_time + travel_time):
                            sorted_errands.remove(errand)
                            current_time = end_time
                            logging.info(f"Assigned errand {errand.id} to contractor {contractor.id} on day {day}")
                            break
                    elif start_time + travel_time < WORK_END:
                        # Handle long-duration errands by splitting them across multiple days
                        remaining_time = WORK_END - (start_time + travel_time)
                        if schedule.assign_errand(contractor, errand, day, start_time + travel_time):
                            errand.service_time -= remaining_time
                            logging.info(f"Partially assigned errand {errand.id} to contractor {contractor.id} on day {day}")
                            current_time = WORK_END
                            break
                else:
                    # If no errand could be assigned, move to the next contractor
                    break
    
    # Try to assign any remaining errands on the last day, even if they exceed working hours
    if sorted_errands:
        last_day = MAX_DAYS - 1
        for contractor in schedule.contractors:
            current_time = WORK_START
            for errand in sorted_errands[:]:
                if schedule.assign_errand(contractor, errand, last_day, current_time):
                    sorted_errands.remove(errand)
                    current_time += errand.service_time
                    logging.info(f"Assigned remaining errand {errand.id} to contractor {contractor.id} on last day")
    
    # Log any remaining unassigned errands
    for errand in sorted_errands:
        logging.warning(f"Failed to assign errand {errand.id}")
    
    logging.info(f"Initial solution generated with {len(sorted_errands)} unassigned errands")
    
    stats = {
        "assigned_errands": len(schedule.errands) - len(sorted_errands),
        "total_errands": len(schedule.errands),
        "total_profit": schedule.calculate_total_profit(),
        "sla_compliance": schedule.calculate_sla_compliance(),
        "resource_utilization": schedule.calculate_resource_utilization()
    }
        
    return schedule, stats