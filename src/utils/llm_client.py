"""LLM interaction utilities for content generation."""

import random
import json
from typing import Optional


class LLMClient:
    """Wrapper for LLM API calls with caching and fallback."""
    
    def __init__(self, provider='openai', model='gpt-3.5-turbo', api_key=''):
        self.provider = provider
        self.model = model
        self.api_key = api_key
        self.cache = {}
        
        if provider == 'openai':
            try:
                import openai
                openai.api_key = api_key
                self.client = openai
            except ImportError:
                self.client = None
    
    def generate_text(self, prompt: str, temperature: float = 0.7, 
                     max_tokens: int = 200, cache_key: Optional[str] = None) -> str:
        """
        Generate text using LLM.
        Falls back to templates if LLM fails.
        """
        # Check cache first
        if cache_key and cache_key in self.cache:
            return self.cache[cache_key]
        
        if not self.client:
            # Fallback to template-based generation
            return self._generate_with_templates(prompt)
        
        try:
            if self.provider == 'openai':
                response = self.client.ChatCompletion.create(
                    model=self.model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                result = response.choices[0].message.content.strip()
            else:
                result = self._generate_with_templates(prompt)
        except Exception as e:
            print(f"LLM generation failed: {e}. Using fallback.")
            result = self._generate_with_templates(prompt)
        
        if cache_key:
            self.cache[cache_key] = result
        
        return result
    
    def _generate_with_templates(self, prompt: str) -> str:
        """Fallback template-based generation when LLM unavailable."""
        # This will be implemented with realistic templates
        return self._template_generate(prompt)
    
    def _template_generate(self, prompt: str) -> str:
        """Template-based text generation as fallback."""
        # Simple implementation - will be enhanced
        templates = {
            'task_name_engineering': [
                "[Component] - [Action] - [Detail]",
                "Implement [Feature]",
                "Fix [Bug]",
                "Refactor [Module]",
                "Optimize [System]",
                "Add [Functionality] to [Component]",
            ],
            'task_name_marketing': [
                "[Campaign] - [Deliverable]",
                "Create [Content Type] for [Channel]",
                "Launch [Campaign]",
                "Design [Asset]",
                "Write [Content]",
                "[Campaign] - Phase [N]",
            ],
            'task_description': [
                "This task involves working on the [component] to [action].",
                "We need to [action] for [reason].",
                "Update [component] according to [specification].",
                "Implement the following requirements:\n- [requirement1]\n- [requirement2]",
            ]
        }
        
        for key, values in templates.items():
            if key in prompt.lower():
                return random.choice(values)
        
        return "Task description"


class PromptManager:
    """Manages LLM prompts with variations and few-shot examples."""
    
    TASK_NAME_PROMPTS = {
        'engineering': """Generate a realistic software engineering task name for a task in a {component}. 
The task should follow the pattern: [Component] - [Action] - [Detail].
Examples:
- "API Client - Add retry logic - Exponential backoff implementation"
- "Database - Optimize query - Index on user_id foreign key"
- "Auth Service - Fix bug - JWT token validation on refresh"
Context: Component={component}, Project Type={project_type}
Generate ONE task name only, no explanation.""",
        
        'marketing': """Generate a realistic marketing task name for a {campaign} campaign.
The task should follow the pattern: [Campaign] - [Deliverable].
Examples:
- "Q4 Product Launch - Design email template"
- "Black Friday Campaign - Write social media copy"
- "Partner Program - Create partnership deck"
Context: Campaign={campaign}, Team={team}
Generate ONE task name only, no explanation.""",
        
        'operations': """Generate a realistic operations/admin task name.
Examples:
- "Renew SSL certificates for production domains"
- "Update disaster recovery runbook procedures"
- "Schedule Q1 budget planning sessions"
Context: {context}
Generate ONE task name only, no explanation.""",
    }
    
    TASK_DESCRIPTION_PROMPTS = {
        'detailed': """Create a detailed task description with the following properties:
- 2-4 sentences of context
- Clear acceptance criteria (bullet points)
- Any relevant links or references
Task name: {task_name}
Project: {project_name}
Generate ONLY the description, no task name.""",
        
        'minimal': """Create a brief 1-sentence task description for:
{task_name}
Keep it under 100 characters.""",
        
        'medium': """Create a task description with:
1 sentence overview + 2-3 bullet points for acceptance criteria
Task: {task_name}
Generate ONLY the description.""",
    }
    
    COMMENT_PROMPTS = {
        'status_update': """Write a realistic status update comment for a task:
Task: {task_name}
Status: {status}
Keep it under 200 characters. Be professional but casual.""",
        
        'question': """Write a realistic question/clarification comment on this task:
Task: {task_name}
Keep it under 150 characters. Be specific and actionable.""",
        
        'blocked': """Write a realistic comment indicating this task is blocked:
Task: {task_name}
Blocking issue: {blocker}
Keep it under 200 characters.""",
    }
