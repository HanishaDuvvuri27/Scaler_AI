"""Utility functions for date generation with realistic patterns."""

import random
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz
from scipy import stats
import numpy as np


class DateGenerator:
    """Generates realistic dates for tasks based on distribution patterns."""
    
    @staticmethod
    def generate_due_date(start_date, end_date, project_type='general', completion_rate=None):
        """
        Generate a realistic due date for a task.
        
        Distribution based on Asana research:
        - 25% within 1 week
        - 40% within 1 month
        - 20% 1-3 months out
        - 10% no due date
        - 5% overdue
        """
        rand = random.random()
        
        if rand < 0.10:
            return None  # No due date
        
        base_date = datetime.now()
        
        if rand < 0.35:  # Within 1 week (25% + 10% offset)
            days_out = random.randint(1, 7)
            due_date = base_date + timedelta(days=days_out)
        elif rand < 0.75:  # Within 1 month (40% cumulative)
            days_out = random.randint(8, 30)
            due_date = base_date + timedelta(days=days_out)
        elif rand < 0.95:  # 1-3 months (20% cumulative)
            days_out = random.randint(31, 90)
            due_date = base_date + timedelta(days=days_out)
        else:  # Overdue (5% cumulative)
            days_back = random.randint(1, 30)
            due_date = base_date - timedelta(days=days_back)
        
        # Avoid weekends for 85% of tasks
        if random.random() < 0.85:
            while due_date.weekday() in [5, 6]:  # 5=Saturday, 6=Sunday
                due_date += timedelta(days=1)
        
        # Cluster around sprint boundaries (end of sprint) for engineering projects
        if project_type == 'sprint' and random.random() < 0.40:
            # Align with typical 2-week sprint boundaries
            days_until_friday = (4 - due_date.weekday()) % 7
            if days_until_friday == 0:
                days_until_friday = 7
            due_date = due_date + timedelta(days=days_until_friday)
        
        # Ensure due date is within simulation range and after creation
        if due_date < start_date:
            due_date = start_date + timedelta(days=random.randint(1, 30))
        if due_date > end_date:
            due_date = end_date - timedelta(days=random.randint(1, 30))
        
        return due_date.date()
    
    @staticmethod
    def generate_created_at(start_date, end_date):
        """
        Generate a creation timestamp with realistic temporal patterns.
        
        Higher creation rates Mon-Wed, lower Thu-Fri.
        Follows company's 6-month history with growth curve.
        """
        # Generate date within range
        time_range = (end_date - start_date).days
        random_days = random.randint(0, time_range)
        created_date = start_date + timedelta(days=random_days)
        
        # Apply day-of-week weighting (more creation Mon-Wed)
        day_weights = {
            0: 1.2,  # Monday
            1: 1.2,  # Tuesday
            2: 1.1,  # Wednesday
            3: 0.9,  # Thursday
            4: 0.8,  # Friday
            5: 0.5,  # Saturday
            6: 0.3   # Sunday
        }
        
        # Adjust probability to match distribution
        # This is approximated by potentially shifting the date
        day_of_week = created_date.weekday()
        if random.random() > day_weights[day_of_week] / 1.2:
            # Shift to a more likely day
            shift_days = random.choice([1, -1, 2, -2])
            created_date = created_date + timedelta(days=shift_days)
            # Ensure still in range
            created_date = max(start_date, min(end_date, created_date))
        
        # Add random time during business hours
        hour = random.randint(9, 17)
        minute = random.randint(0, 59)
        second = random.randint(0, 59)
        
        created_at = datetime.combine(created_date.date(), 
                                     datetime.min.time()).replace(
                                         hour=hour, minute=minute, second=second)
        
        return created_at
    
    @staticmethod
    def generate_completed_at(created_at, project_type='general'):
        """
        Generate completion timestamp if task is completed.
        
        Follows log-normal distribution:
        - Most tasks completed 1-7 days after creation
        - Some take up to 14 days
        - Distribution varies by project type
        """
        if project_type == 'sprint':
            max_days = 14
        elif project_type == 'bug':
            max_days = 21
        else:
            max_days = 30
        
        # Use log-normal distribution for completion time
        # This creates more tasks completed quickly, with a tail of long-running tasks
        shape = 1.2
        scale = 2.0
        days_to_complete = np.random.lognormal(mean=np.log(scale), sigma=shape)
        days_to_complete = min(int(days_to_complete), max_days)
        
        completed_at = created_at + timedelta(days=days_to_complete)
        return completed_at
    
    @staticmethod
    def generate_task_creation_pattern(start_date, end_date, task_count):
        """
        Generate realistic task creation dates following growth curve.
        Returns a list of timestamps distributed realistically.
        """
        creation_dates = []
        total_days = (end_date - start_date).days
        
        for i in range(task_count):
            # Generate with growth curve (more tasks created as time progresses)
            # Use exponential-like growth
            random_val = random.random()
            # Apply power function to skew towards later dates
            growth_factor = random_val ** 0.6  # Skew towards recent dates
            days_offset = int(total_days * growth_factor)
            
            created_date = start_date + timedelta(days=days_offset)
            created_at = DateGenerator.generate_created_at(start_date, end_date)
            creation_dates.append(created_at)
        
        return sorted(creation_dates)


class TimeValidator:
    """Validates temporal consistency of generated data."""
    
    @staticmethod
    def validate_task_dates(created_at, due_date, completed_at):
        """Ensure task date constraints are maintained."""
        if due_date and due_date < created_at.date():
            return False, "Due date before creation date"
        
        if completed_at and completed_at < created_at:
            return False, "Completed before creation"
        
        if due_date and completed_at and completed_at.date() > due_date:
            return False, "Completed after due date (acceptable but unusual)"
        
        return True, "Valid"
