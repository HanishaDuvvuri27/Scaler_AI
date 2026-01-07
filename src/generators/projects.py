"""Generator for Projects and Sections."""

import random
from datetime import datetime
from typing import List

from src.models.entities import Project, Section, Team, User
from src.utils.id_generator import IDGenerator
from src.utils.date_generator import DateGenerator
from src.config import Config


class ProjectGenerator:
    """Generates realistic projects."""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.project_names = self._load_project_names()
        self.project_types = [
            'sprint', 'product_roadmap', 'marketing_campaign',
            'bug_tracking', 'operational', 'ongoing'
        ]
    
    def _load_project_names(self) -> List[str]:
        """Load project names from data file."""
        try:
            with open(f'{self.data_dir}/project_names.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return self._get_default_project_names()
    
    def _get_default_project_names(self) -> List[str]:
        """Fallback project names."""
        return [
            "Product Roadmap Q4", "Mobile App Redesign", "API v2 Migration",
            "Dashboard Optimization", "Customer Portal Launch",
            "Infrastructure Modernization", "AI Integration", "Website Redesign"
        ]
    
    def generate(self, organization_id: str, teams: List[Team], 
                 users: List[User], count: int, 
                 start_date: datetime, end_date: datetime) -> List[Project]:
        """Generate realistic projects."""
        projects = []
        used_names = set()
        
        for _ in range(count):
            # Ensure unique names
            while True:
                name = random.choice(self.project_names)
                if name not in used_names:
                    used_names.add(name)
                    break
            
            # Select team and owner
            team = random.choice(teams) if teams else None
            owner = random.choice(users)
            
            project_type = random.choice(self.project_types)
            
            project = Project(
                project_id=IDGenerator.generate_project_id(),
                organization_id=organization_id,
                team_id=team.team_id if team else None,
                name=name,
                description=f"Project for {name}. Type: {project_type}",
                created_at=DateGenerator.generate_created_at(start_date, end_date),
                owner_id=owner.user_id,
                status=random.choice(['active', 'active', 'active', 'archived']),
                project_type=project_type,
                is_archived=random.random() < 0.15  # 15% archived
            )
            projects.append(project)
        
        return projects


class SectionGenerator:
    """Generates realistic project sections."""
    
    # Standard section names for different project types
    DEFAULT_SECTIONS = {
        'sprint': ['Backlog', 'Ready', 'In Progress', 'Review', 'Done'],
        'product_roadmap': ['Q4 2024', 'Q1 2025', 'Future', 'On Hold'],
        'bug_tracking': ['New', 'Assigned', 'In Progress', 'Testing', 'Resolved'],
        'marketing_campaign': ['Ideation', 'Planning', 'Execution', 'Review', 'Complete'],
        'operational': ['To Do', 'In Progress', 'Complete'],
        'ongoing': ['Backlog', 'Active', 'Complete']
    }
    
    def generate(self, projects: List[Project]) -> List[Section]:
        """Generate sections for projects."""
        sections = []
        
        for project in projects:
            project_type = project.project_type or 'ongoing'
            section_names = self.DEFAULT_SECTIONS.get(project_type, ['To Do', 'Doing', 'Done'])
            
            for order, section_name in enumerate(section_names):
                section = Section(
                    section_id=IDGenerator.generate_uuid(),
                    project_id=project.project_id,
                    name=section_name,
                    display_order=order,
                    created_at=project.created_at
                )
                sections.append(section)
        
        return sections
