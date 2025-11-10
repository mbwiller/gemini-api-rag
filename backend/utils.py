"""
Utility functions for the YouTube Channel RAG tool.

This module provides helper functions for:
- URL validation and parsing
- Text processing and cleaning
- File operations
- Date/time utilities
- String sanitization
"""

import re
import os
import json
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import urlparse, parse_qs
import logging

logger = logging.getLogger(__name__)


# ==================== URL UTILITIES ====================

def validate_youtube_url(url: str) -> bool:
    """
    Validate if the given URL is a valid YouTube channel URL.

    Supported formats:
    - https://youtube.com/@username
    - https://youtube.com/channel/UCxxxxx
    - https://youtube.com/c/channelname
    - https://youtube.com/user/username
    - https://www.youtube.com/... (with www)

    Args:
        url: URL string to validate

    Returns:
        bool: True if valid YouTube channel URL, False otherwise
    """
    if not url or not isinstance(url, str):
        return False

    # YouTube channel URL patterns
    patterns = [
        r'^https?://(www\.)?youtube\.com/@[\w-]+/?$',
        r'^https?://(www\.)?youtube\.com/channel/[\w-]+/?$',
        r'^https?://(www\.)?youtube\.com/c/[\w-]+/?$',
        r'^https?://(www\.)?youtube\.com/user/[\w-]+/?$',
    ]

    return any(re.match(pattern, url.strip()) for pattern in patterns)


def extract_channel_id_from_url(url: str) -> Optional[str]:
    """
    Extract the channel identifier from a YouTube URL.

    Args:
        url: YouTube channel URL

    Returns:
        str: Channel identifier (username, @handle, or channel ID) or None
    """
    if not validate_youtube_url(url):
        return None

    # Remove trailing slash and query parameters
    url = url.split('?')[0].rstrip('/')

    # Extract the identifier based on URL type
    if '/@' in url:
        return url.split('/@')[-1]
    elif '/channel/' in url:
        return url.split('/channel/')[-1]
    elif '/c/' in url:
        return url.split('/c/')[-1]
    elif '/user/' in url:
        return url.split('/user/')[-1]

    return None


def sanitize_channel_name(name: str) -> str:
    """
    Sanitize channel name for use in file paths and store names.

    Args:
        name: Channel name to sanitize

    Returns:
        str: Sanitized name safe for file systems
    """
    # Remove special characters, keep alphanumeric, hyphens, and underscores
    sanitized = re.sub(r'[^\w\s-]', '', name)
    # Replace spaces with underscores
    sanitized = re.sub(r'\s+', '_', sanitized)
    # Remove multiple consecutive underscores
    sanitized = re.sub(r'_+', '_', sanitized)
    # Convert to lowercase and strip
    return sanitized.lower().strip('_')


# ==================== TEXT PROCESSING ====================

def clean_transcript_text(text: str) -> str:
    """
    Clean and normalize transcript text.

    Args:
        text: Raw transcript text

    Returns:
        str: Cleaned text
    """
    if not text:
        return ""

    # Remove multiple spaces
    text = re.sub(r'\s+', ' ', text)
    # Remove multiple newlines (keep at most 2)
    text = re.sub(r'\n{3,}', '\n\n', text)
    # Strip leading/trailing whitespace
    text = text.strip()

    return text


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with suffix.

    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to append if truncated

    Returns:
        str: Truncated text
    """
    if not text or len(text) <= max_length:
        return text

    return text[:max_length - len(suffix)] + suffix


def extract_video_id_from_url(url: str) -> Optional[str]:
    """
    Extract video ID from a YouTube video URL.

    Args:
        url: YouTube video URL

    Returns:
        str: Video ID or None if not found
    """
    if not url:
        return None

    # Pattern for youtube.com/watch?v=VIDEO_ID
    match = re.search(r'[?&]v=([^&]+)', url)
    if match:
        return match.group(1)

    # Pattern for youtu.be/VIDEO_ID
    match = re.search(r'youtu\.be/([^?&]+)', url)
    if match:
        return match.group(1)

    return None


# ==================== FILE OPERATIONS ====================

def ensure_directory_exists(directory: str) -> bool:
    """
    Ensure a directory exists, create if it doesn't.

    Args:
        directory: Path to directory

    Returns:
        bool: True if directory exists or was created
    """
    try:
        os.makedirs(directory, exist_ok=True)
        return True
    except Exception as e:
        logger.error(f"Failed to create directory {directory}: {e}")
        return False


def save_json_file(file_path: str, data: Any) -> bool:
    """
    Save data to a JSON file.

    Args:
        file_path: Path to save file
        data: Data to serialize to JSON

    Returns:
        bool: True if successful
    """
    try:
        # Ensure directory exists
        directory = os.path.dirname(file_path)
        if directory:
            ensure_directory_exists(directory)

        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        logger.error(f"Failed to save JSON file {file_path}: {e}")
        return False


def load_json_file(file_path: str, default: Any = None) -> Any:
    """
    Load data from a JSON file.

    Args:
        file_path: Path to JSON file
        default: Default value if file doesn't exist or is invalid

    Returns:
        Loaded data or default value
    """
    try:
        if not os.path.exists(file_path):
            return default

        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"Failed to load JSON file {file_path}: {e}")
        return default


def create_transcript_file(video_data: Dict[str, Any], output_dir: str) -> Optional[str]:
    """
    Create a transcript file for a video with metadata header.

    Args:
        video_data: Dictionary containing video information
        output_dir: Directory to save the transcript file

    Returns:
        str: Path to created file or None if failed
    """
    try:
        # Ensure output directory exists
        ensure_directory_exists(output_dir)

        # Extract data
        title = video_data.get('title', 'Untitled')
        url = video_data.get('url', '')
        date = video_data.get('date', '')
        transcript = video_data.get('transcript', '')
        video_id = extract_video_id_from_url(url) or 'unknown'

        # Create sanitized filename
        safe_title = sanitize_channel_name(title)[:50]  # Limit length
        filename = f"{safe_title}_{video_id}.txt"
        file_path = os.path.join(output_dir, filename)

        # Create file content with metadata header
        content = f"""Title: {title}
