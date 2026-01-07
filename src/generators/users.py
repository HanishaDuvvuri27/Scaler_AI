"""Generator for Users and Team Memberships."""

import random
from datetime import datetime
from typing import List

from faker import Faker
from src.models.entities import User, TeamMembership
from src.utils.id_generator import IDGenerator
from src.utils.date_generator import DateGenerator
from src.config import Config


class UserGenerator:
    """Generates realistic users with demographic diversity."""
    
    def __init__(self):
        self.faker = Faker()
        # Create multiple locales for demographic diversity
        self.locales = ['en_US', 'en_GB', 'en_IE', 'en_AU']
        self.faker_instances = [Faker(locale) for locale in self.locales]
    
    def generate(self, organization_id: str, count: int,
                 start_date: datetime, end_date: datetime) -> List[User]:
        """Generate realistic users with diverse names."""
        users = []
        used_emails = set()
        
        for _ in range(count):
            # Select random faker instance for diversity
            faker = random.choice(self.faker_instances)
            
            name = faker.name()
            first_name, *last_parts = name.split()
            last_name = ' '.join(last_parts) if last_parts else 'User'
            
            # Ensure unique email
            base_email = f"{first_name.lower()}.{last_name.lower()}".replace(' ', '_')
            email = f"{base_email}@company.com"
            counter = 1
            while email in used_emails:
                email = f"{base_email}{counter}@company.com"
                counter += 1
            used_emails.add(email)
            
            user = User(
                user_id=IDGenerator.generate_user_id(),
                organization_id=organization_id,
                email=email,
                name=name,
                first_name=first_name,
                last_name=last_name,
                avatar_url=f"https://i.pravatar.cc/150?u={email}",
                created_at=DateGenerator.generate_created_at(start_date, end_date),
                is_active=random.random() > 0.05,  # 95% active
                last_seen=datetime.now() - timedelta(days=random.randint(0, 30))
            )
            users.append(user)
        
        return users


class TeamMembershipGenerator:
    """Generates team memberships with realistic distribution."""
    
    def generate(self, teams: List, users: List, 
                 start_date: datetime) -> List[TeamMembership]:
        """
        Generate team memberships.
        
        Distribution:
        - Average team size: 12-15 people
        - Some users in multiple teams (cross-functional)
        - Team leads assigned from existing users
        """
        memberships = []
        team_size_distribution = {
            8: 0.10,   # 10% small teams
            12: 0.25,  # 25% medium-small teams
            15: 0.35,  # 35% medium teams
            20: 0.20,  # 20% medium-large teams
            25: 0.10   # 10% large teams
        }
        
        used_assignments = set()  # Track user-team assignments
        
        for team in teams:
            # Determine team size
            team_size = random.choices(
                list(team_size_distribution.keys()),
                weights=list(team_size_distribution.values())
            )[0]
            
            # Select team members (prefer unassigned users first)
            available_users = [u for u in users if (u.user_id, team.team_id) not in used_assignments]
            team_members = random.sample(available_users, min(team_size, len(available_users)))
            
            for i, user in enumerate(team_members):
                used_assignments.add((user.user_id, team.team_id))
                membership = TeamMembership(
                    team_membership_id=IDGenerator.generate_uuid(),
                    team_id=team.team_id,
                    user_id=user.user_id,
                    joined_at=DateGenerator.generate_created_at(
                        start_date, 
                        user.created_at if user.created_at > start_date else start_date
                    ),
                    role="lead" if i == 0 else "member",
                    is_active=user.is_active
                )
                memberships.append(membership)
        
        return memberships


# Add missing import
from datetime import timedelta
