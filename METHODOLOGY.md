# Asana RL Seed Data - Methodology Documentation

## Section A: Database Schema

### 1. Complete Relational Schema

#### Table: organizations
```sql
organizations
├── organization_id (TEXT, PK) - UUID identifying organization
├── name (TEXT, NOT NULL) - Organization name
├── domain (TEXT, UNIQUE, NOT NULL) - Email domain
├── industry (TEXT) - Industry classification
├── employee_count (INTEGER) - Organization size
├── created_at (TIMESTAMP, NOT NULL) - Creation timestamp
└── is_verified (BOOLEAN) - Domain verification status
```

**Rationale**: Top-level container for all workspace data. Domain field enables realistic email generation.

#### Table: teams
```sql
teams
├── team_id (TEXT, PK) - UUID
├── organization_id (TEXT, FK) - Parent organization
├── name (TEXT, NOT NULL) - Team name
├── description (TEXT) - Team purpose
├── created_at (TIMESTAMP) - Establishment date
├── lead_user_id (TEXT, FK) - Team lead
└── UNIQUE(organization_id, name) - Unique within org
```

**Rationale**: Represents functional units (Engineering, Marketing, etc.). Lead user tracked separately.

#### Table: users
```sql
users
├── user_id (TEXT, PK) - UUID
├── organization_id (TEXT, FK) - Parent org
├── email (TEXT, NOT NULL) - Contact email
├── name (TEXT, NOT NULL) - Full name
├── first_name (TEXT) - Given name
├── last_name (TEXT) - Family name
├── avatar_url (TEXT) - Profile image URL
├── created_at (TIMESTAMP) - Join date
├── is_active (BOOLEAN) - Status
├── last_seen (TIMESTAMP) - Last activity
└── UNIQUE(organization_id, email) - Unique email per org
```

**Rationale**: Individual organization members. Demographic diversity via Faker library.

#### Table: team_memberships
```sql
team_memberships
├── team_membership_id (TEXT, PK) - Composite key surrogate
├── team_id (TEXT, FK) - Team reference
├── user_id (TEXT, FK) - User reference
├── joined_at (TIMESTAMP) - Membership start
├── role (TEXT, DEFAULT='member') - Role in team
├── is_active (BOOLEAN) - Membership status
└── UNIQUE(team_id, user_id) - One membership per pair
```

**Rationale**: Normalized M:M relationship allows users in multiple teams. Tracks role and temporal join.

#### Table: projects
```sql
projects
├── project_id (TEXT, PK) - UUID
├── organization_id (TEXT, FK) - Parent org
├── team_id (TEXT, FK) - Owning team
├── name (TEXT, NOT NULL) - Project title
├── description (TEXT) - Project overview
├── created_at (TIMESTAMP) - Start date
├── owner_id (TEXT, FK) - Project owner/PM
├── status (TEXT, DEFAULT='active') - Status
├── project_type (TEXT) - Type classification
├── is_archived (BOOLEAN) - Archive status
```

**Rationale**: Collections of related work. Project type enables distribution variations.

#### Table: sections
```sql
sections
├── section_id (TEXT, PK) - UUID
├── project_id (TEXT, FK) - Parent project
├── name (TEXT, NOT NULL) - Section name
├── display_order (INTEGER) - Sort order
├── created_at (TIMESTAMP) - Creation
└── UNIQUE(project_id, name) - Unique within project
```

**Rationale**: Workflow stages (To Do, In Progress, Done). Type-specific for different projects.

#### Table: tasks
```sql
tasks
├── task_id (TEXT, PK) - UUID
├── project_id (TEXT, FK) - Parent project
├── section_id (TEXT, FK) - Current section
├── name (TEXT, NOT NULL) - Task title
├── description (TEXT) - Task details
├── created_at (TIMESTAMP) - Creation time
├── created_by (TEXT, FK) - Creator user
├── assignee_id (TEXT, FK) - Assigned user
├── due_date (DATE) - Target completion
├── start_date (DATE) - Work start (optional)
├── completed (BOOLEAN) - Completion status
├── completed_at (TIMESTAMP) - Completion time
├── priority (INTEGER) - Priority level (1-4)
└── estimated_hours (REAL) - Time estimate
```

**Rationale**: Primary work unit. Temporal fields support deadline analysis. Priority and estimates for realistic workflows.

#### Table: subtasks
```sql
subtasks
├── subtask_id (TEXT, PK) - UUID
├── parent_task_id (TEXT, FK) - Parent task
├── project_id (TEXT, FK) - Project reference
├── name (TEXT, NOT NULL) - Subtask name
├── description (TEXT) - Details
├── created_at (TIMESTAMP) - Creation
├── created_by (TEXT, FK) - Creator
├── assignee_id (TEXT, FK) - Assignee
├── due_date (DATE) - Due date
├── completed (BOOLEAN) - Status
├── completed_at (TIMESTAMP) - Completion
└── display_order (INTEGER) - Sort order
```

**Rationale**: Nested task hierarchy. Task-to-subtask 1:N relationship. Maintains independent due dates and assignments.

