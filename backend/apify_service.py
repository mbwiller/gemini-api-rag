"""
Apify YouTube Channel Scraper Service

This module provides functionality to scrape YouTube channels using the Apify platform.
It uses the 'streamers/youtube-scraper' actor to extract video titles, URLs, dates,
and plaintext subtitles/transcripts.

Features:
    - YouTube URL validation
    - Async actor execution with status polling
    - Comprehensive error handling
    - Progress tracking capabilities
    - Structured data output sorted by newest first

Author: Gemini API RAG System
"""

import os
import re
import time
import logging
from typing import List, Dict, Optional, Any
from datetime import datetime
from urllib.parse import urlparse, parse_qs

from apify_client import ApifyClient
from apify_client.clients.resource_clients.actor import ActorClient
from dotenv import load_dotenv


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ApifyServiceError(Exception):
    """Base exception for Apify service errors."""
    pass


class YouTubeURLValidationError(ApifyServiceError):
    """Exception raised for invalid YouTube URLs."""
    pass


class ApifyActorError(ApifyServiceError):
    """Exception raised for Apify actor execution errors."""
    pass


class ApifyYouTubeService:
    """
    Service class for scraping YouTube channels using Apify.

    This class provides methods to interact with the Apify YouTube scraper actor,
    validate URLs, and process the scraped data into a structured format.

    Attributes:
        client (ApifyClient): The Apify API client instance
        actor_id (str): The ID of the YouTube scraper actor
    """

    # Apify YouTube scraper actor ID
    ACTOR_ID = "streamers/youtube-scraper"

    # Default timeout for actor run (in seconds)
    DEFAULT_TIMEOUT = 600

    # Polling interval for checking actor status (in seconds)
    POLL_INTERVAL = 5

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize the Apify YouTube service.

        Args:
            api_token (str, optional): Apify API token. If not provided,
                                      it will be loaded from APIFY_API_TOKEN env variable.

        Raises:
            ApifyServiceError: If API token is not provided or found in environment
        """
        self.api_token = api_token or os.getenv('APIFY_API_TOKEN')

        if not self.api_token:
            raise ApifyServiceError(
                "Apify API token not found. Please set APIFY_API_TOKEN environment variable "
                "or pass it to the constructor."
            )

        # Initialize Apify client
        self.client = ApifyClient(self.api_token)
        logger.info("Apify client initialized successfully")

    @staticmethod
    def validate_youtube_url(url: str) -> bool:
        """
        Validate if the provided URL is a valid YouTube channel or user URL.

        Accepts formats like:
            - https://www.youtube.com/@username
            - https://www.youtube.com/channel/UC...
            - https://www.youtube.com/c/channelname
            - https://www.youtube.com/user/username
            - https://youtube.com/@username

        Args:
            url (str): The YouTube URL to validate

        Returns:
            bool: True if valid YouTube channel/user URL, False otherwise

        Raises:
            YouTubeURLValidationError: If the URL is invalid with detailed error message
        """
        if not url or not isinstance(url, str):
            raise YouTubeURLValidationError("URL must be a non-empty string")

        # Parse the URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            raise YouTubeURLValidationError(f"Invalid URL format: {str(e)}")

        # Check if it's a YouTube domain
        valid_domains = ['youtube.com', 'www.youtube.com', 'm.youtube.com']
        if parsed.netloc not in valid_domains:
            raise YouTubeURLValidationError(
                f"Not a YouTube URL. Expected domain: youtube.com, got: {parsed.netloc}"
            )

        # Check if it's a channel, user, or handle URL
        path = parsed.path.lower()
        valid_patterns = [
            r'^/@[\w-]+',           # @username
            r'^/channel/[\w-]+',    # /channel/UC...
            r'^/c/[\w-]+',          # /c/channelname
            r'^/user/[\w-]+',       # /user/username
        ]

        is_valid = any(re.match(pattern, path) for pattern in valid_patterns)

        if not is_valid:
            raise YouTubeURLValidationError(
                f"Invalid YouTube channel URL format. Path must be one of: "
                f"/@username, /channel/ID, /c/name, or /user/name. Got: {path}"
            )

        logger.info(f"YouTube URL validated successfully: {url}")
        return True

    def _prepare_actor_input(
        self,
        channel_url: str,
        max_videos: int,
        subtitles_language: str = 'en'
    ) -> Dict[str, Any]:
        """
        Prepare the input configuration for the Apify YouTube scraper actor.

        Args:
            channel_url (str): YouTube channel URL to scrape
            max_videos (int): Maximum number of videos to scrape
            subtitles_language (str): Language code for subtitles (default: 'en')

        Returns:
            dict: Actor input configuration
        """
        actor_input = {
            "startUrls": [{"url": channel_url}],
            "maxResults": max_videos,
            "downloadSubtitles": True,
            "subtitlesLanguage": subtitles_language,
            "sortBy": "newest",  # Sort by newest first
            "searchType": "video",
            "includeTranscript": True,
            "subtitlesFormat": "text",
            "proxyConfiguration": {"useApifyProxy": True},
        }

        logger.debug(f"Prepared actor input: {actor_input}")
        return actor_input

    def _wait_for_actor_completion(
        self,
        run_id: str,
        timeout: int = DEFAULT_TIMEOUT,
        progress_callback: Optional[callable] = None
    ) -> Dict[str, Any]:
        """
        Wait for the actor run to complete and return the result.

        Args:
            run_id (str): The actor run ID
            timeout (int): Maximum time to wait in seconds
            progress_callback (callable, optional): Callback function for progress updates

        Returns:
            dict: Actor run information including status and dataset ID

        Raises:
            ApifyActorError: If actor run fails or times out
        """
        start_time = time.time()

        while True:
            # Check timeout
            elapsed = time.time() - start_time
            if elapsed > timeout:
                raise ApifyActorError(
                    f"Actor run timed out after {timeout} seconds. Run ID: {run_id}"
                )

            # Get run status
            try:
                run_info = self.client.run(run_id).get()
            except Exception as e:
                raise ApifyActorError(f"Failed to get run status: {str(e)}")

            status = run_info.get('status')
            logger.info(f"Actor run status: {status} (elapsed: {elapsed:.1f}s)")

            # Call progress callback if provided
            if progress_callback:
                try:
                    progress_callback(status, elapsed, run_info)
                except Exception as e:
                    logger.warning(f"Progress callback error: {str(e)}")

            # Check if completed
            if status == 'SUCCEEDED':
                logger.info(f"Actor run completed successfully. Run ID: {run_id}")
                return run_info

            elif status in ['FAILED', 'ABORTED', 'TIMED-OUT']:
                error_message = run_info.get('statusMessage', 'Unknown error')
                raise ApifyActorError(
                    f"Actor run {status.lower()}: {error_message}. Run ID: {run_id}"
                )

            # Wait before polling again
            time.sleep(self.POLL_INTERVAL)

    def _process_actor_results(
        self,
        dataset_id: str,
        max_videos: int
    ) -> List[Dict[str, Any]]:
        """
        Process and extract data from the actor's dataset.

        Args:
            dataset_id (str): The dataset ID containing actor results
            max_videos (int): Maximum number of videos to return

        Returns:
            list: List of dictionaries containing video data

        Raises:
            ApifyActorError: If dataset retrieval or processing fails
        """
        try:
            # Get dataset items
            dataset_client = self.client.dataset(dataset_id)
            items = list(dataset_client.iterate_items())

            logger.info(f"Retrieved {len(items)} items from dataset")

        except Exception as e:
            raise ApifyActorError(f"Failed to retrieve dataset items: {str(e)}")

        # Process items
        processed_videos = []

        for item in items:
            try:
                # Extract video data
                video_data = self._extract_video_data(item)

                if video_data:
                    processed_videos.append(video_data)

                # Stop if we've reached max_videos
                if len(processed_videos) >= max_videos:
                    break

            except Exception as e:
                logger.warning(f"Failed to process item: {str(e)}")
                continue

        # Sort by date (newest first)
        processed_videos.sort(
            key=lambda x: x.get('date', ''),
            reverse=True
        )

        logger.info(f"Processed {len(processed_videos)} videos successfully")
        return processed_videos[:max_videos]

    def _extract_video_data(self, item: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Extract relevant video data from a dataset item.

        Args:
            item (dict): Raw item from the dataset

        Returns:
            dict: Processed video data with title, url, date, and transcript
                 Returns None if essential fields are missing
        """
        # Extract essential fields
        title = item.get('title')
        url = item.get('url') or item.get('videoUrl')

        # Skip if essential fields are missing
        if not title or not url:
            logger.warning("Skipping item with missing title or URL")
            return None

        # Extract upload date
        upload_date = item.get('uploadDate') or item.get('date') or item.get('publishedAt')
        if upload_date:
            # Convert to ISO format if needed
            try:
                # Handle various date formats
                if isinstance(upload_date, str):
                    # Try to parse and standardize the date
                    date_str = upload_date
                else:
                    date_str = str(upload_date)
            except Exception as e:
                logger.warning(f"Failed to process date: {str(e)}")
                date_str = upload_date
        else:
            date_str = ''

        # Extract transcript/subtitles
        transcript = self._extract_transcript(item)

        # Build structured video data
        video_data = {
            'title': title,
            'url': url,
            'date': date_str,
            'transcript': transcript,
            'description': item.get('description', ''),
            'duration': item.get('duration', ''),
            'view_count': item.get('viewCount', 0),
            'like_count': item.get('likeCount', 0),
            'channel_name': item.get('channelName', ''),
            'channel_url': item.get('channelUrl', ''),
        }

        return video_data

    def _extract_transcript(self, item: Dict[str, Any]) -> str:
        """
        Extract plaintext transcript from various possible fields in the item.

        Args:
            item (dict): Raw item from the dataset

        Returns:
            str: Plaintext transcript, or empty string if not available
        """
        # Try different possible fields for transcripts
        transcript_fields = [
            'subtitles',
            'transcript',
            'captions',
            'subtitlesText',
            'transcriptText'
        ]

        for field in transcript_fields:
            transcript_data = item.get(field)

            if not transcript_data:
                continue

            # If it's already a string, return it
            if isinstance(transcript_data, str):
                return transcript_data.strip()

            # If it's a list of subtitle objects, extract text
            if isinstance(transcript_data, list):
                try:
                    # Extract text from subtitle entries
                    texts = []
                    for entry in transcript_data:
                        if isinstance(entry, dict):
                            text = entry.get('text') or entry.get('content')
                            if text:
                                texts.append(text)
                        elif isinstance(entry, str):
                            texts.append(entry)

                    if texts:
                        return ' '.join(texts).strip()
                except Exception as e:
                    logger.warning(f"Failed to extract transcript from list: {str(e)}")

            # If it's a dict, try to extract text
            if isinstance(transcript_data, dict):
                text = transcript_data.get('text') or transcript_data.get('content')
                if text:
                    return text.strip()

        logger.debug("No transcript found in item")
        return ''

    def scrape_youtube_channel(
        self,
        channel_url: str,
        max_videos: int,
        subtitles_language: str = 'en',
        timeout: int = DEFAULT_TIMEOUT,
        progress_callback: Optional[callable] = None
    ) -> List[Dict[str, Any]]:
        """
        Scrape a YouTube channel and extract video data with transcripts.

        This is the main public method for scraping YouTube channels. It validates
        the URL, runs the Apify actor, waits for completion, and returns structured
        video data sorted by newest first.

        Args:
            channel_url (str): YouTube channel URL to scrape
            max_videos (int): Maximum number of videos to scrape (newest first)
            subtitles_language (str): Language code for subtitles (default: 'en')
            timeout (int): Maximum time to wait for actor completion in seconds
            progress_callback (callable, optional): Callback function called with
                                                   (status, elapsed_time, run_info)

        Returns:
            list: List of dictionaries, each containing:
                - title (str): Video title
                - url (str): Video URL
                - date (str): Upload date
                - transcript (str): Plaintext transcript/subtitles
                - description (str): Video description
                - duration (str): Video duration
                - view_count (int): Number of views
                - like_count (int): Number of likes
                - channel_name (str): Channel name
                - channel_url (str): Channel URL

        Raises:
            YouTubeURLValidationError: If the channel URL is invalid
            ApifyActorError: If actor execution fails
            ApifyServiceError: For other service-related errors

        Example:
            >>> service = ApifyYouTubeService()
            >>> videos = service.scrape_youtube_channel(
            ...     channel_url="https://www.youtube.com/@example",
            ...     max_videos=10
            ... )
            >>> print(f"Scraped {len(videos)} videos")
            >>> print(f"First video: {videos[0]['title']}")
        """
        # Validate inputs
        if max_videos <= 0:
            raise ApifyServiceError("max_videos must be greater than 0")

        # Validate YouTube URL
        self.validate_youtube_url(channel_url)

        logger.info(
            f"Starting YouTube channel scrape: {channel_url} "
            f"(max_videos: {max_videos}, language: {subtitles_language})"
        )

        # Prepare actor input
        actor_input = self._prepare_actor_input(
            channel_url=channel_url,
            max_videos=max_videos,
            subtitles_language=subtitles_language
        )

        # Run the actor
        try:
            logger.info(f"Starting Apify actor: {self.ACTOR_ID}")
            run = self.client.actor(self.ACTOR_ID).call(run_input=actor_input)
            run_id = run.get('id')

            logger.info(f"Actor started successfully. Run ID: {run_id}")

        except Exception as e:
            raise ApifyActorError(f"Failed to start actor: {str(e)}")

        # Wait for completion
        try:
            run_info = self._wait_for_actor_completion(
                run_id=run_id,
                timeout=timeout,
                progress_callback=progress_callback
            )
        except ApifyActorError:
            raise
        except Exception as e:
            raise ApifyActorError(f"Error while waiting for actor completion: {str(e)}")

        # Get dataset ID
        dataset_id = run_info.get('defaultDatasetId')
        if not dataset_id:
            raise ApifyActorError("No dataset ID found in actor run results")

        # Process and return results
        try:
            videos = self._process_actor_results(
                dataset_id=dataset_id,
                max_videos=max_videos
            )

            logger.info(
                f"Successfully scraped {len(videos)} videos from {channel_url}"
            )

            return videos

        except ApifyActorError:
            raise
        except Exception as e:
            raise ApifyActorError(f"Failed to process actor results: {str(e)}")

    def test_connection(self) -> bool:
        """
        Test the Apify API connection.

        Returns:
            bool: True if connection is successful, False otherwise
        """
        try:
            # Try to get user information as a connection test
            user = self.client.user().get()
            logger.info(f"Apify connection successful. User: {user.get('username', 'unknown')}")
            return True
        except Exception as e:
            logger.error(f"Apify connection test failed: {str(e)}")
            return False


