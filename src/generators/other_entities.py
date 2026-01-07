"""Generator for Subtasks, Comments, Custom Fields, and Tags."""

import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from src.models.entities import (
    Subtask, Comment, CustomFieldDefinition, CustomFieldValue, 
    Tag, TaskTag, Task, Project, User
)
from src.utils.id_generator import IDGenerator
from src.utils.date_generator import DateGenerator
from src.utils.llm_client import LLMClient, PromptManager
from src.config import Config


class SubtaskGenerator:
    """Generates subtasks for parent tasks."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
    
    def generate(self, tasks: List[Task], projects: Dict[str, Project],
                 users: List[User]) -> List[Subtask]:
        """
        Generate subtasks.
        
        Distribution:
        - 35% of tasks have subtasks
        - Tasks can have 1-5 subtasks
        """
        subtasks = []
        
        for task in tasks:
            # Decide if task gets subtasks
            if random.random() > Config.SUBTASK_PROBABILITY:
                continue
            
            # Number of subtasks
            subtask_count = random.choices([1, 2, 3, 4, 5], weights=[0.40, 0.30, 0.20, 0.07, 0.03])[0]
            
            for order in range(subtask_count):
                subtask = Subtask(
                    subtask_id=IDGenerator.generate_uuid(),
                    parent_task_id=task.task_id,
                    project_id=task.project_id,
                    name=f"{task.name} - Subtask {order + 1}",
                    description=f"Subtask for completing {task.name}",
                    created_at=task.created_at + timedelta(minutes=random.randint(5, 60)),
                    created_by=task.created_by,
                    assignee_id=random.choice(users).user_id if random.random() > 0.20 else None,
                    due_date=task.due_date,
                    completed=task.completed and random.random() < 0.85,  # Mostly completed with parent
                    completed_at=task.completed_at if task.completed and random.random() < 0.85 else None,
                    display_order=order
                )
                subtasks.append(subtask)
        
        return subtasks


class CommentGenerator:
    """Generates comments on tasks."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.prompt_manager = PromptManager()
        
        self.comment_templates = [
            "Looks good! 👍",
            "Ready for review",
            "Making progress on this",
            "Blocked by [blocker], will resume next week",
            "Updated based on feedback",
            "This is ready to merge",
            "Added [component] as requested",
            "Discussed with [person], we're aligned on approach",
            "Testing in progress",
            "Documentation updated",
        ]
    
    def generate(self, tasks: List[Task], users: List[User],
                 start_date: datetime, end_date: datetime) -> List[Comment]:
        """
        Generate comments on tasks.
        
        Distribution:
        - 60% of tasks have comments
        - 1-5 comments per task
        - More comments on completed tasks
        """
        comments = []
        
        for task in tasks:
            if random.random() > Config.COMMENT_PROBABILITY:
                continue
            
            # More comments on completed/important tasks
            comment_count = random.choices(
                [1, 2, 3, 4, 5],
                weights=[0.35, 0.30, 0.20, 0.10, 0.05]
            )[0]
            
            for _ in range(comment_count):
                comment_author = random.choice(users)
                
                # Comment created after task creation, with reasonable timing
                # If task is completed, comment before or after completion
                # If not completed, comment within last 2 weeks
                if task.completed_at and task.completed_at > task.created_at:
                    # Comment between creation and completion
                    time_diff = (task.completed_at - task.created_at).total_seconds()
                    random_seconds = random.randint(0, int(time_diff))
                    comment_date = task.created_at + timedelta(seconds=random_seconds)
                else:
                    # Comment within 14 days of now or task creation
                    days_back = random.randint(0, 14)
                    comment_date = datetime.now() - timedelta(days=days_back)
                    # But ensure after task creation
                    comment_date = max(comment_date, task.created_at + timedelta(minutes=5))
                
                # Generate comment text
                text = random.choice(self.comment_templates)
                
                comment = Comment(
                    comment_id=IDGenerator.generate_uuid(),
                    task_id=task.task_id,
                    user_id=comment_author.user_id,
                    text=text,
                    created_at=comment_date,
                    attachment_count=0
                )
                comments.append(comment)
        
        return comments


