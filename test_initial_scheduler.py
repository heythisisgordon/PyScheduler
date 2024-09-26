import random
from SyntheticErrandsScheduler.models.errand import Errand
from SyntheticErrandsScheduler.models.contractor import Contractor
from SyntheticErrandsScheduler.models.schedule import Schedule
from SyntheticErrandsScheduler.algorithms.initial_solution import generate_initial_solution
from SyntheticErrandsScheduler.utils import city_map
from SyntheticErrandsScheduler.config import GRID_SIZE, WORK_START, WORK_END, MAX_DAYS, ERRANDS
from SyntheticErrandsScheduler.models.location import Location

def generate_test_data(num_errands, num_contractors):
    errands = []
    for i in range(num_errands):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        location = Location(x, y)
        errand_type = random.choice(list(ERRANDS.keys()))
        errands.append(Errand(f"Errand_{i}", errand_type, location))
    
    contractors = []
    for i in range(num_contractors):
        x, y = random.randint(0, GRID_SIZE-1), random.randint(0, GRID_SIZE-1)
        location = Location(x, y)
        contractors.append(Contractor(f"Contractor_{i}", location))
    
    return errands, contractors

def print_detailed_schedule(schedule):
    print("\nDetailed Schedule:")
    for day in range(MAX_DAYS):
        print(f"Day {day + 1}:")
        day_assignments = schedule.assignments[day]
        if not day_assignments:
            print("  No errands scheduled")
        else:
            for errand, contractor, start_time in day_assignments:
                end_time = start_time + errand.service_time
                print(f"  Contractor {contractor.id}: Errand {errand.id} ({errand.type}) - Start: {start_time}, End: {end_time}")
        print()

def test_initial_scheduler(num_errands, num_contractors):
    errands, contractors = generate_test_data(num_errands, num_contractors)
    schedule = Schedule(contractors, errands)
    
    result_schedule, stats = generate_initial_solution(schedule)
    
    print(f"Test case: {num_errands} errands, {num_contractors} contractors, {MAX_DAYS} days")
    print("Schedule results:")
    
    total_assigned = stats["assigned_errands"]
    total_errands = stats["total_errands"]
    total_profit = stats["total_profit"]
    sla_compliance = stats["sla_compliance"]
    resource_utilization = stats["resource_utilization"]
    
    print(f"\nTotal assigned errands: {total_assigned}/{total_errands}")
    print(f"Total profit: ${total_profit:.2f}")
    print(f"SLA compliance: {sla_compliance:.2%}")
    print(f"Resource utilization: {resource_utilization:.2%}")
    
    unassigned = result_schedule.unassigned_errands
    print(f"\nUnassigned errands: {len(unassigned)}")
    
    if unassigned:
        print("Unassigned errands details:")
        for errand in unassigned:
            print(f"  {errand.id} (Type: {errand.type}, Duration: {errand.service_time} minutes, Priority: {errand.priority})")
    
    print_detailed_schedule(result_schedule)
    
    # Check for overlapping errands
    overlaps = check_for_overlaps(result_schedule)
    if overlaps:
        print("\nWarning: Overlapping errands detected:")
        for overlap in overlaps:
            print(f"  Day {overlap['day']}, Contractor {overlap['contractor']}: {overlap['errand1']} overlaps with {overlap['errand2']}")
    
    return len(unassigned) == 0 and not overlaps

def check_for_overlaps(schedule):
    overlaps = []
    for day in range(MAX_DAYS):
        for contractor in schedule.contractors:
            contractor_schedule = sorted(
                [(errand, start_time) for errand, cont, start_time in schedule.assignments[day] if cont == contractor],
                key=lambda x: x[1]
            )
            for i in range(len(contractor_schedule) - 1):
                errand1, start1 = contractor_schedule[i]
                errand2, start2 = contractor_schedule[i + 1]
                end1 = start1 + errand1.service_time
                if end1 > start2:
                    overlaps.append({
                        'day': day,
                        'contractor': contractor.id,
                        'errand1': errand1.id,
                        'errand2': errand2.id
                    })
    return overlaps

if __name__ == "__main__":
    num_errands = 10
    num_contractors = 2
    
    success = test_initial_scheduler(num_errands, num_contractors)
    
    if success:
        print("\nTest passed: All errands were successfully scheduled without overlaps.")
    else:
        print("\nTest failed: Some errands were left unscheduled or there were overlapping assignments.")