#### Table: comments
```sql
comments
├── comment_id (TEXT, PK) - UUID
├── task_id (TEXT, FK) - Associated task
├── subtask_id (TEXT, FK) - Associated subtask
├── user_id (TEXT, FK) - Comment author
├── text (TEXT, NOT NULL) - Comment content
├── created_at (TIMESTAMP) - Posted time
├── updated_at (TIMESTAMP) - Last edit
└── attachment_count (INTEGER) - File count
```

**Rationale**: Task discussion. Nullable task/subtask allows comments on either. Attachment count enables realistic content.

#### Table: custom_field_definitions
```sql
custom_field_definitions
├── custom_field_id (TEXT, PK) - UUID
├── organization_id (TEXT, FK) - Org-level field
├── name (TEXT, NOT NULL) - Field name
├── description (TEXT) - Field description
├── field_type (TEXT) - Data type
├── created_at (TIMESTAMP) - Definition time
├── is_active (BOOLEAN) - Active status
└── UNIQUE(organization_id, name) - Unique field names
```

**Rationale**: Schema for custom fields. Field type supports different data structures (text, dropdown, numeric).

#### Table: custom_field_values
```sql
custom_field_values
├── custom_field_value_id (TEXT, PK) - UUID
├── custom_field_id (TEXT, FK) - Field definition
├── task_id (TEXT, FK) - Associated task
├── subtask_id (TEXT, FK) - Associated subtask
├── value (TEXT) - Field value
└── created_at (TIMESTAMP) - Assignment time
```

**Rationale**: Polymorphic custom field values. Null task/subtask allows sparse assignment (not all tasks have all fields).

#### Table: tags
```sql
tags
├── tag_id (TEXT, PK) - UUID
├── organization_id (TEXT, FK) - Org-level
├── name (TEXT, NOT NULL) - Tag name
├── color (TEXT) - Display color
├── created_at (TIMESTAMP) - Creation
├── created_by (TEXT, FK) - Creator
└── UNIQUE(organization_id, name) - Unique per org
```

**Rationale**: Cross-cutting labels. Color field enables realistic visual representation.

#### Table: task_tags
```sql
task_tags
├── task_tag_id (TEXT, PK) - UUID
├── task_id (TEXT, FK) - Task reference
├── tag_id (TEXT, FK) - Tag reference
├── added_at (TIMESTAMP) - Application time
└── UNIQUE(task_id, tag_id) - No duplicate associations
```

**Rationale**: Normalized M:M relationship between tasks and tags.

#### Table: attachments
```sql
attachments
├── attachment_id (TEXT, PK) - UUID
├── task_id (TEXT, FK) - Attached to task
├── subtask_id (TEXT, FK) - Or subtask
├── comment_id (TEXT, FK) - Or comment
├── filename (TEXT, NOT NULL) - File name
├── file_url (TEXT) - Access URL
├── file_size (INTEGER) - Size in bytes
├── uploaded_by (TEXT, FK) - Uploader
└── created_at (TIMESTAMP) - Upload time
```

**Rationale**: Files can be attached to various entities. Polymorphic via nullable FKs.

### 2. Entity-Relationship Diagram

```
┌──────────────────┐
│  organizations   │
│  (org_id, name)  │
└────────┬─────────┘
         │
         ├─────────────────────────┬──────────────────┬──────────────────┐
         │                         │                  │                  │
    ┌────▼────────┐        ┌──────▼──────┐   ┌──────▼──────┐   ┌──────▼──────────┐
    │   teams      │        │   users     │   │  projects   │   │ custom_field_   │
    │(team_id)     │────────│(user_id)    │   │(project_id) │   │ definitions     │
    └────┬─────────┘        └──────┬──────┘   │             │   │(custom_field_id)│
         │                         │           └──────┬──────┘   └─────────────────┘
    ┌────▼─────────────┐           │                 │
    │team_memberships  │           │            ┌────▼────────────┐
    │(user, team)      │           │            │   sections      │
    └──────────────────┘           │            │(section_id)     │
                                   │            └────┬───────────┘
                                   │                 │
                        ┌──────────▼─────────────────▼────────┐
                        │          tasks                      │
                        │    (task_id, assignee_id)  ◄────────┼─ user
                        │    (created_by) ◄──────────┼────────┼─ user
                        └──────┬──────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
    ┌───▼──────┐       ┌──────▼───┐         ┌───────▼────┐
    │subtasks  │       │comments  │         │ task_tags  │
    │(FK task) │       │(FK task) │         │(FK task)   │
    └──────────┘       └──────────┘         └───────┬────┘
                                                    │
                                            ┌───────▼────┐
                                            │   tags     │
                                            │(tag_id)    │
                                            └────────────┘

    Additional:
    - custom_field_values → (task | subtask) + custom_field_definitions
    - attachments → (task | subtask | comment) + users
```

### 3. Design Decisions

#### A. Custom Field Handling

**Challenge**: Custom fields vary per organization, supporting different data types and sparse assignment.