class CustomFieldGenerator:
    """Generates custom field definitions and values."""
    
    FIELD_DEFINITIONS = {
        'Text': ['Status', 'Component', 'Release Version'],
        'SingleSelect': ['Priority', 'Effort Level', 'Risk Level', 'Phase'],
        'MultiSelect': ['Labels', 'Skills Required', 'Dependencies'],
        'Number': ['Story Points', 'Estimated Hours', 'Complexity Score'],
        'Dropdown': ['Team', 'Quarter']
    }
    
    FIELD_VALUES = {
        'Status': ['Not Started', 'In Progress', 'Blocked', 'Complete'],
        'Priority': ['Low', 'Medium', 'High', 'Critical'],
        'Effort Level': ['XS', 'S', 'M', 'L', 'XL'],
        'Risk Level': ['Low', 'Medium', 'High'],
        'Phase': ['Phase 1', 'Phase 2', 'Phase 3', 'Phase 4'],
        'Quarter': ['Q1', 'Q2', 'Q3', 'Q4'],
    }
    
    def generate_definitions(self, organization_id: str) -> List[CustomFieldDefinition]:
        """Generate custom field definitions."""
        definitions = []
        used_names = set()
        
        # Collect all unique field names
        all_field_names = []
        for field_names in self.FIELD_DEFINITIONS.values():
            all_field_names.extend(field_names)
        
        # Randomly select 8-13 unique fields
        selected_fields = random.sample(all_field_names, k=min(random.randint(8, 13), len(all_field_names)))
        
        for field_name in selected_fields:
            # Find the type for this field
            field_type = None
            for ftype, fnames in self.FIELD_DEFINITIONS.items():
                if field_name in fnames:
                    field_type = ftype
                    break
            
            definition = CustomFieldDefinition(
                custom_field_id=IDGenerator.generate_uuid(),
                organization_id=organization_id,
                name=field_name,
                field_type=field_type or 'Text',
                description=f"Custom field: {field_name}",
                created_at=datetime.now() - timedelta(days=random.randint(30, 180))
            )
            definitions.append(definition)
        
        return definitions
    
    def generate_values(self, tasks: List[Task], 
                       field_definitions: List[CustomFieldDefinition]) -> List[CustomFieldValue]:
        """Generate custom field values for tasks."""
        values = []
        
        for task in tasks:
            # 60% of tasks have custom field values
            if random.random() > 0.60:
                continue
            
            # Select 1-3 fields for this task
            selected_fields = random.sample(
                field_definitions, 
                k=min(random.randint(1, 3), len(field_definitions))
            )
            
            for field in selected_fields:
                field_value = field.name
                
                if field.field_type == 'SingleSelect':
                    field_value = random.choice(self.FIELD_VALUES.get(field.name, ['Value1', 'Value2']))
                elif field.field_type == 'Number':
                    field_value = str(random.randint(1, 50))
                
                value = CustomFieldValue(
                    custom_field_value_id=IDGenerator.generate_uuid(),
                    custom_field_id=field.custom_field_id,
                    task_id=task.task_id,
                    value=field_value,
                    created_at=task.created_at
                )
                values.append(value)
        
        return values


class TagGenerator:
    """Generates tags for organization."""
    
    DEFAULT_TAGS = [
        'urgent', 'documentation', 'refactor', 'bug-fix', 'feature',
        'backend', 'frontend', 'database', 'security', 'performance',
        'testing', 'ui/ux', 'api', 'infrastructure', 'devops',
        'ai/ml', 'analytics', 'mobile', 'web', 'deployment'
    ]
    
    COLORS = [
        '#FF5A5F', '#FF9671', '#FFD93D', '#6BCB77',
        '#4D96FF', '#9D84B7', '#FF8AAE', '#00D9FF'
    ]
    
    def generate(self, organization_id: str, users: List[User]) -> List[Tag]:
        """Generate tags for organization."""
        tags = []
        
        for tag_name in self.DEFAULT_TAGS:
            tag = Tag(
                tag_id=IDGenerator.generate_uuid(),
                organization_id=organization_id,
                name=tag_name,
                color=random.choice(self.COLORS),
                created_at=datetime.now() - timedelta(days=random.randint(30, 180)),
                created_by=random.choice(users).user_id
            )
            tags.append(tag)
        
        return tags
    
    def generate_task_tags(self, tasks: List[Task], tags: List[Tag]) -> List[TaskTag]:
        """Associate tags with tasks."""
        task_tags = []
        
        for task in tasks:
            # 50% of tasks have tags
            if random.random() > 0.50:
                continue
            
            # 1-3 tags per task
            selected_tags = random.sample(tags, k=min(random.randint(1, 3), len(tags)))
            
            for tag in selected_tags:
                task_tag = TaskTag(
                    task_tag_id=IDGenerator.generate_uuid(),
                    task_id=task.task_id,
                    tag_id=tag.tag_id,
                    added_at=task.created_at + timedelta(minutes=random.randint(0, 120))
                )
                task_tags.append(task_tag)
        
        return task_tags
