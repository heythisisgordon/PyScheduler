import logging
from SyntheticErrandsScheduler.models.location import Location
from SyntheticErrandsScheduler.config import WORK_START, WORK_END

class Contractor:
    def __init__(self, contractor_id, start_location):
        self.id = contractor_id
        self.start_location = start_location
        self.current_location = start_location
        self.schedule = {}  # Dictionary to store the contractor's schedule

    def reset_day(self):
        """Reset the contractor's location for a new day."""
        self.current_location = self.start_location

    def get_end_time(self, day):
        if day not in self.schedule or not self.schedule[day]:
            return WORK_START
        last_errand, last_start_time = self.schedule[day][-1]
        return min(last_start_time + last_errand.service_time, WORK_END)

    def assign_errand(self, day, errand, start_time):
        """
        Assign an errand to the contractor's schedule.

        Args:
            day (int): The day of the assignment.
            errand (Errand): The errand to be assigned.
            start_time (int): The start time of the errand in minutes.
        """
        if day not in self.schedule:
            self.schedule[day] = []
        
        end_time = start_time + errand.service_time
        if end_time > WORK_END:
            logging.warning(f"Errand {errand.id} extends beyond work hours for contractor {self.id} on day {day}")
        
        self.schedule[day].append((errand, start_time))
        self.current_location = errand.location
        logging.debug(f"Assigned errand {errand.id} to contractor {self.id} on day {day} at {start_time}")

    def __str__(self):
        return f"Contractor {self.id} at {self.current_location}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Contractor):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)