# Backward compatibility - alias for the old class name
ApifyService = ApifyYouTubeService


# Example progress callback function
def example_progress_callback(status: str, elapsed_time: float, run_info: Dict[str, Any]) -> None:
    """
    Example progress callback function.

    Args:
        status (str): Current actor run status
        elapsed_time (float): Elapsed time in seconds
        run_info (dict): Complete run information from Apify
    """
    print(f"[{elapsed_time:.1f}s] Status: {status}")


# Convenience function for quick usage
def scrape_youtube_channel(
    channel_url: str,
    max_videos: int,
    api_token: Optional[str] = None,
    progress_callback: Optional[callable] = None
) -> List[Dict[str, Any]]:
    """
    Convenience function to scrape a YouTube channel.

    Args:
        channel_url (str): YouTube channel URL
        max_videos (int): Maximum number of videos to scrape
        api_token (str, optional): Apify API token
        progress_callback (callable, optional): Progress callback function

    Returns:
        list: List of video data dictionaries

    Example:
        >>> from apify_service import scrape_youtube_channel
        >>> videos = scrape_youtube_channel(
        ...     "https://www.youtube.com/@example",
        ...     max_videos=5
        ... )
    """
    service = ApifyYouTubeService(api_token=api_token)
    return service.scrape_youtube_channel(
        channel_url=channel_url,
        max_videos=max_videos,
        progress_callback=progress_callback
    )


if __name__ == "__main__":
    # Example usage
    import sys

    # Set up logging for demo
    logging.basicConfig(level=logging.INFO)

    # Example channel URL
    test_url = "https://www.youtube.com/@example"

    try:
        # Create service instance
        service = ApifyYouTubeService()

        # Validate URL
        print(f"Validating URL: {test_url}")
        service.validate_youtube_url(test_url)
        print("✓ URL is valid")

        # Note: Uncomment below to actually scrape (requires valid API token and channel)
        # videos = service.scrape_youtube_channel(
        #     channel_url=test_url,
        #     max_videos=3,
        #     progress_callback=example_progress_callback
        # )
        #
        # print(f"\nScraped {len(videos)} videos:")
        # for i, video in enumerate(videos, 1):
        #     print(f"\n{i}. {video['title']}")
        #     print(f"   URL: {video['url']}")
        #     print(f"   Date: {video['date']}")
        #     print(f"   Transcript length: {len(video['transcript'])} characters")

    except ApifyServiceError as e:
        print(f"Error: {e}")
        sys.exit(1)
