"""
Utilities Module

Common utility functions used across the application.
"""

import re
from typing import Optional


def validate_email(email: str) -> bool:
    """Validate email format.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email format is valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def sanitize_input(input_str: Optional[str]) -> str:
    """Sanitize and clean input string.
    
    Args:
        input_str (str or None): Input string to sanitize
        
    Returns:
        str: Cleaned string
    """
    if not input_str:
        return ''
    return input_str.strip()


def validate_age(age_str: str) -> Optional[int]:
    """Validate and convert age string to integer.
    
    Args:
        age_str (str): Age as string
        
    Returns:
        int or None: Valid age as integer, None if invalid
    """
    try:
        age = int(age_str)
        if 0 <= age <= 18:
            return age
        return None
    except (ValueError, TypeError):
        return None