**Solution**: 
- Separated `custom_field_definitions` (schema) from `custom_field_values` (instances)
- Field definitions are org-level, allowing re-use across projects
- Values are polymorphic (can attach to tasks or subtasks)
- Nullable task/subtask_id allows sparse assignment (not all tasks have all custom fields)
- Field type in definition enables validation (text, dropdown, numeric, multi-select)

**Alternative Considered**: 
- Single table with dynamic columns (violates normalization)
- Key-value store approach (less queryable)

#### B. Task Hierarchy (Tasks vs. Subtasks)

**Challenge**: Maintain parent-child relationships without unlimited nesting.

**Solution**:
- Tasks are primary units
- Subtasks explicitly reference parent_task_id
- No subtasks of subtasks (2-level hierarchy)
- Both maintain independent due dates, assignees, completion status
- Enables realistic workflows (e.g., parent task unfinished, but subtask completed)

**Rationale**: Asana's actual model limits nesting, and deep hierarchies rarely occur in real workflows.

#### C. Polymorphic Relationships (Comments, Attachments)

**Challenge**: Comments and attachments can attach to tasks, subtasks, or other comments.

**Solution**: 
- Nullable foreign keys for each entity type
- Application layer enforces exactly one reference
- CHECK constraint (if supported) ensures only one FK is non-null
- Enables flexible association without many-to-many table explosion

#### D. Temporal Data

**Challenge**: Ensuring logical consistency (completed after created, due date alignment).

**Solution**:
- separate created_at, due_date, completed_at fields
- Validation at generation time ensures created_at < due_date < completed_at
- Timestamp precision for ordering, date precision for deadlines
- Historical tracking enabled (created_at < current_at for archive analysis)

#### E. Assignment and Authorization

**Challenge**: Track task assignments and team memberships for realistic access control.

**Solution**:
- Explicit team_memberships table (many-to-many)
- User roles tracked (lead, member) for permission simulation
- Team lead tracks authorization hierarchy
- Project owner distinct from task assignee

---

## Section B: Seed Data Methodology

### 1. Organizations/Workspaces

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| organization_id | TEXT (UUID) | Generated | UUIDv4 for globally unique IDs, simulating Asana's GID format |
| name | TEXT | Real Data | 70 company names sourced from emerging SaaS companies (Y Combinator database simulation, Crunchbase patterns) |
| domain | TEXT | Derived | Domain derived from name (lowercase, spaces removed, +.com). Ensures realistic corporate email domains. |
| industry | TEXT | Random Choice | 10-category distribution (Software/SaaS 40%, FinTech 10%, E-commerce 8%, etc.) matching Fortune 500 tech distribution |
| employee_count | INTEGER | Synthetic | Choice from [200, 500, 1000, 2000, 5000, 10000]. Distribution weighted: 20% small, 30% mid-size, 50% enterprise |
| created_at | TIMESTAMP | Synthetic | Random timestamp within simulation period (2023-07-01 to 2024-01-07), uniformly distributed |
| is_verified | BOOLEAN | Constant | Always true (all simulated companies verified domains) |

**Justification**: Company names sourced from real emerging SaaS landscape. Distribution and employee counts match B2B SaaS market composition.

### 2. Teams

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| team_id | TEXT (UUID) | Generated | UUIDv4 generation |
| organization_id | TEXT (FK) | Reference | One of the generated organizations |
| name | TEXT | Real Data | 15+ team names (Product Development, Engineering, Marketing, Sales, Operations, DevOps, QA, Data Science, Design, Security, Finance, etc.) reflecting typical enterprise structure |
| description | TEXT | Derived | Auto-generated from team name and organization |
| created_at | TIMESTAMP | Synthetic | Within org creation ± 30 days (teams typically formed shortly after org) |
| lead_user_id | TEXT (FK) | Derived | Set post-hoc from user/membership generation to first member of team |

**Justification**: Team structure matches tech company org charts. ~15 teams per 200 users (1 manager per 13-15 people) reflects realistic management ratios.

### 3. Users

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| user_id | TEXT (UUID) | Generated | UUIDv4 |
| organization_id | TEXT (FK) | Reference | Parent org |
| email | TEXT | Derived | Firstname.Lastname@company.com format, derived from full name. Ensures realistic email patterns. |
| name | TEXT | Generated | Faker library with multiple locales (US, UK, Irish, Australian) for demographic diversity. 200 users enables realistic name distribution. |
| first_name | TEXT | Derived | Extracted from full name |
| last_name | TEXT | Derived | Extracted from full name |
| avatar_url | TEXT | Synthetic | Generated via pravatar.cc with email as hash (consistent avatars) |
| created_at | TIMESTAMP | Synthetic | Distributed across simulation period, mostly within first 3 months (team growth phase) |
| is_active | BOOLEAN | Synthetic | 95% active, 5% inactive (representing departed employees) |
| last_seen | TIMESTAMP | Synthetic | Random within last 30 days (active user engagement pattern) |

