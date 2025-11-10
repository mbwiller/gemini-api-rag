# Apify YouTube Scraper Service

Comprehensive Python module for scraping YouTube channels using the Apify platform.

## Features

- **YouTube URL Validation**: Validates channel URLs with detailed error messages
- **Async Execution**: Runs Apify actor asynchronously with status polling
- **Progress Tracking**: Optional callback function for real-time progress updates
- **Comprehensive Error Handling**: Custom exception classes for different error types
- **Sorted Results**: Videos sorted by newest first
- **Plaintext Transcripts**: Extracts and returns plaintext subtitles/transcripts
- **Production-Ready**: Includes logging, type hints, and extensive documentation

## Installation

The required dependencies are already listed in `requirements.txt`:

```bash
pip install -r requirements.txt
```

Required packages:
- `apify-client==1.7.1`
- `python-dotenv==1.0.0`

## Configuration

Set up your Apify API token in the `.env` file:

```bash
APIFY_API_TOKEN=your_apify_api_token_here
```

You can get your Apify API token from: https://console.apify.com/account/integrations

## Usage

### Basic Usage

```python
from backend.apify_service import ApifyYouTubeService

# Initialize the service
service = ApifyYouTubeService()

# Scrape a YouTube channel
videos = service.scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=10
)

# Process results
for video in videos:
    print(f"Title: {video['title']}")
    print(f"URL: {video['url']}")
    print(f"Date: {video['date']}")
    print(f"Transcript: {video['transcript'][:100]}...")
    print()
```

### With Progress Tracking

```python
from backend.apify_service import ApifyYouTubeService

def my_progress_callback(status, elapsed_time, run_info):
    print(f"[{elapsed_time:.1f}s] Current status: {status}")

service = ApifyYouTubeService()

videos = service.scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=10,
    progress_callback=my_progress_callback
)
```

### URL Validation Only

```python
from backend.apify_service import ApifyYouTubeService

service = ApifyYouTubeService()

try:
    service.validate_youtube_url("https://www.youtube.com/@example")
    print("Valid URL!")
except YouTubeURLValidationError as e:
    print(f"Invalid URL: {e}")
```

### Convenience Function

```python
from backend.apify_service import scrape_youtube_channel

# Quick one-liner usage
videos = scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=5
)
```

### Custom Configuration

```python
from backend.apify_service import ApifyYouTubeService

# Custom API token
service = ApifyYouTubeService(api_token="your_custom_token")

# Custom timeout and language
videos = service.scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=10,
    subtitles_language='es',  # Spanish subtitles
    timeout=900  # 15 minutes timeout
)
```

## API Reference

### ApifyYouTubeService Class

#### `__init__(api_token: Optional[str] = None)`

Initialize the service.

**Parameters:**
- `api_token` (str, optional): Apify API token. Defaults to `APIFY_API_TOKEN` environment variable.

**Raises:**
- `ApifyServiceError`: If API token is not provided or found.

#### `scrape_youtube_channel(channel_url, max_videos, ...)`

Main method to scrape a YouTube channel.

**Parameters:**
- `channel_url` (str): YouTube channel URL (required)
- `max_videos` (int): Maximum number of videos to scrape (required)
- `subtitles_language` (str): Language code for subtitles (default: 'en')
- `timeout` (int): Maximum time to wait in seconds (default: 600)
- `progress_callback` (callable, optional): Progress callback function

**Returns:**
- `list[dict]`: List of video dictionaries with the following fields:
  - `title` (str): Video title
  - `url` (str): Video URL
  - `date` (str): Upload date
  - `transcript` (str): Plaintext transcript/subtitles
  - `description` (str): Video description
  - `duration` (str): Video duration
  - `view_count` (int): Number of views
  - `like_count` (int): Number of likes
  - `channel_name` (str): Channel name
  - `channel_url` (str): Channel URL

**Raises:**
- `YouTubeURLValidationError`: If channel URL is invalid
- `ApifyActorError`: If actor execution fails
- `ApifyServiceError`: For other service-related errors

#### `validate_youtube_url(url: str) -> bool`

Validate a YouTube URL.

**Accepted formats:**
- `https://www.youtube.com/@username`
- `https://www.youtube.com/channel/UC...`
- `https://www.youtube.com/c/channelname`
- `https://www.youtube.com/user/username`

**Parameters:**
- `url` (str): URL to validate

**Returns:**
- `bool`: True if valid

**Raises:**
- `YouTubeURLValidationError`: If URL is invalid with detailed error message

#### `test_connection() -> bool`

Test the Apify API connection.

**Returns:**
- `bool`: True if connection is successful, False otherwise

### Exception Classes

#### `ApifyServiceError`

Base exception for all Apify service errors.

#### `YouTubeURLValidationError`

Raised when a YouTube URL is invalid. Inherits from `ApifyServiceError`.

#### `ApifyActorError`

Raised when Apify actor execution fails. Inherits from `ApifyServiceError`.

## Supported YouTube URL Formats

