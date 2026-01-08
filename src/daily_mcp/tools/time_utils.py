"""Time utilities for daily-mcp.

Provides current time information to help agents understand
relative time expressions like 'yesterday', 'just now', etc.
"""

from __future__ import annotations

from datetime import datetime


def get_current_time() -> str:
    """Get current time information for agent context.

    Returns comprehensive time info that helps agents convert
    relative time expressions (e.g., 'yesterday 3pm', 'just now')
    to absolute datetime values.

    Returns:
        Formatted string with current datetime info.
    """
    now = datetime.now()

    # Format various representations
    date_str = now.strftime("%Y-%m-%d")
    time_str = now.strftime("%H:%M:%S")
    datetime_str = now.strftime("%Y-%m-%d %H:%M:%S")
    weekday = now.strftime("%A")

    # Calculate useful reference points
    yesterday = now.replace(day=now.day - 1) if now.day > 1 else now
    yesterday_str = yesterday.strftime("%Y-%m-%d")

    return (
        f"Current Time Information:\n"
        f"- Now: {datetime_str}\n"
        f"- Date: {date_str} ({weekday})\n"
        f"- Time: {time_str}\n"
        f"- Yesterday: {yesterday_str}\n"
        f"\n"
        f"Use this to convert relative time expressions:\n"
        f"- 'just now' / '刚刚' → {datetime_str}\n"
        f"- 'yesterday 3pm' / '昨天下午3点' → {yesterday_str} 15:00:00\n"
        f"- 'this morning 9am' / '今天早上9点' → {date_str} 09:00:00"
    )
