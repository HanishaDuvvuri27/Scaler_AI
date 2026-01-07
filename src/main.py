"""Main orchestration script for generating Asana seed data."""

import sqlite3
import logging
import sys
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from tqdm import tqdm

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.generators.organizations import OrganizationGenerator, TeamGenerator
from src.generators.users import UserGenerator, TeamMembershipGenerator
from src.generators.projects import ProjectGenerator, SectionGenerator
from src.generators.tasks import TaskGenerator
from src.generators.other_entities import (
    SubtaskGenerator, CommentGenerator, CustomFieldGenerator, TagGenerator
)
from src.utils.llm_client import LLMClient


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database connections and operations."""
    
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._ensure_directory(db_path)
    
    def _ensure_directory(self, db_path: str):
        """Ensure database directory exists."""
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
    
    def initialize_schema(self):
        """Initialize database schema from schema.sql."""
        try:
            with open('schema.sql', 'r') as f:
                schema = f.read()
            
            conn = sqlite3.connect(self.db_path)
            conn.executescript(schema)
            conn.commit()
            conn.close()
            logger.info(f"Database schema initialized: {self.db_path}")
        except FileNotFoundError:
            logger.error("schema.sql not found!")
            raise
    
    def insert_batch(self, table_name: str, data: list, columns: list):
        """Insert batch of records into table."""
        if not data:
            return
        
        placeholders = ','.join(['?' for _ in columns])
        query = f"INSERT INTO {table_name} ({','.join(columns)}) VALUES ({placeholders})"
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Convert entities to tuples
        rows = []
        for item in data:
            if hasattr(item, '__dict__'):
                # It's a dataclass
                values = tuple(getattr(item, col) for col in columns)
            else:
                values = tuple(item[col] if isinstance(item, dict) else item[col] for col in columns)
            rows.append(values)
        
        cursor.executemany(query, rows)
        conn.commit()
        conn.close()
    
    def verify_data(self) -> dict:
        """Verify data integrity."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        tables = [
            'organizations', 'teams', 'users', 'team_memberships',
            'projects', 'sections', 'tasks', 'subtasks', 'comments',
            'custom_field_definitions', 'custom_field_values', 'tags', 'task_tags'
        ]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            count = cursor.fetchone()[0]
            stats[table] = count
        
        conn.close()
        return stats