✅ **Valid:**
- `https://www.youtube.com/@username`
- `https://www.youtube.com/channel/UCxxxxxx`
- `https://www.youtube.com/c/channelname`
- `https://www.youtube.com/user/username`
- `https://youtube.com/@example` (without www)

❌ **Invalid:**
- `https://www.youtube.com/watch?v=xxxxx` (individual video)
- `https://www.youtube.com/playlist?list=xxxxx` (playlist)
- `https://google.com/@example` (wrong domain)

## Error Handling

The module provides comprehensive error handling with specific exception types:

```python
from backend.apify_service import (
    ApifyYouTubeService,
    YouTubeURLValidationError,
    ApifyActorError,
    ApifyServiceError
)

service = ApifyYouTubeService()

try:
    videos = service.scrape_youtube_channel(
        channel_url="https://www.youtube.com/@example",
        max_videos=10
    )
except YouTubeURLValidationError as e:
    print(f"Invalid URL: {e}")
except ApifyActorError as e:
    print(f"Actor execution failed: {e}")
except ApifyServiceError as e:
    print(f"Service error: {e}")
```

## Logging

The module uses Python's standard logging module. Configure logging level as needed:

```python
import logging

# Set to DEBUG for detailed logs
logging.basicConfig(level=logging.DEBUG)

# Or set to WARNING to reduce output
logging.basicConfig(level=logging.WARNING)
```

## Progress Callback

The progress callback function receives three parameters:

```python
def my_callback(status: str, elapsed_time: float, run_info: dict):
    """
    Args:
        status: Current actor run status ('RUNNING', 'SUCCEEDED', etc.)
        elapsed_time: Elapsed time in seconds since actor started
        run_info: Complete run information from Apify API
    """
    print(f"Status: {status}, Time: {elapsed_time:.1f}s")
    print(f"Run ID: {run_info.get('id')}")
```

## Configuration Constants

The service includes several configurable constants:

- `ACTOR_ID = "streamers/youtube-scraper"` - Apify actor to use
- `DEFAULT_TIMEOUT = 600` - Default timeout in seconds (10 minutes)
- `POLL_INTERVAL = 5` - Status polling interval in seconds

## Testing

Run the included test suite:

```bash
python3 backend/test_apify_service.py
```

This tests:
- URL validation patterns
- Module structure
- Required methods and classes
- Key features implementation

## Best Practices

1. **Always validate URLs first** before scraping to catch errors early
2. **Use progress callbacks** for long-running scrapes
3. **Handle exceptions properly** to provide good user feedback
4. **Set appropriate timeouts** based on the number of videos
5. **Check for empty transcripts** before processing video data
6. **Use connection test** before starting large scraping jobs

## Troubleshooting

### "Apify API token not found" Error

**Solution:** Set the `APIFY_API_TOKEN` in your `.env` file or pass it to the constructor.

### "Actor run timed out" Error

**Solution:** Increase the timeout parameter or reduce max_videos:

```python
videos = service.scrape_youtube_channel(
    channel_url=url,
    max_videos=5,  # Reduce number
    timeout=900    # Increase timeout to 15 minutes
)
```

### "No transcript found" for some videos

**Solution:** Some videos don't have subtitles. The service will skip these videos automatically and log a warning. Check the logs for details.

### Import errors

**Solution:** Make sure all dependencies are installed:

```bash
pip install -r requirements.txt
```

## Performance Tips

- **Limit max_videos**: Start with small numbers (5-10) for testing
- **Use appropriate timeouts**: ~1 minute per video is a safe estimate
- **Monitor progress**: Use progress callbacks to track long operations
- **Check connection first**: Use `test_connection()` before large jobs

## Example: Complete Workflow

```python
from backend.apify_service import ApifyYouTubeService
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def progress_callback(status, elapsed, run_info):
    print(f"[{elapsed:.1f}s] {status}")

# Initialize service
service = ApifyYouTubeService()

# Test connection
if not service.test_connection():
    print("Failed to connect to Apify API")
    exit(1)

# Validate URL
channel_url = "https://www.youtube.com/@example"
try:
    service.validate_youtube_url(channel_url)
    print(f"✓ URL is valid: {channel_url}")
except Exception as e:
    print(f"✗ Invalid URL: {e}")
    exit(1)

# Scrape channel
try:
    videos = service.scrape_youtube_channel(
        channel_url=channel_url,
        max_videos=10,
        subtitles_language='en',
        progress_callback=progress_callback
    )

    print(f"\nSuccessfully scraped {len(videos)} videos!")

    # Process videos
    for i, video in enumerate(videos, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   Date: {video['date']}")
        print(f"   URL: {video['url']}")
        print(f"   Transcript length: {len(video['transcript'])} chars")

except Exception as e:
    print(f"Error: {e}")
```

## License

Part of the Gemini API RAG project.

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review the Apify actor documentation: https://apify.com/streamers/youtube-scraper
3. Check Apify API docs: https://docs.apify.com/api/client/python
