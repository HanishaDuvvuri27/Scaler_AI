# Asana RL Environment Seed Data Generation

## Overview

This project generates high-quality, realistic seed data for a reinforcement learning environment simulating Asana, an enterprise project management platform. The generated SQLite database contains entities representing a B2B SaaS company with realistic workflows, distributions, and temporal patterns.

## Quick Start

### Prerequisites
- Python 3.8+
- SQLite3

### Installation

1. **Clone/Setup the project:**
```bash
cd asana-rl-seed-data
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your settings (optional OpenAI API key)
```

4. **Generate seed data:**
```bash
python src/main.py
```

The generated database will be created at `output/asana_simulation.sqlite`.

## Project Structure

```
asana-rl-seed-data/
├── README.md                          # This file
├── schema.sql                         # Database schema DDL
├── requirements.txt                   # Python dependencies
├── .env.example                       # Configuration template
├── src/
│   ├── main.py                        # Entry point and orchestration
│   ├── config.py                      # Configuration management
│   ├── scrapers/                      # External data sources
│   │   └── __init__.py
│   ├── generators/                    # Data generation modules
│   │   ├── organizations.py           # Organization and team generation
│   │   ├── users.py                   # User and membership generation
│   │   ├── projects.py                # Project and section generation
│   │   ├── tasks.py                   # Task generation with LLM support
│   │   ├── other_entities.py          # Subtasks, comments, tags, etc.
│   │   └── __init__.py
│   ├── models/                        # Data models
│   │   ├── entities.py                # Entity dataclasses
│   │   └── __init__.py
│   └── utils/                         # Utility functions
│       ├── config.py                  # Configuration utilities
│       ├── date_generator.py          # Date/time generation
│       ├── id_generator.py            # ID generation
│       ├── llm_client.py              # LLM interaction
│       └── __init__.py
├── prompts/                           # LLM prompt templates
├── data/                              # Data files
│   ├── company_names.txt              # Company name sources
│   ├── team_names.txt                 # Team name templates
│   └── project_names.txt              # Project templates
└── output/
    └── asana_simulation.sqlite        # Generated database
```

## Configuration

Edit `.env` to customize data generation:

```env
# LLM Configuration
OPENAI_API_KEY=sk-...
LLM_PROVIDER=openai
LLM_MODEL=gpt-3.5-turbo

# Data Generation
ORGANIZATION_COUNT=1
TEAM_COUNT=15
USER_COUNT=200
PROJECT_COUNT=45
TASK_COUNT=5000
SUBTASK_COUNT=2000
COMMENT_COUNT=3000

# Date Range
SIMULATION_START_DATE=2023-07-01
SIMULATION_END_DATE=2024-01-07

# Database
DATABASE_PATH=output/asana_simulation.sqlite
```

### Configuration Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `ORGANIZATION_COUNT` | 1 | Number of organizations to generate |
| `TEAM_COUNT` | 15 | Teams per organization |
| `USER_COUNT` | 200 | Users per organization |
| `PROJECT_COUNT` | 45 | Projects per organization |
| `TASK_COUNT` | 5000 | Total tasks to generate |
| `SUBTASK_COUNT` | 2000 | Subtasks per organization |
| `COMMENT_COUNT` | 3000 | Comments per organization |
| `SIMULATION_START_DATE` | 2023-07-01 | Simulation period start |
| `SIMULATION_END_DATE` | 2024-01-07 | Simulation period end |

## Data Realism Features

### 1. **Temporal Consistency**
- Task creation timestamps follow realistic business hour patterns (9am-5pm)
- Weighted by day-of-week (higher Mon-Wed, lower Fri-Sat)
- Growth curve applied over simulation period
- Completion timestamps follow log-normal distribution
- All temporal relationships validated (no completed-before-creation)

### 2. **Distribution Realism**
- **Task completion rates vary by project type:**
  - Sprint projects: 75% completion
  - Bug tracking: 65% completion
  - Ongoing projects: 45% completion

- **Task due dates follow research-based distribution:**
  - 25% within 1 week
  - 40% within 1 month
  - 20% 1-3 months out
  - 10% no due date
  - 5% overdue

