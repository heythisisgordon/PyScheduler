from SyntheticErrandsScheduler.config import WORK_START, WORK_END, MAX_DAYS, SLA_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time
import logging

logging.basicConfig(level=logging.DEBUG)

class Schedule:
    def __init__(self, contractors, errands):
        self.contractors = contractors
        self.errands = errands
        self.unassigned_errands = set(errands)
        self.completed_errands = set()
        self.assignments = {d: [] for d in range(MAX_DAYS)}
        self.total_profit = 0

    @property
    def num_days(self):
        return MAX_DAYS

    def can_assign_errand(self, contractor, errand, day, start_time):
        if errand not in self.unassigned_errands:
            return False
        
        if not errand.are_predecessors_completed(self.completed_errands):
            return False

        travel_time = calculate_travel_time(contractor.current_location, errand.location)
        arrival_time = start_time + travel_time
        end_time = arrival_time + errand.service_time

        return end_time <= WORK_END or day == MAX_DAYS - 1  # Allow overflow on the last day

    def assign_errand(self, contractor, errand, day, start_time):
        try:
            logging.debug(f"Trying to assign errand {errand.id} to contractor {contractor.id} on day {day} at {start_time}")

            if self.can_assign_errand(contractor, errand, day, start_time):
                travel_time = calculate_travel_time(contractor.current_location, errand.location)
                arrival_time = start_time + travel_time

                contractor.assign_errand(day, errand, arrival_time)
                self.assignments[day].append((errand, contractor, arrival_time))
                self.unassigned_errands.remove(errand)
                self.completed_errands.add(errand)
                self.total_profit += errand.charge
                logging.debug(f"Successfully assigned errand {errand.id} to contractor {contractor.id}")
                return True
            else:
                logging.debug(f"Cannot perform errand {errand.id}: Time conflict or predecessors not completed")
        except Exception as e:
            logging.error(f"Error assigning errand {errand.id}: {str(e)}")
        return False

    def calculate_total_profit(self):
        return sum(errand.charge for day in self.assignments for errand, _, _ in self.assignments[day])

    def calculate_sla_compliance(self):
        total_errands = len(self.errands)
        completed_errands = len(self.completed_errands)
        return completed_errands / total_errands if total_errands > 0 else 1.0

    def calculate_resource_utilization(self):
        total_work_time = (WORK_END - WORK_START) * MAX_DAYS * len(self.contractors)
        used_time = sum(
            min(errand.service_time, WORK_END - start_time)  # Cap at WORK_END
            for day in self.assignments
            for errand, _, start_time in self.assignments[day]
        )
        return used_time / total_work_time if total_work_time > 0 else 0.0

    def get_unassigned_errands(self):
        return list(self.unassigned_errands)

    def __str__(self):
        return f"Schedule with {len(self.contractors)} contractors and {len(self.errands)} errands"

    def __repr__(self):
        return self.__str__()

    def print_schedule(self):
        for day in range(MAX_DAYS):
            print(f"Day {day + 1}:")
            for errand, contractor, start_time in self.assignments[day]:
                end_time = start_time + errand.service_time
                print(f"  Contractor {contractor.id}: Errand {errand.id} ({start_time} - {end_time})")
            print()

    def get_contractor_schedule(self, contractor_id):
        schedule = []
        for day in range(MAX_DAYS):
            day_schedule = [
                (errand, start_time)
                for errand, cont, start_time in self.assignments[day]
                if cont.id == contractor_id
            ]
            schedule.append(day_schedule)
        return schedule