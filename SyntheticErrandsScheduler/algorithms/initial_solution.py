import random
import logging  # This is needed to enable logging in this file
logging.basicConfig(level=logging.DEBUG)  # This sets the logging level to DEBUG

from SyntheticErrandsScheduler.config import WORK_START, WORK_END, MAX_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

def generate_initial_solution(schedule):
    logging.info("Generating initial solution")
    for day in range(MAX_DAYS):
        available_errands = list(schedule.unassigned_errands)
        random.shuffle(available_errands)

        for errand in available_errands[:]:
            assigned = False
            for contractor in schedule.contractors:
                current_time = contractor.get_end_time(day)
                travel_time = calculate_travel_time(contractor.current_location, errand.location)
                arrival_time = current_time + travel_time
                
                logging.debug(f"Day {day}: Attempting to assign errand {errand.id} to contractor {contractor.id}")
                logging.debug(f"Current time: {current_time}, Travel time: {travel_time}, Service time: {errand.service_time}")
                logging.debug(f"Contractor {contractor.id} available until: {WORK_END}, Arrival time: {arrival_time}")

                if arrival_time + errand.service_time <= WORK_END:
                    if schedule.assign_errand(contractor, errand, day, current_time):
                        assigned = True
                        available_errands.remove(errand)
                        logging.info(f"Assigned errand {errand.id} to contractor {contractor.id} on day {day}")
                        break
            
            if not assigned:
                logging.debug(f"Could not assign errand {errand.id} on day {day}")

    logging.info(f"Initial solution generated with {len(schedule.unassigned_errands)} unassigned errands")
    return schedule