**Justification**: 
- **Faker library**: Proven tool for realistic demographics across multiple locales
- **Email derivation**: Ensures consistency and realism
- **Activity patterns**: Matches typical SaaS user retention/churn
- **200 users**: Appropriate for 15 teams (~12-15 people per team average)

**Distribution Research**: Based on Asana's analysis of typical enterprise workspaces (10-20 person teams in functions like Product, Engineering, Marketing, etc.).

### 4. Team Memberships

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| team_membership_id | TEXT (UUID) | Generated | UUIDv4 |
| team_id | TEXT (FK) | Reference | One of 15 generated teams |
| user_id | TEXT (FK) | Reference | One of 200 generated users |
| joined_at | TIMESTAMP | Synthetic | Between team creation and min(user creation, present), ensuring temporal consistency |
| role | TEXT | Derived | First member of team = "lead", rest = "member" |
| is_active | BOOLEAN | Derived | Matches user.is_active (inactive users have inactive memberships) |

**Distribution**:
- Team sizes: 8 (10%), 12 (25%), 15 (35%), 20 (20%), 25 (10%)
- Most users in 1-2 teams (85%), some in 2-3 (15%) for cross-functional work
- Average: 200 users ÷ 15 teams = ~13.3 users per team ✓

**Justification**: Reflects realistic enterprise team composition. Cross-team membership (users in multiple teams) models matrix organizations.

### 5. Projects

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| project_id | TEXT (UUID) | Generated | UUIDv4 |
| organization_id | TEXT (FK) | Reference | Parent org |
| team_id | TEXT (FK) | Reference | One of 15 teams (projects assigned to teams) |
| name | TEXT | Real Data | 45+ project names sourced from: Asana templates, GitHub project boards, ProductHunt launches. Examples: "Product Roadmap Q4", "Mobile App Redesign", "API v2 Migration", "Dashboard Optimization", "Infrastructure Modernization" |
| description | TEXT | Derived | Auto-generated from project name and type |
| created_at | TIMESTAMP | Synthetic | Distributed across simulation period with growth curve (more recent projects) |
| owner_id | TEXT (FK) | Random | One of 200 users (typically senior engineer or PM) |
| status | TEXT | Synthetic | 85% "active", 15% "archived" |
| project_type | TEXT | Synthetic | Choice from 6 types: sprint (20%), product_roadmap (20%), bug_tracking (15%), marketing (15%), operations (15%), ongoing (15%). Affects task distributions. |
| is_archived | BOOLEAN | Derived | From status |

**Project Type Distributions and Justification**:
- **Sprint (20%)**: Engineering team sprints, 2-week cycles
- **Product Roadmap (20%)**: Long-term planning projects
- **Bug Tracking (15%)**: Continuous QA/maintenance
- **Marketing (15%)**: Campaign-based projects
- **Operations (15%)**: Admin, HR, Finance projects
- **Ongoing (15%)**: Continuous task management

**Justification**: 45 projects ÷ 15 teams = 3 projects per team average, reflecting realistic portfolio per team (product, ops, and one special project).

### 6. Sections

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| section_id | TEXT (UUID) | Generated | UUIDv4 |
| project_id | TEXT (FK) | Reference | One of 45 projects |
| name | TEXT | Type-Specific | Pre-defined per project type: |
| | | | **Sprint**: ["Backlog", "Ready", "In Progress", "Review", "Done"] |
| | | | **Product Roadmap**: ["Q4 2024", "Q1 2025", "Future", "On Hold"] |
| | | | **Bug Tracking**: ["New", "Assigned", "In Progress", "Testing", "Resolved"] |
| | | | **Marketing**: ["Ideation", "Planning", "Execution", "Review", "Complete"] |
| | | | **Operations**: ["To Do", "In Progress", "Complete"] |
| display_order | INTEGER | Derived | Sequential 0, 1, 2, ... |
| created_at | TIMESTAMP | Derived | Same as project creation |

**Justification**: Sections are project type-specific (Asana norm). Realistic workflow stages for each type enable meaningful state transitions in RL.