URL: {url}
Date: {date}
Video ID: {video_id}

{'=' * 80}
TRANSCRIPT
{'=' * 80}

{transcript}
"""

        # Write to file
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

        logger.info(f"Created transcript file: {file_path}")
        return file_path

    except Exception as e:
        logger.error(f"Failed to create transcript file for {video_data.get('title')}: {e}")
        return None


# ==================== DATE/TIME UTILITIES ====================

def get_timestamp() -> str:
    """
    Get current timestamp in ISO format.

    Returns:
        str: Current timestamp
    """
    return datetime.now().isoformat()


def format_date(date_str: str, output_format: str = "%Y-%m-%d") -> str:
    """
    Format a date string to a specific format.

    Args:
        date_str: Input date string
        output_format: Desired output format (strftime format)

    Returns:
        str: Formatted date or original string if parsing fails
    """
    try:
        # Try parsing common date formats
        for fmt in ["%Y-%m-%d", "%Y-%m-%dT%H:%M:%S", "%Y/%m/%d", "%d-%m-%Y"]:
            try:
                dt = datetime.strptime(date_str, fmt)
                return dt.strftime(output_format)
            except ValueError:
                continue
        return date_str
    except Exception:
        return date_str


def parse_duration(duration_str: str) -> int:
    """
    Parse duration string (HH:MM:SS or MM:SS) to seconds.

    Args:
        duration_str: Duration string

    Returns:
        int: Duration in seconds, or 0 if parsing fails
    """
    try:
        parts = duration_str.split(':')
        if len(parts) == 3:  # HH:MM:SS
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:  # MM:SS
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return 0
    except Exception:
        return 0


# ==================== VALIDATION UTILITIES ====================

def validate_video_count(count: Any) -> tuple[bool, Optional[str]]:
    """
    Validate video count parameter.

    Args:
        count: Video count to validate

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    try:
        count = int(count)
        if count < 1:
            return False, "Video count must be at least 1"
        if count > 100:
            return False, "Video count cannot exceed 100"
        return True, None
    except (ValueError, TypeError):
        return False, "Video count must be a valid number"


def validate_store_name(store_name: str) -> tuple[bool, Optional[str]]:
    """
    Validate store name format.

    Args:
        store_name: Store name to validate

    Returns:
        tuple: (is_valid: bool, error_message: Optional[str])
    """
    if not store_name or not isinstance(store_name, str):
        return False, "Store name is required"

    if len(store_name) < 3:
        return False, "Store name must be at least 3 characters"

    if len(store_name) > 100:
        return False, "Store name cannot exceed 100 characters"

    # Check for valid characters
    if not re.match(r'^[a-zA-Z0-9_-]+$', store_name):
        return False, "Store name can only contain letters, numbers, hyphens, and underscores"

    return True, None


# ==================== FORMATTING UTILITIES ====================

def format_video_count(count: int) -> str:
    """
    Format video count for display.

    Args:
        count: Number of videos

    Returns:
        str: Formatted string (e.g., "5 videos" or "1 video")
    """
    return f"{count} video{'s' if count != 1 else ''}"


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in human-readable format.

    Args:
        size_bytes: Size in bytes

    Returns:
        str: Formatted size (e.g., "1.5 MB")
    """
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.1f} TB"


def create_store_name(channel_name: str) -> str:
    """
    Create a store name from a channel name.

    Args:
        channel_name: Channel name

    Returns:
        str: Store name with timestamp
    """
    sanitized = sanitize_channel_name(channel_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{sanitized}_{timestamp}"


# ==================== ERROR HANDLING ====================

def create_error_response(message: str, details: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized error response.

    Args:
        message: Error message
        details: Optional detailed error information

    Returns:
        dict: Error response dictionary
    """
    response = {
        'status': 'error',
        'error': message,
        'timestamp': get_timestamp()
    }
    if details:
        response['details'] = details
    return response


def create_success_response(data: Any, message: Optional[str] = None) -> Dict[str, Any]:
    """
    Create a standardized success response.

    Args:
        data: Response data
        message: Optional success message

    Returns:
        dict: Success response dictionary
    """
    response = {
        'status': 'success',
        'data': data,
        'timestamp': get_timestamp()
    }
    if message:
        response['message'] = message
    return response


# ==================== LOGGING UTILITIES ====================

def setup_logging(log_level: str = 'INFO', log_file: Optional[str] = None) -> None:
    """
    Set up logging configuration.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
    """
    level = getattr(logging, log_level.upper(), logging.INFO)

    handlers = [logging.StreamHandler()]
    if log_file:
        handlers.append(logging.FileHandler(log_file))

    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
