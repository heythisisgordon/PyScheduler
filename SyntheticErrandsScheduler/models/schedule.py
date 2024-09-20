from SyntheticErrandsScheduler.config import WORK_START, WORK_END, MAX_DAYS
from SyntheticErrandsScheduler.utils.travel_time import calculate_travel_time

class Schedule:
    def __init__(self, contractors, errands):
        """
        Initialize a Schedule object.

        Args:
            contractors (list): List of Contractor objects.
            errands (list): List of Errand objects.
        """
        self.contractors = contractors
        self.errands = errands
        self.unassigned_errands = set(errands)
        self.assignments = {d: [] for d in range(MAX_DAYS)}

    def assign_errand(self, contractor, errand, day, start_time):
        """
        Assign an errand to a contractor on a specific day and time.

        Args:
            contractor (Contractor): The contractor to assign the errand to.
            errand (Errand): The errand to be assigned.
            day (int): The day of the assignment.
            start_time (int): The start time of the errand in minutes.
        """
        travel_time = calculate_travel_time(contractor.current_location, errand.location)
        if contractor.can_perform_errand(errand, start_time, travel_time):
            contractor.assign_errand(day, errand, start_time + travel_time)
            self.assignments[day].append((errand, contractor, start_time + travel_time))
            self.unassigned_errands.remove(errand)
            return True
        return False

    def remove_assignment(self, day, assignment):
        """
        Remove an assignment from the schedule.

        Args:
            day (int): The day of the assignment.
            assignment (tuple): The (errand, contractor, start_time) tuple to remove.
        """
        if assignment in self.assignments[day]:
            self.assignments[day].remove(assignment)
            errand, contractor, _ = assignment
            contractor.schedule[day] = [a for a in contractor.schedule[day] if a[0] != errand]
            self.unassigned_errands.add(errand)

    def calculate_total_profit(self):
        """
        Calculate the total profit for the current schedule.

        Returns:
            float: The total profit.
        """
        total_profit = 0
        for day in range(MAX_DAYS):
            for errand, _, _ in self.assignments[day]:
                total_profit += errand.calculate_profit(day, MAX_DAYS)
        return total_profit

    def is_valid(self):
        """
        Check if the current schedule is valid.

        Returns:
            bool: True if the schedule is valid, False otherwise.
        """
        for day in range(MAX_DAYS):
            for contractor in self.contractors:
                last_end_time = WORK_START
                for errand, start_time in contractor.schedule.get(day, []):
                    travel_time = calculate_travel_time(contractor.current_location, errand.location)
                    if start_time < last_end_time + travel_time or start_time + errand.service_time > WORK_END:
                        return False
                    last_end_time = start_time + errand.service_time
                    contractor.current_location = errand.location
                contractor.reset_day()
        return True

    def get_unassigned_errands(self):
        """
        Get the list of unassigned errands.

        Returns:
            list: List of unassigned Errand objects.
        """
        return list(self.unassigned_errands)

    def __str__(self):
        return f"Schedule with {len(self.contractors)} contractors and {len(self.errands)} errands"

    def __repr__(self):
        return self.__str__()