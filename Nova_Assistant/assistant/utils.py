# utils.py — Helper utility functions for Nova Assistant
# These functions provide time, date, greeting, timezone, countdown, and formatting support.

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError


# ──────────────────────────────────────────────
# Core time / date helpers
# ──────────────────────────────────────────────

def get_current_time(timezone: str = None) -> str:
    """Return current time formatted as 12-hour clock, e.g. '03:45 PM'.

    Args:
        timezone: Optional IANA timezone string, e.g. 'Asia/Kolkata'.
                  Defaults to local system time when None.
    """
    now = _get_now(timezone)
    return now.strftime("%I:%M %p")


def get_current_date(timezone: str = None) -> str:
    """Return current date formatted nicely, e.g. '18 April 2026'.

    Args:
        timezone: Optional IANA timezone string.
    """
    now = _get_now(timezone)
    return now.strftime("%d %B %Y")


def get_day_name(timezone: str = None) -> str:
    """Return current day name, e.g. 'Saturday'.

    Args:
        timezone: Optional IANA timezone string.
    """
    now = _get_now(timezone)
    return now.strftime("%A")


def get_time_based_greeting(timezone: str = None) -> str:
    """Return a greeting based on the time of day.

    Args:
        timezone: Optional IANA timezone string.
    """
    hour = _get_now(timezone).hour

    if hour < 12:
        return "Good morning"
    elif hour < 17:
        return "Good afternoon"
    else:
        return "Good evening"


# ──────────────────────────────────────────────
# Extended date / time info
# ──────────────────────────────────────────────

def get_datetime_info(timezone: str = None) -> dict:
    """Return a dictionary with comprehensive date and time details.

    Returns keys: date, time, day, week_number, day_of_year,
                  is_weekend, month, year, timezone.
    """
    now = _get_now(timezone)
    return {
        "date": now.strftime("%d %B %Y"),
        "time": now.strftime("%I:%M %p"),
        "day": now.strftime("%A"),
        "week_number": now.isocalendar().week,
        "day_of_year": now.timetuple().tm_yday,
        "is_weekend": now.weekday() >= 5,
        "month": now.strftime("%B"),
        "year": now.year,
        "timezone": str(now.tzinfo) if now.tzinfo else "local",
    }


def get_week_number(timezone: str = None) -> int:
    """Return the ISO week number of the current date (1–53)."""
    return _get_now(timezone).isocalendar().week


def is_weekend(timezone: str = None) -> bool:
    """Return True if today is Saturday or Sunday."""
    return _get_now(timezone).weekday() >= 5


def get_days_until(target_date: datetime) -> int:
    """Return the number of days from today until *target_date*.

    Returns a negative number if *target_date* is in the past.

    Args:
        target_date: A datetime object representing the target date.
    """
    delta = target_date.date() - datetime.now().date()
    return delta.days


def get_unix_timestamp(timezone: str = None) -> int:
    """Return the current UTC Unix timestamp as an integer."""
    return int(_get_now(timezone).timestamp())


# ──────────────────────────────────────────────
# Formatting helpers
# ──────────────────────────────────────────────

def format_duration(seconds: int) -> str:
    """Convert a duration in seconds to a human-readable string.

    Examples:
        format_duration(3661)  →  '1h 1m 1s'
        format_duration(45)    →  '45s'
        format_duration(3600)  →  '1h 0m 0s'
    """
    if not isinstance(seconds, (int, float)) or seconds < 0:
        raise ValueError("seconds must be a non-negative number.")

    seconds = int(seconds)
    hours, remainder = divmod(seconds, 3600)
    minutes, secs = divmod(remainder, 60)

    if hours:
        return f"{hours}h {minutes}m {secs}s"
    if minutes:
        return f"{minutes}m {secs}s"
    return f"{secs}s"


def format_date(dt: datetime, fmt: str = "%d %B %Y") -> str:
    """Format any datetime object into a readable string.

    Args:
        dt:  The datetime to format.
        fmt: strftime format string. Defaults to '18 April 2026' style.
    """
    if not isinstance(dt, datetime):
        raise TypeError("dt must be a datetime object.")
    return dt.strftime(fmt)


# ──────────────────────────────────────────────
# Timezone utilities
# ──────────────────────────────────────────────

def convert_timezone(dt: datetime, target_tz: str) -> datetime:
    """Convert a datetime object to a different timezone.

    Args:
        dt:        A timezone-aware or naive (assumed local) datetime.
        target_tz: IANA timezone string, e.g. 'America/New_York'.

    Returns:
        A new timezone-aware datetime in *target_tz*.
    """
    tz = _resolve_tz(target_tz)
    if dt.tzinfo is None:
        dt = dt.astimezone()          # attach local tz
    return dt.astimezone(tz)


def get_time_in_timezone(timezone: str) -> str:
    """Return the current time in the given IANA timezone as a formatted string.

    Args:
        timezone: IANA timezone string, e.g. 'Europe/London'.
    """
    return _get_now(timezone).strftime("%I:%M %p (%Z)")


# ──────────────────────────────────────────────
# Calendar helpers
# ──────────────────────────────────────────────

def get_month_progress(timezone: str = None) -> float:
    """Return how far through the current month we are as a percentage (0–100)."""
    now = _get_now(timezone)
    # Last day of the current month
    if now.month == 12:
        last_day = 31
    else:
        last_day = (now.replace(month=now.month + 1, day=1) - timedelta(days=1)).day
    return round((now.day / last_day) * 100, 1)


def get_year_progress(timezone: str = None) -> float:
    """Return how far through the current year we are as a percentage (0–100)."""
    now = _get_now(timezone)
    start_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    start_of_next_year = start_of_year.replace(year=now.year + 1)
    elapsed = (now - start_of_year).total_seconds()
    total = (start_of_next_year - start_of_year).total_seconds()
    return round((elapsed / total) * 100, 2)


def get_season(timezone: str = None) -> str:
    """Return the current meteorological season in the Northern Hemisphere.

    Returns one of: 'Spring', 'Summer', 'Autumn', 'Winter'.
    """
    month = _get_now(timezone).month
    if month in (3, 4, 5):
        return "Spring"
    elif month in (6, 7, 8):
        return "Summer"
    elif month in (9, 10, 11):
        return "Autumn"
    else:
        return "Winter"


# ──────────────────────────────────────────────
# Internal helpers (not part of the public API)
# ──────────────────────────────────────────────

def _get_now(timezone: str = None) -> datetime:
    """Return the current datetime, optionally in a given IANA timezone."""
    if timezone is None:
        return datetime.now()
    return datetime.now(_resolve_tz(timezone))


def _resolve_tz(timezone: str) -> ZoneInfo:
    """Parse and return a ZoneInfo object; raise ValueError for unknown zones."""
    try:
        return ZoneInfo(timezone)
    except (ZoneInfoNotFoundError, KeyError):
        raise ValueError(
            f"Unknown timezone: '{timezone}'. "
            "Use an IANA name like 'Asia/Kolkata' or 'America/New_York'."
        )