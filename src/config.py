"""Configuration management for the Asana seed data generator."""

import os
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()


class Config:
    """Global configuration settings."""
    
    # API Configuration
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
    ANTHROPIC_API_KEY = os.getenv('ANTHROPIC_API_KEY', '')
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openai')
    LLM_MODEL = os.getenv('LLM_MODEL', 'gpt-3.5-turbo')
    
    # Data Generation Configuration
    ORGANIZATION_COUNT = int(os.getenv('ORGANIZATION_COUNT', 1))
    TEAM_COUNT = int(os.getenv('TEAM_COUNT', 15))
    USER_COUNT = int(os.getenv('USER_COUNT', 200))
    PROJECT_COUNT = int(os.getenv('PROJECT_COUNT', 45))
    TASK_COUNT = int(os.getenv('TASK_COUNT', 5000))
    SUBTASK_COUNT = int(os.getenv('SUBTASK_COUNT', 2000))
    COMMENT_COUNT = int(os.getenv('COMMENT_COUNT', 3000))
    
    # Date Range Configuration
    SIMULATION_START_DATE = datetime.strptime(
        os.getenv('SIMULATION_START_DATE', '2023-07-01'), '%Y-%m-%d'
    )
    SIMULATION_END_DATE = datetime.strptime(
        os.getenv('SIMULATION_END_DATE', '2024-01-07'), '%Y-%m-%d'
    )
    
    # Database Configuration
    DATABASE_PATH = os.getenv('DATABASE_PATH', 'output/asana_simulation.sqlite')
    
    # Logging Configuration
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # Data Sources
    USE_REAL_COMPANY_NAMES = os.getenv('USE_REAL_COMPANY_NAMES', 'true').lower() == 'true'
    USE_REAL_PROJECT_TEMPLATES = os.getenv('USE_REAL_PROJECT_TEMPLATES', 'true').lower() == 'true'
    
    # Data constraints and heuristics
    TASK_COMPLETION_RATE_SPRINT = 0.75  # 75% of sprint tasks completed
    TASK_COMPLETION_RATE_BUG = 0.65  # 65% of bug tasks completed
    TASK_COMPLETION_RATE_ONGOING = 0.45  # 45% of ongoing tasks completed
    
    # Task due date distribution percentages
    TASK_DUE_DATE_DISTRIBUTION = {
        'within_week': 0.25,  # 25% within 1 week
        'within_month': 0.40,  # 40% within 1 month
        'within_3_months': 0.20,  # 20% 1-3 months out
        'no_due_date': 0.10,  # 10% no due date
        'overdue': 0.05  # 5% overdue
    }
    
    # Comment probability per task
    COMMENT_PROBABILITY = 0.6  # 60% of tasks have comments
    
    # Subtask probability per task
    SUBTASK_PROBABILITY = 0.35  # 35% of tasks have subtasks
    
    # Unassigned task probability
    UNASSIGNED_PROBABILITY = 0.15  # 15% of tasks are unassigned
