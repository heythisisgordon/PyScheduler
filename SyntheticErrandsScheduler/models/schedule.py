from SyntheticErrandsScheduler.config import WORK_START, WORK_END, MAX_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time
import copy
import logging  # This is needed to enable logging in this file
logging.basicConfig(level=logging.DEBUG)  # This sets the logging level to DEBUG

class Schedule:
    def __init__(self, contractors, errands):
        self.contractors = contractors
        self.errands = errands
        self.unassigned_errands = set(errands)
        self.assignments = {d: [] for d in range(MAX_DAYS)}
        self.total_profit = 0

    @property
    def num_days(self):
        return MAX_DAYS

    def assign_errand(self, contractor, errand, day, start_time):
        try:
            travel_time = calculate_travel_time(contractor.current_location, errand.location)
            
            logging.debug(f"Trying to assign errand {errand.id} to contractor {contractor.id} on day {day} at {start_time}")

            if contractor.can_perform_errand(errand, start_time, travel_time):
                contractor.assign_errand(day, errand, start_time + travel_time)
                self.assignments[day].append((errand, contractor, start_time + travel_time))
                if errand in self.unassigned_errands:
                    self.unassigned_errands.remove(errand)
                self.total_profit += errand.calculate_profit(day, MAX_DAYS)
                logging.debug(f"Successfully assigned errand {errand.id} to contractor {contractor.id}")
                return True
            else:
                logging.debug(f"Cannot perform errand {errand.id}: Time constraint violation")
        except Exception as e:
            logging.error(f"Error assigning errand {errand.id}: {str(e)}")
        return False

    def remove_assignment(self, day, assignment):
        if assignment in self.assignments[day]:
            self.assignments[day].remove(assignment)
            errand, contractor, _ = assignment
            contractor.schedule[day] = [a for a in contractor.schedule[day] if a[0] != errand]
            self.unassigned_errands.add(errand)
            self.total_profit -= errand.calculate_profit(day, MAX_DAYS)

    def calculate_total_profit(self):
        total_profit = 0
        for day in range(MAX_DAYS):
            for errand, _, _ in self.assignments[day]:
                total_profit += errand.calculate_profit(day, MAX_DAYS)
        self.total_profit = total_profit
        return total_profit

    def is_valid(self):
        for day in range(MAX_DAYS):
            for contractor in self.contractors:
                if day in contractor.schedule:
                    last_end_time = WORK_START
                    for errand, start_time in contractor.schedule[day]:
                        travel_time = calculate_travel_time(contractor.current_location, errand.location)
                        if start_time < last_end_time + travel_time or start_time + errand.service_time > WORK_END:
                            return False
                        last_end_time = start_time + errand.service_time
                        contractor.current_location = errand.location
                contractor.reset_day()
        return True

    def get_unassigned_errands(self):
        return list(self.unassigned_errands)

    def __str__(self):
        return f"Schedule with {len(self.contractors)} contractors and {len(self.errands)} errands"

    def __repr__(self):
        return self.__str__()