class AsanaDataGenerator:
    """Main orchestrator for generating Asana seed data."""
    
    def __init__(self, config: Config):
        self.config = config
        self.db_manager = DatabaseManager(config.DATABASE_PATH)
        
        # Initialize LLM client if API key provided
        self.llm_client = None
        if config.OPENAI_API_KEY:
            try:
                self.llm_client = LLMClient(
                    provider=config.LLM_PROVIDER,
                    model=config.LLM_MODEL,
                    api_key=config.OPENAI_API_KEY
                )
                logger.info(f"LLM client initialized: {config.LLM_PROVIDER}")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}. Using fallback templates.")
    
    def generate(self):
        """Generate all seed data."""
        logger.info("Starting Asana seed data generation...")
        
        # Initialize database
        self.db_manager.initialize_schema()
        
        # Generate entities in order of dependencies
        logger.info("Generating organizations...")
        org_gen = OrganizationGenerator()
        organizations = org_gen.generate(
            self.config.ORGANIZATION_COUNT,
            self.config.SIMULATION_START_DATE,
            self.config.SIMULATION_END_DATE
        )
        self._insert_entities(organizations, 'organizations', [
            'organization_id', 'name', 'domain', 'industry', 'employee_count',
            'created_at', 'is_verified'
        ])
        
        org_id = organizations[0].organization_id
        
        # Generate teams
        logger.info("Generating teams...")
        team_gen = TeamGenerator()
        teams = team_gen.generate(
            org_id,
            self.config.TEAM_COUNT,
            self.config.SIMULATION_START_DATE,
            self.config.SIMULATION_END_DATE
        )
        self._insert_entities(teams, 'teams', [
            'team_id', 'organization_id', 'name', 'description', 'created_at', 'lead_user_id'
        ])
        
        # Generate users
        logger.info("Generating users...")
        user_gen = UserGenerator()
        users = user_gen.generate(
            org_id,
            self.config.USER_COUNT,
            self.config.SIMULATION_START_DATE,
            self.config.SIMULATION_END_DATE
        )
        self._insert_entities(users, 'users', [
            'user_id', 'organization_id', 'email', 'name', 'first_name',
            'last_name', 'avatar_url', 'created_at', 'is_active', 'last_seen'
        ])
        
        # Generate team memberships
        logger.info("Generating team memberships...")
        membership_gen = TeamMembershipGenerator()
        memberships = membership_gen.generate(teams, users, self.config.SIMULATION_START_DATE)
        self._insert_entities(memberships, 'team_memberships', [
            'team_membership_id', 'team_id', 'user_id', 'joined_at', 'role', 'is_active'
        ])
        
        # Generate projects
        logger.info("Generating projects...")
        project_gen = ProjectGenerator()
        projects = project_gen.generate(
            org_id,
            teams,
            users,
            self.config.PROJECT_COUNT,
            self.config.SIMULATION_START_DATE,
            self.config.SIMULATION_END_DATE
        )
        self._insert_entities(projects, 'projects', [
            'project_id', 'organization_id', 'team_id', 'name', 'description',
            'created_at', 'owner_id', 'status', 'project_type', 'is_archived'
        ])
        
        # Generate sections
        logger.info("Generating sections...")
        section_gen = SectionGenerator()
        sections = section_gen.generate(projects)
        self._insert_entities(sections, 'sections', [
            'section_id', 'project_id', 'name', 'display_order', 'created_at'
        ])
        
        # Create sections lookup
        sections_by_project = defaultdict(list)
        for section in sections:
            sections_by_project[section.project_id].append(section)
        
        # Generate tasks
        logger.info("Generating tasks...")
        task_gen = TaskGenerator(self.llm_client)
        tasks = task_gen.generate(
            projects,
            sections_by_project,
            users,
            self.config.TASK_COUNT,
            self.config.SIMULATION_START_DATE,
            self.config.SIMULATION_END_DATE
        )
        self._insert_entities(tasks, 'tasks', [
            'task_id', 'project_id', 'section_id', 'name', 'description',
            'created_at', 'created_by', 'assignee_id', 'due_date', 'start_date',
            'completed', 'completed_at', 'priority', 'estimated_hours'
        ])
        
        # Generate subtasks
        logger.info("Generating subtasks...")
        subtask_gen = SubtaskGenerator(self.llm_client)
        projects_dict = {p.project_id: p for p in projects}
        subtasks = subtask_gen.generate(tasks, projects_dict, users)
        self._insert_entities(subtasks, 'subtasks', [
            'subtask_id', 'parent_task_id', 'project_id', 'name', 'description',
            'created_at', 'created_by', 'assignee_id', 'due_date', 'completed',
            'completed_at', 'display_order'
        ])
        
        # Generate comments
        logger.info("Generating comments...")
        comment_gen = CommentGenerator(self.llm_client)
        comments = comment_gen.generate(tasks, users, self.config.SIMULATION_START_DATE, self.config.SIMULATION_END_DATE)
        self._insert_entities(comments, 'comments', [
            'comment_id', 'task_id', 'subtask_id', 'user_id', 'text',
            'created_at', 'updated_at', 'attachment_count'
        ])
        
        # Generate custom fields
        logger.info("Generating custom fields...")
        custom_field_gen = CustomFieldGenerator()
        custom_field_defs = custom_field_gen.generate_definitions(org_id)
        self._insert_entities(custom_field_defs, 'custom_field_definitions', [
            'custom_field_id', 'organization_id', 'name', 'description',
            'field_type', 'created_at', 'is_active'
        ])
        
        custom_field_values = custom_field_gen.generate_values(tasks, custom_field_defs)
        self._insert_entities(custom_field_values, 'custom_field_values', [
            'custom_field_value_id', 'custom_field_id', 'task_id', 'subtask_id',
            'value', 'created_at'
        ])
        
        # Generate tags
        logger.info("Generating tags...")
        tag_gen = TagGenerator()
        tags = tag_gen.generate(org_id, users)
        self._insert_entities(tags, 'tags', [
            'tag_id', 'organization_id', 'name', 'color', 'created_at', 'created_by'
        ])
        
        task_tags = tag_gen.generate_task_tags(tasks, tags)
        self._insert_entities(task_tags, 'task_tags', [
            'task_tag_id', 'task_id', 'tag_id', 'added_at'
        ])
        
        # Verify data
        logger.info("Verifying data...")
        stats = self.db_manager.verify_data()
        
        logger.info("Data generation complete!")
        logger.info(f"Database: {self.config.DATABASE_PATH}")
        logger.info("Summary of generated data:")
        for table, count in stats.items():
            logger.info(f"  {table}: {count}")
        
        return stats
    
    def _insert_entities(self, entities, table_name, columns):
        """Insert entities with progress bar."""
        if not entities:
            logger.warning(f"No entities to insert into {table_name}")
            return
        
        with tqdm(total=len(entities), desc=f"Inserting {table_name}") as pbar:
            # Insert in batches
            batch_size = 100
            for i in range(0, len(entities), batch_size):
                batch = entities[i:i+batch_size]
                self.db_manager.insert_batch(table_name, batch, columns)
                pbar.update(len(batch))


def main():
    """Main entry point."""
    try:
        generator = AsanaDataGenerator(Config)
        stats = generator.generate()
        print("\n[SUCCESS] Seed data generation successful!")
        return 0
    except Exception as e:
        logger.error(f"Error during generation: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    exit(main())
