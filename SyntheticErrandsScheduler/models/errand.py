import logging
from SyntheticErrandsScheduler.config import ERRANDS, PRIORITY_LEVELS, SLA_DAYS

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class Errand:
    def __init__(self, errand_id, errand_type, location, start_time=None, end_time=None, days_since_request=0, predecessors=None):
        """
        Initialize an Errand object.

        Args:
            errand_id (int): Unique identifier for the errand.
            errand_type (str): Type of the errand (must be a key in ERRANDS config).
            location (Location): Location of the errand.
            start_time (int, optional): Start time of the errand's time window.
            end_time (int, optional): End time of the errand's time window.
            days_since_request (int, optional): Number of days since the errand was requested.
            predecessors (set, optional): Set of Errand objects that must be completed before this one.
        """
        logger.debug(f"Initializing Errand with ID: {errand_id}, Type: {errand_type}")
        self.id = errand_id
        self.type = errand_type
        self.location = location
        self.start_time = start_time
        self.end_time = end_time
        self.days_since_request = days_since_request
        self.predecessors = predecessors or set()

        if errand_type not in ERRANDS:
            raise ValueError(f"Invalid errand type: {errand_type}")
        
        self.details = ERRANDS[errand_type]
        logger.debug(f"Errand {self.id} initialized successfully")

    @property
    def charge(self):
        return self.details['charge']

    @property
    def service_time(self):
        return self.details['time']

    @property
    def priority(self):
        return self.details['priority']

    @property
    def priority_level(self):
        return PRIORITY_LEVELS[self.priority]

    def calculate_profit(self, day, sla_days=SLA_DAYS):
        """
        Calculate the profit for this errand based on the day it's scheduled.

        Args:
            day (int): The day the errand is scheduled.
            sla_days (int): The number of days in the Service Level Agreement.

        Returns:
            float: The calculated profit.
        """
        logger.debug(f"Calculating profit for Errand {self.id} on day {day}")
        base_profit = self.charge
        days_until_due = sla_days - self.days_since_request

        if day <= days_until_due:
            # Early completion bonus
            early_days = days_until_due - day
            early_bonus = self.details['early_incentive'] * early_days
            profit = base_profit + early_bonus
        else:
            # Late penalty
            late_days = day - days_until_due
            late_penalty = self.details['late_penalty'] * late_days * base_profit
            profit = max(0, base_profit - late_penalty)  # Ensure profit doesn't go negative

        logger.debug(f"Calculated profit for Errand {self.id}: {profit}")
        return profit

    def are_predecessors_completed(self, completed_errands):
        """
        Check if all predecessors of this errand have been completed.

        Args:
            completed_errands (set): Set of completed Errand objects.

        Returns:
            bool: True if all predecessors are completed, False otherwise.
        """
        return all(predecessor in completed_errands for predecessor in self.predecessors)

    def __str__(self):
        return f"Errand {self.id} ({self.type}, Priority: {self.priority_level}) at {self.location}"

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        if not isinstance(other, Errand):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(self.id)

logger.debug("Errand class defined successfully")