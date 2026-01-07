"""UUID and ID generation utilities."""

import uuid
from typing import Optional


class IDGenerator:
    """Generates Asana-like GID and UUIDs for various entities."""
    
    @staticmethod
    def generate_uuid() -> str:
        """Generate a UUIDv4 string."""
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_gid() -> str:
        """
        Generate an Asana-like Global ID (GID).
        Asana uses large numeric IDs; we'll use UUIDs for consistency.
        """
        return str(uuid.uuid4())
    
    @staticmethod
    def generate_ids(count: int, prefix: Optional[str] = None) -> list:
        """Generate multiple IDs."""
        return [IDGenerator.generate_uuid() for _ in range(count)]
    
    @staticmethod
    def generate_task_id() -> str:
        """Generate a task-specific ID."""
        return f"task_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_user_id() -> str:
        """Generate a user-specific ID."""
        return f"user_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_project_id() -> str:
        """Generate a project-specific ID."""
        return f"proj_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_team_id() -> str:
        """Generate a team-specific ID."""
        return f"team_{uuid.uuid4().hex[:12]}"
    
    @staticmethod
    def generate_organization_id() -> str:
        """Generate an organization-specific ID."""
        return f"org_{uuid.uuid4().hex[:12]}"
