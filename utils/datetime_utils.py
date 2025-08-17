"""
UTC datetime utilities for consistent date/time handling across Python components
"""
import datetime as dt
from typing import Union


def utc_timestamp() -> str:
    """Get current UTC timestamp in YYYY-MM-DD HH:MM:SS format"""
    return dt.datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")


def utc_date() -> str:
    """Get current UTC date in YYYY-MM-DD format"""
    return dt.datetime.utcnow().strftime("%Y-%m-%d")


def utc_iso_timestamp() -> str:
    """Get current UTC timestamp in ISO format"""
    return dt.datetime.utcnow().isoformat() + "Z"


def format_utc_timestamp(date_obj: dt.datetime) -> str:
    """Format a datetime object to UTC timestamp string (YYYY-MM-DD HH:MM:SS)"""
    return date_obj.strftime("%Y-%m-%d %H:%M:%S")


def validate_datetime_input(datetime_str: str) -> dict:
    """
    Validate if a date string is in proper format and represents a valid date
    Returns: {"valid": bool, "error": str or None}
    """
    if not datetime_str or not isinstance(datetime_str, str):
        return {"valid": False, "error": "Date/time string is required"}
    
    # Try different formats
    formats = [
        "%Y-%m-%d %H:%M:%S",  # YYYY-MM-DD HH:MM:SS
        "%Y-%m-%d",           # YYYY-MM-DD
        "%Y-%m-%dT%H:%M:%S",  # ISO without Z
        "%Y-%m-%dT%H:%M:%SZ", # ISO with Z
    ]
    
    for fmt in formats:
        try:
            dt.datetime.strptime(datetime_str, fmt)
            return {"valid": True}
        except ValueError:
            continue
    
    return {
        "valid": False, 
        "error": "Invalid format. Expected YYYY-MM-DD HH:MM:SS, YYYY-MM-DD, or ISO format"
    }