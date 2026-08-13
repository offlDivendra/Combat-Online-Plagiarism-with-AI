"""
Helper Utility Functions
Common utility functions used across the application.
"""

import os
import uuid
from datetime import datetime
from typing import Optional, Any
import json


def generate_unique_id() -> str:
    """
    Generate a unique identifier.
    
    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.
    
    Returns:
        ISO formatted timestamp string
    """
    return datetime.now().isoformat()


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.
    
    Args:
        size_bytes: File size in bytes
        
    Returns:
        Formatted string (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length.
    
    Args:
        text: Text to truncate
        max_length: Maximum length
        suffix: Suffix to add when truncated
        
    Returns:
        Truncated text
    """
    if not text or len(text) <= max_length:
        return text
    
    return text[:max_length - len(suffix)] + suffix


def sanitize_filename(filename: str) -> str:
    """
    Sanitize a filename by removing unsafe characters.
    
    Args:
        filename: Original filename
        
    Returns:
        Sanitized filename
    """
    # Remove or replace unsafe characters
    unsafe_chars = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
    sanitized = filename
    
    for char in unsafe_chars:
        sanitized = sanitized.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    sanitized = sanitized.strip('. ')
    
    # Ensure filename is not empty
    if not sanitized:
        sanitized = "unnamed_file"
    
    return sanitized


def ensure_directory_exists(directory: str) -> None:
    """
    Ensure a directory exists, create if it doesn't.
    
    Args:
        directory: Directory path
    """
    os.makedirs(directory, exist_ok=True)


def save_uploaded_file(file_content: bytes, filename: str, upload_dir: str) -> str:
    """
    Save uploaded file content to disk.
    
    Args:
        file_content: File content as bytes
        filename: Original filename
        upload_dir: Directory to save the file
        
    Returns:
        Path to saved file
    """
    # Ensure upload directory exists
    ensure_directory_exists(upload_dir)
    
    # Sanitize filename
    safe_filename = sanitize_filename(filename)
    
    # Generate unique filename to avoid conflicts
    unique_filename = f"{generate_unique_id()}_{safe_filename}"
    file_path = os.path.join(upload_dir, unique_filename)
    
    # Save file
    with open(file_path, 'wb') as f:
        f.write(file_content)
    
    return file_path


def delete_file_safe(file_path: str) -> bool:
    """
    Safely delete a file without raising exceptions.
    
    Args:
        file_path: Path to file
        
    Returns:
        True if deleted successfully, False otherwise
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception:
        return False


def calculate_percentage(part: float, whole: float) -> float:
    """
    Calculate percentage with division by zero protection.
    
    Args:
        part: Part value
        whole: Whole value
        
    Returns:
        Percentage (0-100)
    """
    if whole == 0:
        return 0.0
    return round((part / whole) * 100, 2)


def validate_text_length(text: str, min_length: int = 10, max_length: int = 1000000) -> tuple:
    """
    Validate text length is within acceptable bounds.
    
    Args:
        text: Text to validate
        min_length: Minimum acceptable length
        max_length: Maximum acceptable length
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not text or not text.strip():
        return False, "Text cannot be empty"
    
    text_length = len(text.strip())
    
    if text_length < min_length:
        return False, f"Text too short. Minimum {min_length} characters required."
    
    if text_length > max_length:
        return False, f"Text too long. Maximum {max_length} characters allowed."
    
    return True, None


def format_datetime(dt: datetime, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format datetime object to string.
    
    Args:
        dt: Datetime object
        format_str: Format string
        
    Returns:
        Formatted datetime string
    """
    return dt.strftime(format_str)


def parse_json_safe(json_str: str, default: Any = None) -> Any:
    """
    Parse JSON string safely without raising exceptions.
    
    Args:
        json_str: JSON string
        default: Default value to return on error
        
    Returns:
        Parsed JSON or default value
    """
    try:
        return json.loads(json_str)
    except Exception:
        return default


def to_json_safe(obj: Any, default: Any = None) -> Optional[str]:
    """
    Convert object to JSON string safely.
    
    Args:
        obj: Object to convert
        default: Default value to return on error
        
    Returns:
        JSON string or default value
    """
    try:
        return json.dumps(obj, indent=2, default=str)
    except Exception:
        return default


def get_similarity_color(similarity: float) -> str:
    """
    Get color code based on similarity percentage for UI display.
    
    Args:
        similarity: Similarity percentage (0-100)
        
    Returns:
        Color name or hex code
    """
    if similarity >= 80:
        return "#dc2626"  # Red - High similarity
    elif similarity >= 60:
        return "#ea580c"  # Orange - Moderate-high
    elif similarity >= 40:
        return "#f59e0b"  # Amber - Moderate
    elif similarity >= 20:
        return "#84cc16"  # Lime - Low
    else:
        return "#22c55e"  # Green - Original


def get_similarity_badge(similarity: float) -> str:
    """
    Get badge text based on similarity percentage.
    
    Args:
        similarity: Similarity percentage (0-100)
        
    Returns:
        Badge text
    """
    if similarity >= 80:
        return "POTENTIAL PLAGIARISM"
    elif similarity >= 60:
        return "HIGH SIMILARITY"
    elif similarity >= 40:
        return "MODERATE SIMILARITY"
    elif similarity >= 20:
        return "LOW SIMILARITY"
    else:
        return "MOSTLY ORIGINAL"


def extract_filename_without_extension(filepath: str) -> str:
    """
    Extract filename without extension from a file path.
    
    Args:
        filepath: Full file path
        
    Returns:
        Filename without extension
    """
    filename = os.path.basename(filepath)
    return os.path.splitext(filename)[0]


def create_summary_stats(data: list, key: str) -> dict:
    """
    Create summary statistics from a list of dictionaries.
    
    Args:
        data: List of dictionaries
        key: Key to extract values from
        
    Returns:
        Dictionary with min, max, avg, median
    """
    if not data:
        return {
            "min": 0,
            "max": 0,
            "avg": 0,
            "median": 0,
            "count": 0
        }
    
    values = [item[key] for item in data if key in item]
    
    if not values:
        return {
            "min": 0,
            "max": 0,
            "avg": 0,
            "median": 0,
            "count": 0
        }
    
    values.sort()
    n = len(values)
    median = values[n // 2] if n % 2 == 1 else (values[n // 2 - 1] + values[n // 2]) / 2
    
    return {
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "avg": round(sum(values) / len(values), 2),
        "median": round(median, 2),
        "count": len(values)
    }