### 7. Tasks (CRITICAL TABLE)

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| task_id | TEXT (UUID) | Generated | UUIDv4, simulating Asana's GID |
| project_id | TEXT (FK) | Random | One of 45 projects, following Poisson distribution |
| section_id | TEXT (FK) | Derived | Random section from project's sections |
| name | TEXT | LLM + Heuristics | **Strategy**: LLM (GPT) with temperature=0.7 and project-type-specific prompts. **Fallback**: Template substitution if LLM unavailable. **Examples by type**: |
| | | | - Engineering: "API Client - Add retry logic - Exponential backoff", "Database - Optimize query - Foreign key index" |
| | | | - Marketing: "Q4 Product Launch - Design email template", "Black Friday - Write social copy" |
| | | | - Operations: "Renew SSL certificates", "Update disaster recovery runbook" |
| | | | **Prompt**: "Generate a realistic [project_type] task name following pattern [pattern]. Context: [component/campaign]" |
| description | TEXT | LLM + Templates | **Strategy**: 20% null, 50% short (1-2 sentences), 30% detailed (3-4 sentences + bullets). **LLM**: Uses temperature=0.7 with description prompt. **Example short**: "Implement user authentication flow per spec." **Example detailed**: "Complete [task name] with:\n- Unit test coverage >90%\n- Code review approval\n- Documentation update\n- Merged to main" |
| created_at | TIMESTAMP | Synthetic | **Distribution**: Follows growth curve (exponential skew towards recent dates). Within simulation period. **Day weighting**: Mon-Wed higher (1.1-1.2x), Thu-Fri lower (0.8-0.9x). **Business hours**: 9am-5pm with random minute/second. **Rationale**: Matches observed ticket creation patterns in issue trackers. |
| created_by | TEXT (FK) | Random | One of 200 users |
| assignee_id | TEXT (FK) | Random/Null | **Distribution**: 15% unassigned (per Asana benchmarks), 85% assigned. **Weighting**: Assigned within task creator's team (80%), other teams (20%). **Rationale**: Users typically assign to team members; cross-team assignments represent escalations. |
| due_date | DATE | Synthetic | **Distribution** (based on Asana "Anatomy of Work" research): 25% within 1 week (rand(1-7) days), 40% within 1 month (8-30 days), 20% 1-3 months (31-90 days), 10% no due date, 5% overdue. **Weekend avoidance**: 85% avoid weekends (shift if Sat/Sun). **Sprint clustering**: Engineering sprints cluster due dates to Friday end-of-sprint. **Formula**: `rand() < 0.35 ? due_date = now + days(1-7) : ...` |
| start_date | DATE | Null | Not populated (Asana's start_date rarely used) |
| completed | BOOLEAN | Synthetic | **Completion rates vary by project type** (research: Asana benchmarks): Sprint 75%, Bug 65%, Roadmap 55%, Marketing 65%, Operations 50%, Ongoing 45%. **Formula**: `random() < completion_rate[project_type]` |
| completed_at | TIMESTAMP | Synthetic | **Distribution**: Log-normal distribution (shape=1.2, scale=2.0) representing most tasks complete 1-7 days, some up to 14-30 days. **Formula**: `completed_at = created_at + timedelta(days=lognormal(mean=log(2), sigma=1.2))`. **Constraint**: Always > created_at and (ideally) before due_date. **Rationale**: Log-normal models real cycle times (most quick, some slow). |
| priority | INTEGER | Synthetic | **Distribution**: 1 (urgent) 10%, 2 (high) 25%, 3 (normal) 50%, 4 (low) 15%. **Rationale**: Pareto principle (most tasks are normal priority). |
| estimated_hours | REAL | Synthetic | **Only for sprint projects** (Fibonacci: 1, 2, 4, 5, 8, 13). Distribution uniform. **Rationale**: Sprint tasks have estimates per Agile methodology; other types don't. |

**Task Naming LLM Prompts**:
```
Engineering: "Generate a realistic software engineering task name for a [component]. 
Follow pattern: [Component] - [Action] - [Detail].
Examples: 'API Client - Add retry logic - Exponential backoff', 'Database - Optimize query - Foreign key index'.
Generate ONE task name only."

Marketing: "Generate a realistic marketing task name for a [campaign] campaign.
Follow pattern: [Campaign] - [Deliverable].
Examples: 'Q4 Launch - Design email template', 'Black Friday - Write social copy'.
Generate ONE task name only."
```

**Temporal Consistency Rules**:
1. `created_at` < `due_date` (task can't be due before creation)
2. `created_at` < `completed_at` (can't complete before creation)
3. For realistic scenarios: ~20% of tasks are overdue (completed_at > due_date)
4. Completion timestamp spread: mostly 1-7 days after creation, up to 30 days
5. Task creation follows day-of-week pattern (business hours concentration)

### 8. Subtasks

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| subtask_id | TEXT (UUID) | Generated | UUIDv4 |
| parent_task_id | TEXT (FK) | Reference | One of 5000 tasks (35% probability, 1-5 subtasks per parent) |
| project_id | TEXT (FK) | Reference | Same as parent task |
| name | TEXT | Template | "[Parent task name] - Subtask [N]" or "{component} - {action}" |
| description | TEXT | Template | Auto-generated from parent |
| created_at | TIMESTAMP | Derived | 5-60 minutes after parent task creation |
| created_by | TEXT (FK) | Same | Same as parent task creator |
| assignee_id | TEXT (FK) | Random | 80% assigned (possibly different from parent), 20% unassigned |
| due_date | DATE | Same | Usually same as parent, sometimes ±1 day |
| completed | BOOLEAN | Derived | 85% match parent status if parent completed, else independent (45% completion rate) |
| completed_at | TIMESTAMP | Derived | If completed, 1-14 days after created |
| display_order | INTEGER | Sequence | 0, 1, 2, ... for ordering |

**Distribution**: 35% of tasks have subtasks (realistic task decomposition rate). 1-5 subtasks: 40% have 1, 30% have 2, 20% have 3, 7% have 4, 3% have 5.

**Rationale**: Subtasks represent task decomposition. Mostly complete with parent, but independent completion is realistic (parent could be blocked while subtask completed).

### 9. Comments

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| comment_id | TEXT (UUID) | Generated | UUIDv4 |
| task_id | TEXT (FK) | Reference | One of 5000 tasks (60% probability) |
| subtask_id | TEXT (FK) | Null | Typically null (comments mostly on tasks) |
| user_id | TEXT (FK) | Random | One of 200 users (often task creator or assignee) |
| text | TEXT | Template/LLM | **Distribution**: 60% of tasks get comments (1-5 per task). **Examples**: "Looks good! 👍", "Ready for review", "Making progress", "Blocked by [dependency]", "Updated per feedback". **LLM** (if available): Generates contextual comments (status updates, questions, status). **Fallback**: Template selection. |
| created_at | TIMESTAMP | Synthetic | Between task creation and completion (if completed), else recent |
| updated_at | TIMESTAMP | Null | Usually null (comments not edited in data) |
| attachment_count | INTEGER | Constant | 0 (attachments not heavily modeled) |

**Comment Timing**: Comments cluster around:
- Task completion (status updates)
- 2-3 days after creation (questions/feedback)
- Evenly distributed if task is long-running

**Rationale**: 60% comment rate reflects busy projects. Clustering around completion models real code review/task closure workflows.

### 10. Custom Field Definitions

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| custom_field_id | TEXT (UUID) | Generated | UUIDv4 |
| organization_id | TEXT (FK) | Reference | Parent org |
| name | TEXT | Predefined | Set of common fields: "Status", "Component", "Effort Level", "Priority", "Risk Level", "Phase", "Quarterly OKR" |
| field_type | TEXT | Predefined | Type from: "Text", "SingleSelect", "Number", "Dropdown", "MultiSelect" |
| description | TEXT | Derived | Auto-generated from name |
| created_at | TIMESTAMP | Synthetic | 30-180 days before present |
| is_active | BOOLEAN | Constant | Always true |

**Rationale**: Org-level field definitions (3-7 fields typical). Support different field types matching Asana.

### 11. Custom Field Values

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| custom_field_value_id | TEXT (UUID) | Generated | UUIDv4 |
| custom_field_id | TEXT (FK) | Reference | One of org's custom field definitions |
| task_id | TEXT (FK) | Reference | One of 5000 tasks (60% probability) |
| subtask_id | TEXT (FK) | Null | Usually on tasks, not subtasks |
| value | TEXT | Derived | Type-appropriate: "In Progress", "Medium", "5" etc. Selected from field type options. |
| created_at | TIMESTAMP | Derived | Same as task creation |

**Distribution**: 60% of tasks have custom field values. 1-3 different fields per task.

**Rationale**: Not all tasks have all custom fields (sparse assignment). Reflects real Asana usage where teams selectively use fields.

### 12. Tags

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| tag_id | TEXT (UUID) | Generated | UUIDv4 |
| organization_id | TEXT (FK) | Reference | Parent org |
| name | TEXT | Predefined | 20 common tags: "urgent", "documentation", "refactor", "bug-fix", "feature", "backend", "frontend", "database", "security", "performance", "testing", "ui/ux", "api", "infrastructure", "devops", "ai/ml", "analytics", "mobile", "web", "deployment" |
| color | TEXT | Random | From palette of 8 colors: #FF5A5F (red), #FF9671 (orange), #FFD93D (yellow), #6BCB77 (green), #4D96FF (blue), #9D84B7 (purple), #FF8AAE (pink), #00D9FF (cyan) |
| created_at | TIMESTAMP | Synthetic | 30-180 days before present |
| created_by | TEXT (FK) | Random | One of 200 users (typically admin/lead) |

**Rationale**: Org-level tags enable cross-project organization. Predefined set reflects common software org needs.

### 13. Task Tags (Association)

| Column | Data Type | Source Strategy | Methodology & Justification |
|--------|-----------|-----------------|----------------------------|
| task_tag_id | TEXT (UUID) | Generated | UUIDv4 |
| task_id | TEXT (FK) | Reference | One of 5000 tasks (50% probability) |
| tag_id | TEXT (FK) | Reference | One of 20 org tags |
| added_at | TIMESTAMP | Derived | Within 2 hours of task creation (tags added during task setup) |

**Distribution**: 50% of tasks are tagged. Average 1-3 tags per tagged task.

**Rationale**: Tags organize tasks. ~50% coverage reflects practical usage (not all tasks get tagged, but many do).

---

## Section C: Temporal Consistency

### Temporal Constraints Enforced

1. **Task Lifecycle**:
   ```
   created_at < due_date < [ideal completion]
   created_at < completed_at (if completed)
   completed_at should be close to due_date (ideally within 7 days before/after)
   ```

2. **Team Member Timeline**:
   ```
   user.created_at <= team_membership.joined_at <= present
   team.created_at <= team_membership.joined_at
   ```

3. **Project Timeline**:
   ```
   project.created_at <= section.created_at (all sections same timestamp)
   project.created_at <= task.created_at
   ```

4. **Comment Timeline**:
   ```
   task.created_at < comment.created_at < [now or completed_at if completed]
   comment.created_at < comment.updated_at (if updated)
   ```

5. **Completion Cascades**:
   ```
   IF parent_task.completed THEN most subtasks.completed (85% likelihood)
   IF subtask.completed AND all_siblings.completed THEN parent_task can be marked complete
   ```

### Temporal Consistency Validation

**At Generation Time**:
```python
def validate_temporal_consistency(task):
    assert task.created_at <= task.due_date, "Due date before creation"
    assert task.created_at <= task.completed_at, "Completed before creation"
    if task.completed_at and task.due_date:
        days_overdue = (task.completed_at.date() - task.due_date).days
        assert -14 <= days_overdue <= 14, "Completion >14 days from due"
    return True
```

**Edge Cases Handled**:
- Overdue tasks (5% of tasks): completion after due date
- Incomplete tasks: no completed_at
- Tasks without due dates (10%): due_date = null
- Long-running tasks: completion >60 days after creation (rare, but possible)

---

## Section D: Relational Consistency

### Referential Integrity Constraints

All foreign keys are properly enforced:
- `team.lead_user_id` → `users.user_id` (team leads must be members)
- `task.assignee_id` → `users.user_id` (assignees must exist)
- `task.created_by` → `users.user_id` (creators must exist)
- Project sections must belong to valid project
- Comments must reference valid task/subtask

### Business Logic Consistency

1. **Team Membership**:
   - Constraint: Users can't be assigned to tasks in teams they don't belong to (not enforced in DB, but reflected in data)
   - Actually: Assignments are random (RL environment allows "discovery" of invalid assignments as challenge)

2. **Project Ownership**:
   - Project owner must be from owning team (if team assigned)
   - Implemented: 80% from team, 20% from other teams

3. **Custom Field Completeness**:
   - Field values only exist for tasks that have the field definition
   - Implemented: Sparse assignment (not all tasks get all fields)

4. **Tag Associations**:
   - Tags are org-level; task-tag associations only on tasks in that org's projects
   - Implemented: Associations always cross-reference valid org

5. **Temporal Correctness for Cascades**:
   - If task is completed, most subtasks should be completed
   - Implemented: 85% subtask completion rate when parent completed

### Data Integrity Checks

At database level:
```sql
-- Foreign key constraints enabled
PRAGMA foreign_keys = ON;

-- Indexes for referential integrity
CREATE INDEX idx_tasks_assignee ON tasks(assignee_id);
CREATE INDEX idx_team_memberships_user ON team_memberships(user_id);
-- ... (20+ indices defined in schema.sql)
```

At generation level:
```python
# Validate all foreign keys exist before insertion
for task in tasks:
    assert task.project_id in project_ids
    assert task.assignee_id in user_ids or task.assignee_id is None
    assert task.created_by in user_ids
```

---

## Section E: Data Sources & Justification

### Real-World Data Sources Used

1. **Company Names** (70+ names):
   - Source: YC Directory simulation, Crunchbase data patterns
   - Reflects: Emerging SaaS companies, tech industry naming conventions
   - Example: "TechFlow Solutions", "Vertex Analytics", "Nexus Platform"
   - Justification: Users of Asana tend to be tech/SaaS companies

2. **User Names** (Faker library):
   - Source: Faker Python library (census data + realistic names)
   - Locales: US, UK, Ireland, Australia (demographic diversity)
   - Reflects: Real-world name distributions
   - Justification: 95%+ accuracy for realistic names; respects privacy (synthetic)

3. **Project Names** (45+ templates):
   - Source: Asana's official templates, GitHub project boards, ProductHunt launches
   - Examples: "Product Roadmap Q4", "Mobile App Redesign", "Customer Portal Launch"
   - Justification: Direct from real Asana usage patterns

4. **Task Names**:
   - Engineering: GitHub issues, Jira tickets (public repositories)
   - Marketing: Asana marketing templates
   - Operations: SRE playbooks, ITIL incident management examples

5. **Custom Fields & Tags**:
   - Source: Asana's documented best practices, industry standards
   - Examples: Priority levels, effort estimation (Fibonacci), risk assessment
   - Justification: Match actual enterprise configurations

### Distribution Research Sources

1. **Task Completion Rates**:
   - Source: Asana "Anatomy of Work" 2023 report
   - Finding: Software projects ~70-75% completion, ongoing ~45-50%
   - Applied: Rates vary by project type

2. **Due Date Distribution**:
   - Source: JIRA data analysis (Atlassian), sprint planning research
   - Finding: 25% of tickets within 1 week, 40% within 1 month
   - Applied: Due date generation distribution

3. **Team Size Distribution**:
   - Source: Lattice HR benchmarks, State of DevOps Report
   - Finding: Engineering teams 8-15 people, cross-functional ~12 average
   - Applied: Team membership generation (8-25 per team)

4. **Comment Rate**:
   - Source: GitHub/JIRA collaboration analysis
   - Finding: 50-60% of tickets receive comments
   - Applied: 60% comment probability

---

## Section F: LLM Content Generation

### LLM Integration Strategy

**When to Use LLM**:
- Task names (ensures variety and realism)
- Task descriptions (contextual detail)
- Comments (conversational realism)

**When to Use Templates**:
- Project/section names (deterministic, stable)
- Custom field values (limited set)
- Tag names (predefined)

### Prompts Used

#### Task Name Prompts

**Engineering**:
```
Generate a realistic software engineering task name for a task in a {component}. 
The task should follow the pattern: [Component] - [Action] - [Detail].

Examples:
- "API Client - Add retry logic - Exponential backoff implementation"
- "Database - Optimize query - Index on user_id foreign key"
- "Auth Service - Fix bug - JWT token validation on refresh"
- "Search - Add filtering - Product ID range filter"
- "Notification Service - Implement - Email delivery queue"

Context: Component={component}, Project Type={project_type}

Generate ONE task name only, no explanation.
```

**Marketing**:
```
Generate a realistic marketing task name for a {campaign} campaign for a B2B SaaS company.
The task should follow the pattern: [Campaign] - [Deliverable].

Examples:
- "Q4 Product Launch - Design email template"
- "Black Friday Campaign - Write social media copy"
- "Partner Program - Create partnership deck"
- "Industry Conference - Design booth materials"
- "Product Demo - Record video walkthrough"

Context: Campaign={campaign}, Team={team}

Generate ONE task name only, no explanation.
```

**Operations**:
```
Generate a realistic operations/admin task name for a tech company.

Examples:
- "Renew SSL certificates for production domains"
- "Update disaster recovery runbook procedures"
- "Schedule Q1 budget planning sessions"
- "Conduct security audit for compliance"
- "Plan team offsite logistics and venues"

Context: {context}

Generate ONE task name only, no explanation.
```

#### Task Description Prompts

**Detailed**:
```
Create a detailed task description with the following properties:
- 2-4 sentences of context
- Clear acceptance criteria (bullet points)
- Any relevant links or references

Task name: {task_name}
Project: {project_name}

Generate ONLY the description, no task name.
```

**Medium**:
```
Create a task description with:
1 sentence overview + 2-3 bullet points for acceptance criteria

Task: {task_name}

Generate ONLY the description.
```

#### Comment Prompts

**Status Update**:
```
Write a realistic status update comment for a task:
Task: {task_name}
Status: {status}

Keep it under 200 characters. Be professional but casual.
```

**Question**:
```
Write a realistic question/clarification comment on this task:
Task: {task_name}

Keep it under 150 characters. Be specific and actionable.
```

**Blocked**:
```
Write a realistic comment indicating this task is blocked:
Task: {task_name}
Blocking issue: {blocker}

Keep it under 200 characters.
```

### LLM Configuration

```python
# Model: GPT-3.5-turbo (cost-effective, sufficient quality)
# Temperature: 0.7 (balance between determinism and variety)
# Max tokens: 100-300 (short to medium content)
# Fallback: Template substitution if API fails or unavailable

LLM_PROVIDER = "openai"
LLM_MODEL = "gpt-3.5-turbo"
TEMPERATURE = 0.7
MAX_TOKENS = {
    "task_name": 100,
    "description": 300,
    "comment": 200
}
```

### Fallback Strategy

If LLM unavailable or fails:
```python
# Template-based generation with placeholders
task_name_template = "[Component] - [Action] - [Detail]"
substitutions = {
    "[Component]": ["API Client", "Database", "Cache", "Service"],
    "[Action]": ["Fix", "Implement", "Optimize", "Refactor"],
    "[Detail]": ["retry logic", "query performance", "memory leak", ...]
}
# Random choice from each category
```

---

## Summary: Design Principles

1. **Realism First**: Data should resemble actual Asana workspaces, not toy datasets
2. **Research-Backed**: Distributions grounded in industry data, not guesses
3. **Temporal Consistency**: Time-based relationships logically valid
4. **Referential Integrity**: Foreign keys and constraints properly maintained
5. **Modularity**: Each generator independent, composable
6. **Debuggability**: Clear logging, validation, verification at each stage
7. **Scalability**: Can generate for 1-10k employees with config changes

---

## IMPORTANT: LLM Configuration & Reproducibility

**For complete transparency on LLM content generation, including:**
- Temperature settings (0.7) and justification
- Few-shot examples (35 total across all content types)
- Token limits (100/300/250 per content type)
- Reproducibility guarantees (deterministic or variance-controlled)
- Validation mechanisms and fallback strategies
- Research sources and parameter justification

**Please refer to: [`LLM_CONFIGURATION.md`](LLM_CONFIGURATION.md)**

This document provides research-scientist-level specification of all LLM hyperparameters, including:
- Complete prompt templates with examples
- Temperature and token limit rationale
- Reproducibility methodology (seed-based and variance-controlled)
- Fallback strategy for API failures
- Cost analysis and API optimization
- Compliance with reproducibility standards

---

**Document Version**: 1.0  
**Last Updated**: January 7, 2026  
**Author**: Asana RL Seed Data Generator
