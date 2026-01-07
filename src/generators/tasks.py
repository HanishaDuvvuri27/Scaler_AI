"""Generator for Tasks with realistic patterns and LLM-based content."""

import random
from datetime import datetime, timedelta
from typing import List, Optional, Dict

from src.models.entities import Task, Project, Section, User
from src.utils.id_generator import IDGenerator
from src.utils.date_generator import DateGenerator
from src.utils.llm_client import PromptManager, LLMClient
from src.config import Config


class TaskGenerator:
    """Generates realistic tasks with LLM-based content and realistic patterns."""
    
    def __init__(self, llm_client: Optional[LLMClient] = None):
        self.llm_client = llm_client
        self.prompt_manager = PromptManager()
        
        # Task name templates for different project types
        self.task_templates = {
            'engineering': [
                "Implement [feature]",
                "Fix [bug] in [component]",
                "Refactor [module] for [goal]",
                "Optimize [system] - [improvement]",
                "Add [capability] to [component]",
                "Update [component] to [spec]",
                "Research [topic] for [goal]",
                "Write tests for [component]",
                "Document [feature]",
                "Review PR for [feature]",
            ],
            'marketing': [
                "[Campaign] - Create [asset]",
                "[Campaign] - Write [content]",
                "[Campaign] - Design [deliverable]",
                "[Campaign] - Review [document]",
                "[Campaign] - Schedule [post]",
                "[Campaign] - Analyze [metric]",
                "[Campaign] - Plan [phase]",
                "[Campaign] - Launch [initiative]",
            ],
            'operations': [
                "Renew [service] credentials",
                "Update [system] configuration",
                "Schedule [meeting]",
                "Process [request] for [team]",
                "Review [policy] compliance",
                "Coordinate [initiative]",
                "Plan [event]",
                "Update documentation for [process]",
            ]
        }
    
    def generate(self, projects: List[Project], sections: Dict[str, List[Section]], 
                 users: List[User], count: int, 
                 start_date: datetime, end_date: datetime) -> List[Task]:
        """
        Generate realistic tasks with proper distributions.
        
        Key patterns:
        - 15% unassigned tasks
        - Completion rates vary by project type (sprint 75%, bug 65%, ongoing 45%)
        - Due dates follow research-based distribution
        - Temporal consistency maintained
        """
        tasks = []
        
        for _ in range(count):
            project = random.choice(projects)
            creator = random.choice(users)
            
            # Get sections for this project
            project_sections = sections.get(project.project_id, [])
            section = random.choice(project_sections) if project_sections else None
            
            # Generate creation timestamp
            created_at = DateGenerator.generate_created_at(start_date, end_date)
            
            # Generate task name
            task_name = self._generate_task_name(project, creator)
            
            # Generate description
            description = self._generate_description(task_name, project)
            
            # Determine assignee (15% unassigned)
            assignee_id = None
            if random.random() > Config.UNASSIGNED_PROBABILITY:
                assignee_id = random.choice(users).user_id
            
            # Generate due date with realistic distribution
            due_date = None
            if random.random() > 0.10:  # 90% of tasks have due dates
                # Generate due date that's after created_at
                days_in_future = random.choices(
                    [random.randint(1, 7), random.randint(8, 30), random.randint(31, 90)],
                    weights=[0.25, 0.40, 0.20]
                )[0]
                
                due_date = (created_at + timedelta(days=days_in_future)).date()
                
                # Avoid weekends
                if random.random() < 0.85:
                    while due_date.weekday() in [5, 6]:
                        due_date += timedelta(days=1)
                
                # Ensure within end_date
                if due_date > end_date.date():
                    due_date = end_date.date()
            
            # Determine completion status
            completion_rate = self._get_completion_rate(project.project_type)
            completed = random.random() < completion_rate
            
            # Generate completion timestamp if completed
            completed_at = None
            if completed and created_at < datetime.now():
                completed_at = DateGenerator.generate_completed_at(
                    created_at, project.project_type
                )
            
            # Priority assignment
            priority = random.choices(
                [1, 2, 3, 4],  # 1=urgent, 2=high, 3=normal, 4=low
                weights=[0.10, 0.25, 0.50, 0.15]
            )[0]
            
            # Estimated hours for engineering tasks
            estimated_hours = None
            if project.project_type == 'sprint':
                estimated_hours = random.choice([1, 2, 4, 5, 8, 13])
            
            task = Task(
                task_id=IDGenerator.generate_uuid(),
                project_id=project.project_id,
                section_id=section.section_id if section else None,
                name=task_name,
                description=description,
                created_at=created_at,
                created_by=creator.user_id,
                assignee_id=assignee_id,
                due_date=due_date,
                completed=completed,
                completed_at=completed_at,
                priority=priority,
                estimated_hours=estimated_hours
            )
            
            tasks.append(task)
        
        return tasks
    
    def _generate_task_name(self, project: Project, creator: User) -> str:
        """Generate a realistic task name based on project type."""
        project_type = project.project_type or 'ongoing'
        templates = self.task_templates.get(project_type, self.task_templates['engineering'])
        
        base_name = random.choice(templates)
        
        # Use LLM if available, otherwise use template with substitutions
        if self.llm_client:
            try:
                prompt = self.prompt_manager.TASK_NAME_PROMPTS.get(project_type, '')
                if prompt:
                    task_name = self.llm_client.generate_text(
                        prompt.format(
                            component="system" if project_type == 'engineering' else "campaign",
                            project_type=project_type,
                            campaign=project.name,
                            team="team",
                            context="general"
                        ),
                        temperature=0.7,
                        max_tokens=100,
                        cache_key=f"task_name_{project_type}_{hash(base_name)}"
                    )
                    return task_name.strip()
            except Exception as e:
                print(f"LLM generation failed: {e}. Using template.")
        
        # Fallback to template substitution
        return self._substitute_template(base_name, project_type)
    
    def _substitute_template(self, template: str, project_type: str) -> str:
        """Substitute placeholders in template with realistic values."""
        substitutions = {
            'engineering': {
                '[feature]': ['user authentication', 'mobile support', 'caching layer', 'API endpoints'],
                '[bug]': ['race condition', 'memory leak', 'null pointer exception', 'API timeout'],
                '[component]': ['database', 'API client', 'UI component', 'service layer'],
                '[module]': ['authentication', 'payment processing', 'data models', 'utilities'],
                '[goal]': ['performance', 'maintainability', 'scalability', 'readability'],
                '[system]': ['database queries', 'API responses', 'image processing', 'cache'],
                '[improvement]': ['indexing', 'lazy loading', 'batching', 'compression'],
                '[capability]': ['error handling', 'logging', 'metrics', 'notifications'],
                '[spec]': ['new requirements', 'design specs', 'API contract', 'interface'],
                '[topic]': ['scaling strategies', 'architecture patterns', 'framework options', 'tools'],
            },
            'marketing': {
                '[Campaign]': ['Q4 Product Launch', 'Black Friday', 'Brand Refresh', 'Partner Program'],
                '[asset]': ['email template', 'social media post', 'landing page', 'promotional banner'],
                '[content]': ['blog post', 'whitepaper', 'case study', 'newsletter'],
                '[deliverable]': ['presentation deck', 'video script', 'infographic', 'campaign plan'],
                '[document]': ['campaign brief', 'content calendar', 'brand guidelines', 'strategy doc'],
                '[post]': ['tweets', 'LinkedIn updates', 'Instagram posts', 'email campaign'],
                '[metric]': ['CTR', 'conversion rate', 'engagement', 'impressions'],
                '[phase]': ['phase 1', 'phase 2', 'final push', 'launch'],
                '[initiative]': ['webinar', 'campaign', 'partnership', 'promotion'],
            }
        }
        
        result = template
        if project_type in substitutions:
            for placeholder, options in substitutions[project_type].items():
                if placeholder in result:
                    result = result.replace(placeholder, random.choice(options))
        
        return result
    
    def _generate_description(self, task_name: str, project: Project) -> Optional[str]:
        """Generate task description."""
        if random.random() < 0.20:
            return None  # 20% tasks have no description
        
        description_lengths = {
            'short': 0.35,   # 35% have 1-2 sentences
            'medium': 0.40,  # 40% have 3-5 sentences
            'long': 0.25     # 25% have detailed descriptions with bullets
        }
        
        length_type = random.choices(
            list(description_lengths.keys()),
            weights=list(description_lengths.values())
        )[0]
        
        if self.llm_client:
            try:
                prompt_type = length_type
                prompt = self.prompt_manager.TASK_DESCRIPTION_PROMPTS.get(prompt_type, '')
                description = self.llm_client.generate_text(
                    prompt.format(task_name=task_name, project_name=project.name),
                    temperature=0.7,
                    max_tokens=300
                )
                return description.strip()
            except:
                pass
        
        # Fallback descriptions
        base_descriptions = {
            'short': f"Work on {task_name}.",
            'medium': f"Complete {task_name} according to project requirements. This task is part of {project.name}.",
            'long': f"Complete {task_name} with the following criteria:\n- Ensure quality standards\n- Document the process\n- Get team review\n- Update project tracking"
        }
        
        return base_descriptions.get(length_type, "Task description")
    
    def _get_completion_rate(self, project_type: Optional[str]) -> float:
        """Get completion rate based on project type."""
        rates = {
            'sprint': Config.TASK_COMPLETION_RATE_SPRINT,
            'bug': Config.TASK_COMPLETION_RATE_BUG,
            'product_roadmap': 0.55,
            'marketing_campaign': 0.65,
            'operational': 0.50,
            'ongoing': Config.TASK_COMPLETION_RATE_ONGOING
        }
        return rates.get(project_type, 0.50)