- **Assignment patterns:**
  - 15% unassigned tasks
  - Weighted by team membership
  - Considers user workload

### 3. **Entity Relationships**
- Teams contain 8-25 users with realistic distribution
- Projects assigned to teams
- Tasks distributed across project sections
- 35% of tasks have 1-5 subtasks
- 60% of tasks have 1-5 comments
- Comments clustered around completion time

### 4. **Content Realism**
- Task names generated with project type-specific patterns
  - Engineering: "[Component] - [Action] - [Detail]"
  - Marketing: "[Campaign] - [Deliverable]"
  - Operations: Standard templates
- Descriptions vary in length (20% empty, 50% short, 30% detailed)
- Comments follow realistic patterns
- Custom fields initialized with org-wide definitions

## Database Schema

### Core Tables

- **organizations**: Top-level workspace containers
- **teams**: Groups within organizations (e.g., Engineering, Marketing)
- **users**: Individual team members with profiles
- **team_memberships**: User-team associations with roles
- **projects**: Goal-oriented task collections
- **sections**: Project subdivisions (e.g., "To Do", "Done")
- **tasks**: Primary work units with assignments and deadlines
- **subtasks**: Nested tasks within parent tasks
- **comments**: Task discussion and status updates
- **custom_field_definitions**: Organization-wide field schemas
- **custom_field_values**: Task/subtask field values
- **tags**: Organizational labels
- **task_tags**: Task-tag associations
- **attachments**: Files attached to tasks/comments

See `schema.sql` for complete DDL.

## LLM Integration

The generator supports OpenAI's GPT models for generating realistic task names, descriptions, and comments:

### Setup
1. Get API key from OpenAI
2. Set `OPENAI_API_KEY` in `.env`
3. The system will automatically use LLM for content generation

### Fallback
If LLM is unavailable or fails, the system falls back to template-based generation with realistic substitutions.

## Data Quality Verification

The system includes built-in verification:
- ✅ Referential integrity checks
- ✅ Temporal consistency validation
- ✅ Distribution verification
- ✅ Business logic compliance

Run verification:
```bash
python -m src.main
# Outputs summary of data statistics
```

## Performance Notes

Generation times (approximate):
- 1 Organization: ~5-10 minutes
- 200 Users: included above
- 5000 Tasks: included above
- Total with 200 users, 5000 tasks: ~15-20 minutes

Adjust `TASK_COUNT` and other parameters based on needed scale.

## Customization

### Adding Custom Data Sources

Edit `data/company_names.txt`, `data/team_names.txt`, `data/project_names.txt` to customize generated names.

### Modifying Task Patterns

Edit `src/generators/tasks.py` to adjust:
- Task naming conventions
- Description lengths
- Completion rates
- Priority distributions

### Adjusting Distributions

Edit `src/config.py` to modify:
- Task completion rates by project type
- Due date distributions
- Comment probability
- Subtask probability

## Troubleshooting

### LLM Generation Fails
- Verify `OPENAI_API_KEY` is set correctly
- Check API quota and rate limits
- System will fallback to templates automatically

### Database Locked Error
- Ensure no other processes have the database open
- Delete `output/asana_simulation.sqlite` and regenerate

### Out of Memory
- Reduce `TASK_COUNT` in `.env`
- Reduce `USER_COUNT` or `PROJECT_COUNT`
- Generate in smaller batches

## References

### Research Sources

- **Task Completion Rates**: Asana "Anatomy of Work" research
- **Due Date Distribution**: Industry sprint planning standards
- **Team Size Distribution**: Tech company team composition benchmarks
- **Temporal Patterns**: Business hour analysis, JIRA/GitHub data

### Used Libraries

- **Faker**: Realistic user name generation with diverse locales
- **OpenAI**: LLM-based content generation
- **SQLite3**: Lightweight embedded database
- **tqdm**: Progress tracking during generation

## Future Enhancements

- [ ] Support for Asana API integration
- [ ] Advanced LLM-based relationship generation
- [ ] Historical data trend analysis
- [ ] Performance metrics generation
- [ ] Export to other formats (PostgreSQL, MongoDB)


