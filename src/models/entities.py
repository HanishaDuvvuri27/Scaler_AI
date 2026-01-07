"""Data models for Asana entities."""

from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, List


@dataclass
class Organization:
    organization_id: str
    name: str
    domain: str
    created_at: datetime
    industry: str = "Software/SaaS"
    employee_count: int = 500
    is_verified: bool = True


@dataclass
class Team:
    team_id: str
    organization_id: str
    name: str
    description: Optional[str] = None
    created_at: Optional[datetime] = None
    lead_user_id: Optional[str] = None


@dataclass
class User:
    user_id: str
    organization_id: str
    email: str
    name: str
    first_name: str
    last_name: str
    created_at: datetime
    avatar_url: Optional[str] = None
    is_active: bool = True
    last_seen: Optional[datetime] = None


@dataclass
class TeamMembership:
    team_membership_id: str
    team_id: str
    user_id: str
    joined_at: datetime
    role: str = "member"
    is_active: bool = True


@dataclass
class Project:
    project_id: str
    organization_id: str
    name: str
    created_at: datetime
    owner_id: str
    team_id: Optional[str] = None
    description: Optional[str] = None
    status: str = "active"
    project_type: Optional[str] = None
    is_archived: bool = False


@dataclass
class Section:
    section_id: str
    project_id: str
    name: str
    created_at: datetime
    display_order: int = 0


@dataclass
class Task:
    task_id: str
    project_id: str
    name: str
    created_at: datetime
    created_by: str
    section_id: Optional[str] = None
    description: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[date] = None
    start_date: Optional[date] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    priority: Optional[int] = None
    estimated_hours: Optional[float] = None


@dataclass
class Subtask:
    subtask_id: str
    parent_task_id: str
    project_id: str
    name: str
    created_at: datetime
    created_by: str
    assignee_id: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[date] = None
    completed: bool = False
    completed_at: Optional[datetime] = None
    display_order: int = 0


@dataclass
class Comment:
    comment_id: str
    user_id: str
    text: str
    created_at: datetime
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None
    updated_at: Optional[datetime] = None
    attachment_count: int = 0


@dataclass
class CustomFieldDefinition:
    custom_field_id: str
    organization_id: str
    name: str
    field_type: str
    created_at: datetime
    description: Optional[str] = None
    is_active: bool = True


@dataclass
class CustomFieldValue:
    custom_field_value_id: str
    custom_field_id: str
    value: str
    created_at: datetime
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None


@dataclass
class Tag:
    tag_id: str
    organization_id: str
    name: str
    created_at: datetime
    created_by: str
    color: Optional[str] = None


@dataclass
class TaskTag:
    task_tag_id: str
    task_id: str
    tag_id: str
    added_at: datetime


@dataclass
class Attachment:
    attachment_id: str
    filename: str
    created_at: datetime
    uploaded_by: str
    task_id: Optional[str] = None
    subtask_id: Optional[str] = None
    comment_id: Optional[str] = None
    file_url: Optional[str] = None
    file_size: Optional[int] = None
