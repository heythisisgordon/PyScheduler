from SyntheticErrandsScheduler.models.contractor import Contractor
from SyntheticErrandsScheduler.models.errand import Errand
from SyntheticErrandsScheduler.models.schedule import Schedule
from SyntheticErrandsScheduler.models.location import Location
from SyntheticErrandsScheduler.config import WORK_START, WORK_END
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time
from SyntheticErrandsScheduler.algorithms.initial_solution import generate_initial_solution
import logging

logging.basicConfig(level=logging.DEBUG)

def test_basic_scheduling():
    # Create contractors
    contractor1 = Contractor(contractor_id=1, start_location=Location(0, 0))
    contractor2 = Contractor(contractor_id=2, start_location=Location(50, 50))

    # Create errands
    errand1 = Errand(errand_id=1, errand_type='Delivery', location=Location(10, 10))
    errand2 = Errand(errand_id=2, errand_type='Dog Walk', location=Location(20, 20))
    errand3 = Errand(errand_id=3, errand_type='Detail Car', location=Location(30, 30))

    # Create a schedule
    schedule = Schedule(contractors=[contractor1, contractor2], errands=[errand1, errand2, errand3])

    # Generate initial solution
    final_schedule, stats = generate_initial_solution(schedule)

    # Print results
    print("Scheduling Results:")
    print(f"Total errands: {stats['total_errands']}")
    print(f"Assigned errands: {stats['assigned_errands']}")
    print(f"Unassigned errands: {len(final_schedule.unassigned_errands)}")
    print(f"Total profit: {stats['total_profit']}")
    print(f"SLA compliance: {stats['sla_compliance']:.2f}")
    print(f"Resource utilization: {stats['resource_utilization']:.2f}")

    # Print detailed schedule
    for day in range(final_schedule.num_days):
        print(f"\nDay {day + 1}:")
        for contractor in final_schedule.contractors:
            if day in contractor.schedule:
                print(f"  Contractor {contractor.id}:")
                for errand, start_time in contractor.schedule[day]:
                    print(f"    Errand {errand.id} ({errand.type}) at {start_time}")
            else:
                print(f"  Contractor {contractor.id}: No assignments")

if __name__ == "__main__":
    test_basic_scheduling()