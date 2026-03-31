import json
import os
from groq import Groq
from datetime import date, timedelta

client = Groq(api_key=os.getenv('GROQ_API_KEY', ''))

def generate_schedule(tasks_data: list, user_settings: dict, project_info: dict) -> dict:
    """
    Generate a daily schedule using Groq AI based on tasks, deadlines, and user settings.
    """
    tasks_text = "\n".join([
        f"- Task: {t['title']} | Priority: {t['priority']} | "
        f"Deadline: {t.get('deadline', 'No deadline')} | "
        f"Estimated Hours: {t.get('estimated_hours', 1)} | Status: {t['status']}"
        for t in tasks_data
    ])

    prompt = f"""You are a smart productivity assistant. Generate a detailed daily work schedule.

PROJECT: {project_info.get('title', 'General Tasks')}
Project Deadline: {project_info.get('end_date', 'Not set')}
Today's Date: {date.today().isoformat()}

USER SETTINGS:
- Work hours per day: {user_settings.get('work_hours_per_day', 8)} hours
- Preferred working time: {user_settings.get('preferred_working_time', 'morning')}
- Max tasks per day: {user_settings.get('max_tasks_per_day', 5)}
- Break interval: every {user_settings.get('break_interval_minutes', 60)} minutes

TASKS TO SCHEDULE:
{tasks_text}

Generate a JSON schedule with the following structure:
{{
  "schedule": [
    {{
      "date": "YYYY-MM-DD",
      "day_label": "Day 1 - Monday",
      "tasks": [
        {{
          "task_title": "...",
          "time_slot": "9:00 AM - 11:00 AM",
          "duration_hours": 2,
          "goal": "Specific goal for today",
          "priority": "high"
        }}
      ],
      "total_hours": 6,
      "focus_note": "Today's key focus message"
    }}
  ],
  "summary": "Brief overview of the entire schedule",
  "risk_assessment": "Any deadline risks identified",
  "productivity_tips": ["tip1", "tip2"]
}}

Return ONLY valid JSON, no extra text."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )

    content = response.choices[0].message.content.strip()
    # Clean potential markdown code blocks
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]
    content = content.strip()

    return json.loads(content)


def reschedule_tasks(missed_days: int, remaining_tasks: list, user_settings: dict) -> dict:
    """
    Intelligently reschedule remaining tasks after missed days.
    """
    tasks_text = "\n".join([
        f"- {t['title']} | Priority: {t['priority']} | "
        f"Deadline: {t.get('deadline', 'No deadline')} | "
        f"Est. Hours: {t.get('estimated_hours', 1)}"
        for t in remaining_tasks
    ])

    prompt = f"""You are a smart productivity assistant helping reschedule missed work.

SITUATION: The user missed {missed_days} day(s) of work.
Today's Date: {date.today().isoformat()}

USER SETTINGS:
- Work hours per day: {user_settings.get('work_hours_per_day', 8)} hours
- Max tasks per day: {user_settings.get('max_tasks_per_day', 5)}

REMAINING TASKS:
{tasks_text}

Create a revised schedule to catch up. Prioritize by urgency and deadline risk.

Return JSON:
{{
  "revised_schedule": [
    {{
      "date": "YYYY-MM-DD",
      "tasks": [
        {{
          "task_title": "...",
          "time_slot": "...",
          "duration_hours": 2,
          "adjustment_note": "Why this was rescheduled here"
        }}
      ],
      "catch_up_note": "Strategy note for this day"
    }}
  ],
  "summary": "How the schedule was adjusted",
  "deadline_risks": ["any tasks at risk of missing deadline"],
  "recommendations": ["action1", "action2"]
}}

Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=2000,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]
    content = content.strip()

    return json.loads(content)


def get_task_priority_suggestions(tasks_data: list) -> dict:
    """
    AI-powered task prioritization suggestions.
    """
    tasks_text = "\n".join([
        f"- ID:{t['id']} | {t['title']} | Current Priority: {t['priority']} | Deadline: {t.get('deadline', 'None')}"
        for t in tasks_data
    ])

    prompt = f"""Analyze these tasks and suggest optimal priority ordering.

TASKS:
{tasks_text}

Today: {date.today().isoformat()}

Return JSON:
{{
  "suggestions": [
    {{
      "task_id": 1,
      "task_title": "...",
      "suggested_priority": "high",
      "reason": "Why this priority level",
      "urgency_score": 8
    }}
  ],
  "overall_recommendation": "Brief strategy advice"
}}

Return ONLY valid JSON."""

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
        max_tokens=1000,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith('```'):
        content = content.split('```')[1]
        if content.startswith('json'):
            content = content[4:]

    return json.loads(content.strip())