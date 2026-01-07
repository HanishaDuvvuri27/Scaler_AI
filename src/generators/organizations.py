"""Generator for Organizations and Teams."""

import random
from datetime import datetime, timedelta
from typing import List, Tuple

from src.models.entities import Organization, Team
from src.utils.id_generator import IDGenerator
from src.utils.date_generator import DateGenerator
from src.config import Config


class OrganizationGenerator:
    """Generates realistic organizations/workspaces."""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.company_names = self._load_company_names()
        self.industries = [
            "Software/SaaS", "FinTech", "E-commerce", "Media/Publishing",
            "Healthcare Tech", "EdTech", "Logistics", "Real Estate",
            "Enterprise Software", "Cloud Infrastructure"
        ]
    
    def _load_company_names(self) -> List[str]:
        """Load company names from data file."""
        try:
            with open(f'{self.data_dir}/company_names.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return self._get_default_company_names()
    
    def _get_default_company_names(self) -> List[str]:
        """Fallback company names."""
        return [
            "TechFlow Solutions", "Vertex Analytics", "Nexus Platform",
            "Stellar Systems", "CloudVerse AI", "DataSync Pro", "Quantum Labs",
            "Aurora Cloud", "Prism Analytics", "Fusion Dynamics", "Zenith Tech",
            "Velocity Solutions", "Harmony Systems", "Nexar Global", "Cipher Labs"
        ]
    
    def generate(self, count: int, start_date: datetime, 
                 end_date: datetime) -> List[Organization]:
        """Generate realistic organizations."""
        organizations = []
        used_names = set()
        
        for _ in range(count):
            # Ensure unique names
            while True:
                name = random.choice(self.company_names)
                if name not in used_names:
                    used_names.add(name)
                    break
            
            # Create domain from company name
            domain = name.lower().replace(' ', '') + '.com'
            
            org = Organization(
                organization_id=IDGenerator.generate_organization_id(),
                name=name,
                domain=domain,
                industry=random.choice(self.industries),
                employee_count=random.choice([200, 500, 1000, 2000, 5000, 10000]),
                created_at=DateGenerator.generate_created_at(start_date, end_date),
                is_verified=True
            )
            organizations.append(org)
        
        return organizations


class TeamGenerator:
    """Generates realistic teams within organizations."""
    
    def __init__(self, data_dir='data'):
        self.data_dir = data_dir
        self.team_names = self._load_team_names()
    
    def _load_team_names(self) -> List[str]:
        """Load team names from data file."""
        try:
            with open(f'{self.data_dir}/team_names.txt', 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except FileNotFoundError:
            return self._get_default_team_names()
    
    def _get_default_team_names(self) -> List[str]:
        """Fallback team names."""
        return [
            "Product Development", "Engineering", "Marketing", "Sales",
            "Operations", "Customer Success", "DevOps", "QA & Testing",
            "Data Science", "Design", "Security", "Finance"
        ]
    
    def generate(self, organization_id: str, count: int, 
                 start_date: datetime, end_date: datetime) -> List[Team]:
        """Generate realistic teams for an organization."""
        teams = []
        used_names = set()
        
        for _ in range(count):
            # Ensure unique names within organization
            while True:
                name = random.choice(self.team_names)
                if name not in used_names:
                    used_names.add(name)
                    break
            
            team = Team(
                team_id=IDGenerator.generate_team_id(),
                organization_id=organization_id,
                name=name,
                description=f"{name} team for {organization_id}",
                created_at=DateGenerator.generate_created_at(start_date, end_date),
                lead_user_id=None  # Will be set after users are created
            )
            teams.append(team)
        
        return teams
