"""MCP Prompts - Pre-defined prompt templates."""

from __future__ import annotations

from typing import TypedDict


class PromptArgument(TypedDict):
    """Type for prompt argument definition."""

    name: str
    description: str
    required: bool


class PromptData(TypedDict):
    """Type for prompt metadata."""

    name: str
    description: str
    arguments: list[PromptArgument]
    template: str


DAILY_REVIEW_TEMPLATE = """
You are helping the user review their day. Based on the provided date, please:

1. **Summarize the day's activities** using the available tools:
   - Check finance records (income/expenses)
   - Review completed and pending todos
   - Look at health metrics recorded
   - Read daily log entries

2. **Provide insights**:
   - Spending patterns or unusual expenses
   - Task completion rate
   - Health trends or concerns
   - Notable events from daily logs

3. **Suggest improvements**:
   - Budget recommendations if overspending
   - Prioritize overdue tasks
   - Health reminders based on missing metrics

Date to review: {date}

Please use the query tools to gather data and provide a comprehensive daily review.
"""

WEEKLY_PLANNING_TEMPLATE = """
You are helping the user plan their week. Please:

1. **Review last week**:
   - Summarize financial activity (total income/expense)
   - Count completed vs pending todos
   - Check health tracking consistency

2. **Identify carryover items**:
   - List overdue todos that need attention
   - Note any recurring expenses

3. **Help plan the week ahead**:
   - Ask about priorities for the coming week
   - Suggest todos based on patterns
   - Remind about health tracking goals

Focus area for this week: {focus}

Use the available tools to gather historical data and help create an actionable weekly plan.
"""

FINANCIAL_ANALYSIS_TEMPLATE = """
You are a personal finance assistant. Analyze the user's financial data for the specified period.

Analysis period: {period} (e.g., "last month", "last 3 months", "2024")

Please provide:

1. **Income Analysis**:
   - Total income by source
   - Income trends over time

2. **Expense Analysis**:
   - Total expenses by category
   - Top spending categories
   - Unusual or one-time expenses

3. **Financial Health**:
   - Net savings (income - expenses)
   - Savings rate percentage
   - Month-over-month comparison if applicable

4. **Recommendations**:
   - Areas to reduce spending
   - Budget suggestions by category
   - Savings goals

Use SQL queries on the finance table to gather comprehensive data for this analysis.
"""

HEALTH_CHECKUP_TEMPLATE = """
You are a health tracking assistant. Review the user's health metrics and provide insights.

Metric focus: {metric_type} (or "all" for comprehensive review)
Time period: {days} days

Please analyze:

1. **Data Overview**:
   - Records available for each metric type
   - Tracking consistency (gaps in data)

2. **Trends Analysis**:
   - Changes over time
   - Average values
   - Min/max ranges

3. **Health Insights**:
   - Notable patterns
   - Potential concerns
   - Positive trends

4. **Recommendations**:
   - Metrics that need more consistent tracking
   - Lifestyle suggestions based on data
   - When to consult a healthcare provider

Use the health query tools to gather and analyze the data.
"""

# Prompt metadata for MCP
PROMPTS: dict[str, PromptData] = {
    "daily-review": {
        "name": "daily-review",
        "description": "Review and summarize a day's activities, finances, todos, and health",
        "arguments": [
            {
                "name": "date",
                "description": "Date to review in YYYY-MM-DD format (defaults to today)",
                "required": False,
            }
        ],
        "template": DAILY_REVIEW_TEMPLATE,
    },
    "weekly-planning": {
        "name": "weekly-planning",
        "description": "Plan the upcoming week based on past data and current priorities",
        "arguments": [
            {
                "name": "focus",
                "description": "Main focus area for the week (e.g., 'work', 'health')",
                "required": False,
            }
        ],
        "template": WEEKLY_PLANNING_TEMPLATE,
    },
    "financial-analysis": {
        "name": "financial-analysis",
        "description": "Comprehensive analysis of income and expenses for a specified period",
        "arguments": [
            {
                "name": "period",
                "description": "Analysis period (e.g., 'last month', 'last 3 months')",
                "required": True,
            }
        ],
        "template": FINANCIAL_ANALYSIS_TEMPLATE,
    },
    "health-checkup": {
        "name": "health-checkup",
        "description": "Review health metrics and provide insights and recommendations",
        "arguments": [
            {
                "name": "metric_type",
                "description": "Specific metric to focus on, or 'all' for comprehensive",
                "required": False,
            },
            {
                "name": "days",
                "description": "Number of days to analyze (default: 30)",
                "required": False,
            },
        ],
        "template": HEALTH_CHECKUP_TEMPLATE,
    },
}
