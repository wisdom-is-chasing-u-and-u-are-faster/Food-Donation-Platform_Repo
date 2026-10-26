"""
HACCP Thermal Logging & Biological Safety Window Service
Compliant with Good Samaritan Food Act and FDA Food Safety Modernization Act (FSMA).
Requirements: Cold food < 41°F, Hot food > 135°F, Biological window <= 2 hours.
"""
from typing import Dict, Any, Tuple
from datetime import datetime


def evaluate_haccp_temperature(
        temp_f: float, is_perishable: bool = True) -> Tuple[bool, str, str]:
    """
    Evaluates food temperature against HACCP critical control points.
    Returns: (is_compliant, haccp_status, message)
    """
    if not is_perishable:
        return True, "COMPLIANT", "Ambient shelf-stable item."

    if temp_f <= 41.0:
        return True, "COMPLIANT", f"Cold holding compliant: {temp_f:.1f}°F <= 41.0°F"
    elif temp_f >= 135.0:
        return True, "COMPLIANT", f"Hot holding compliant: {temp_f:.1f}°F >= 135.0°F"
    elif 41.0 < temp_f <= 45.0:
        return False, "WARNING", f"Danger zone warning: {temp_f:.1f}°F slightly elevated above 41°F"
    elif 130.0 <= temp_f < 135.0:
        return False, "WARNING", f"Danger zone warning: {temp_f:.1f}°F slightly below hot holding threshold 135°F"
    else:
        return False, "VIOLATION", f"CRITICAL HACCP VIOLATION: {temp_f:.1f}°F is inside the microbial danger zone (41°F - 135°F)"


def calculate_safe_transit_window(
        created_at_str: str, max_window_minutes: float = 120.0) -> float:
    """
    Calculates remaining biological safe transit window in minutes (120 min max).
    """
    try:
        # Handle ISO format and SQLite datetime strings
        created_time = datetime.fromisoformat(
            created_at_str.replace(
                "Z", "+00:00").split("+")[0])
    except Exception:
        created_time = datetime.now()

    elapsed_minutes = (datetime.now() - created_time).total_seconds() / 60.0
    remaining = max(0.0, max_window_minutes - elapsed_minutes)
    return round(remaining, 1)
