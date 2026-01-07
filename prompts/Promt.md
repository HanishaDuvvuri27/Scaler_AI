# LLM Content Generation Configuration

## Professional LLM Usage

We used LLM as a **development tool with human oversight**, not as decision authority:

✅ **Our approach:**
- Defined all design decisions based on research and requirements
- Used LLM for implementation with code review
- Validated all outputs against quality criteria
- Maintained complete control over data generation

❌ **What we didn't do:**
- Blindly follow LLM suggestions
- Accept outputs without validation
- Delegate design decisions to LLM

---

## 1. LLM Configuration

### Model Setup
```python
Provider:          OpenAI
Model:             gpt-3.5-turbo
Temperature:       0.7          # Balanced creativity with consistency
Max Tokens:
  - Task names:    100 tokens
  - Descriptions:  300 tokens
  - Comments:      250 tokens
Timeout:           30 seconds
Fallback:          Template-based generation (deterministic)
```

---

## 2. How We Ensure Variety

### Temperature = 0.7
- **0.0**: Too deterministic (repetitive)
- **0.7**: Sweet spot - realistic variety with semantic consistency ✓
- **1.0+**: Too creative (generates nonsense)

**Example:** Same prompt generates different but realistic outputs:
```
Input: "Generate task for Auth Service"

Output 1: "Auth Service - Implement refresh token logic - JWT expiration"
Output 2: "Auth Service - Add token rotation - Secure credential refresh"
Output 3: "Auth Service - Fix session persistence - Cross-domain tokens"
```

### Few-Shot Examples
Provide pattern anchors for LLM:

**Engineering tasks:**
- "API Client - Add retry logic - Exponential backoff"
- "Database - Optimize query - Index foreign keys"
- "Auth Service - Fix bug - JWT validation"

**Marketing tasks:**
- "Q4 Launch - Design email template"
- "Black Friday - Write social media copy"
- "Partner Program - Create presentation deck"

**Operations tasks:**
- "Renew SSL certificates for production"
- "Update disaster recovery procedures"
- "Schedule budget planning sessions"

### Parameterized Prompts
Each prompt uses variables to ensure different content:

```python
prompt = f"""
Generate a task name for {component} in {project_type}.
Pattern: [Component] - [Action] - [Detail]
Context: Team={team}, Priority={priority}
"""
```

---

## 3. Token Limits

| Content | Max Tokens | Why |
|---------|-----------|-----|
| Task Names | 100 | Asana UI limit (~120 chars) |
| Descriptions | 300 | Research: >300 chars rarely read |
| Comments | 250 | Realistic conversation length |

---

## 4. Reproducibility

### Deterministic Mode
```bash
# Set in .env file
RANDOM_SEED=42

# Generate identical database every run
python src/main.py
```

### Variance-Controlled Mode (Default)
```bash
# No seed, temperature=0.7
python src/main.py

# Same structure, different content (±2% variation acceptable)
```

---

## 5. Output Validation

All LLM outputs validated before insertion:
```python
def validate_task_name(name: str) -> bool:
    checks = [
        len(name) <= 120,           # Length constraint
        len(name) >= 10,            # Meaningful content
        not name.startswith(' '),   # Clean whitespace
        '\n' not in name,           # No newlines
        any(c.isalpha() for c in name)  # Has text
    ]
    return all(checks)

# If validation fails → use fallback template
```

---

## 6. Fallback Strategy

If LLM API fails or times out:
```python
# Automatic fallback to template-based generation
if llm_call_fails:
    use_deterministic_templates()
    # Never fails - always produces valid output
```

---

## 7. Example Prompts Used

### Task Name Prompt (Engineering)
```
Generate a realistic engineering task name for a {component}.
Follow pattern: [Component] - [Action] - [Detail]

Examples:
1. API Client - Add retry logic - Exponential backoff
2. Database - Optimize query - Index on user_id

Context: Component={component}, Project={project_type}
Output: ONE task name only
```

### Description Prompt (Medium)
```
Create a task description:
- 1 sentence overview
- 2-3 bullet point acceptance criteria

Task: {task_name}
Project: {project_name}

Example format:
"Optimize dashboard queries.
- Add indexes on frequently queried fields
- Reduce query time by 50%
- Add performance monitoring"
```

### Comment Prompt (Status)
```
Write a brief status update for this task:
Task: {task_name}
Status: {status}

Examples:
- "Pushed implementation to staging, ready for QA"
- "Completed design, awaiting review"
- "80% done, hit one blocker but resolved"

Keep it under 200 characters, professional but casual.
```

---

## 8. Implementation Reference

See `src/utils/llm_client.py` for:
- Prompt template implementation
- Temperature control
- Fallback mechanisms
- Output validation

See `src/generators/tasks.py` for:
- How prompts are used in code
- Validation before insertion
- Fallback generation

---

## Summary

✓ Temperature = 0.7 for realistic variety  
✓ Few-shot examples anchor patterns  
✓ Parameterized prompts ensure variation  
✓ Token limits prevent excessive output  
✓ Output validation ensures quality  
✓ Fallback strategy handles failures  
✓ Reproducibility guaranteed with seed option
