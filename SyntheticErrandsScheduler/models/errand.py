from SyntheticErrandsScheduler.config import ERRANDS
from SyntheticErrandsScheduler.models.location import Location

class Errand:
    def __init__(self, errand_id, errand_type, location):
        """
        Initialize an Errand object.

        Args:
            errand_id (int): Unique identifier for the errand.
            errand_type (str): Type of the errand (must be a key in ERRANDS config).
            location (Location): Location of the errand.
        """
        self.id = errand_id
        self.type = errand_type
        self.location = location

        if errand_type not in ERRANDS:
            raise ValueError(f"Invalid errand type: {errand_type}")
        
        self.details = ERRANDS[errand_type]

    @property
    def charge(self):
        return self.details['charge']

    @property
    def service_time(self):
        return self.details['time']

    @property
    def home_required(self):
        return self.details['home_required']

    @property
    def early_incentive(self):
        return self.details['early_incentive']

    @property
    def late_penalty(self):
        return self.details['late_penalty']

    def calculate_profit(self, day_completed, total_days):
        """
        Calculate the profit for this errand based on when it's completed.

        Args:
            day_completed (int): The day the errand is completed (0-indexed).
            total_days (int): Total number of days in the scheduling period.

        Returns:
            float: The profit for this errand.
        """
        profit = self.charge

        if day_completed < total_days:
            # Early completion bonus
            profit += self.early_incentive * (total_days - day_completed - 1)
        elif day_completed > total_days:
            # Late completion penalty
            profit -= self.late_penalty * (day_completed - total_days)

        return max(profit, 0)  # Ensure profit is not negative

    def __str__(self):
        return f"Errand {self.id} ({self.type}) at {self.location}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Errand):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)