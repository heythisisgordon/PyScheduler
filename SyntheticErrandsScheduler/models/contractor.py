import logging
from SyntheticErrandsScheduler.models.location import Location
from SyntheticErrandsScheduler.config import WORK_START, WORK_END

class Contractor:
    def __init__(self, contractor_id, start_location):
        """
        Initialize a Contractor object.

        Args:
            contractor_id (int): Unique identifier for the contractor.
            start_location (Location): Starting location of the contractor.
        """
        self.id = contractor_id
        self.start_location = start_location
        self.current_location = start_location
        self.schedule = {}  # Dictionary to store the contractor's schedule

    def reset_day(self):
        """Reset the contractor's location and available time for a new day."""
        self.current_location = self.start_location

    def get_end_time(self, day):
        if day not in self.schedule or not self.schedule[day]:
            return WORK_START
        last_errand, last_start_time = self.schedule[day][-1]
        return last_start_time + last_errand.service_time
    
    def can_perform_errand(self, errand, current_time, travel_time):
        """
        Check if the contractor can perform the given errand.

        Args:
            errand (Errand): The errand to be performed.
            current_time (int): The current time in minutes.
            travel_time (int): The time to travel to the errand location.

        Returns:
            bool: True if the contractor can perform the errand, False otherwise.
        """
        arrival_time = current_time + travel_time
        completion_time = arrival_time + errand.service_time

        logging.debug(f"Contractor {self.id}: Current time: {current_time}, Arrival time: {arrival_time}, Completion time: {completion_time}")

        if completion_time > WORK_END:
            logging.debug(f"Contractor {self.id}: Cannot perform errand {errand.id}. Completion time {completion_time} exceeds work end time {WORK_END}")
            return False

        # Check for conflicts with existing assignments
        for day, assignments in self.schedule.items():
            for assigned_errand, assigned_start_time in assignments:
                if assigned_start_time <= completion_time and current_time <= assigned_start_time + assigned_errand.service_time:
                    logging.debug(f"Contractor {self.id}: Cannot perform errand {errand.id}. Conflict with existing assignment {assigned_errand.id}")
                    return False

        return True

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
        
        self.schedule[day].append((errand, start_time))
        self.current_location = errand.location

    def get_end_time(self, day):
        """
        Get the end time of the contractor's last errand for the given day.

        Args:
            day (int): The day to check.

        Returns:
            int: The end time of the last errand, or WORK_START if no errands are scheduled.
        """
        if day not in self.schedule or not self.schedule[day]:
            return WORK_START
        
        last_errand, last_start_time = self.schedule[day][-1]
        return last_start_time + last_errand.service_time

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