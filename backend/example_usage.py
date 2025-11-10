"""
Example usage script for Apify YouTube Scraper Service

This script demonstrates how to use the ApifyYouTubeService to scrape
YouTube channels for AI development content.

Usage:
    python backend/example_usage.py
"""

import os
import sys
import logging
from typing import List, Dict, Any

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.apify_service import (
    ApifyYouTubeService,
    YouTubeURLValidationError,
    ApifyActorError,
    ApifyServiceError
)


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def progress_callback(status: str, elapsed_time: float, run_info: Dict[str, Any]) -> None:
    """
    Custom progress callback to display scraping progress.

    Args:
        status: Current actor run status
        elapsed_time: Time elapsed in seconds
        run_info: Complete run information from Apify
    """
    progress_symbols = {
        'READY': '⏳',
        'RUNNING': '🔄',
        'SUCCEEDED': '✅',
        'FAILED': '❌',
        'ABORTED': '🛑',
        'TIMED-OUT': '⏱️'
    }

    symbol = progress_symbols.get(status, '⚡')
    print(f"{symbol} [{elapsed_time:.1f}s] Status: {status}")


def validate_channel_url(service: ApifyYouTubeService, url: str) -> bool:
    """
    Validate a YouTube channel URL.

    Args:
        service: ApifyYouTubeService instance
        url: YouTube URL to validate

    Returns:
        bool: True if valid, False otherwise
    """
    try:
        service.validate_youtube_url(url)
        print(f"✓ Valid YouTube channel URL: {url}")
        return True
    except YouTubeURLValidationError as e:
        print(f"✗ Invalid URL: {e}")
        return False


def scrape_channel_example(
    channel_url: str,
    max_videos: int = 5,
    show_progress: bool = True
) -> List[Dict[str, Any]]:
    """
    Example function to scrape a YouTube channel.

    Args:
        channel_url: YouTube channel URL
        max_videos: Maximum number of videos to scrape
        show_progress: Whether to show progress updates

    Returns:
        List of video dictionaries
    """
    print("\n" + "="*70)
    print("YOUTUBE CHANNEL SCRAPING EXAMPLE")
    print("="*70)

    # Initialize service
    print("\n1. Initializing Apify service...")
    try:
        service = ApifyYouTubeService()
        print("   ✓ Service initialized successfully")
    except ApifyServiceError as e:
        print(f"   ✗ Failed to initialize service: {e}")
        return []

    # Test connection
    print("\n2. Testing Apify API connection...")
    if service.test_connection():
        print("   ✓ Connection successful")
    else:
        print("   ✗ Connection failed")
        return []

    # Validate URL
    print(f"\n3. Validating channel URL...")
    if not validate_channel_url(service, channel_url):
        return []

    # Scrape channel
    print(f"\n4. Scraping {max_videos} videos from channel...")
    print(f"   Channel: {channel_url}")
    print(f"   This may take a few minutes...\n")

    try:
        callback = progress_callback if show_progress else None

        videos = service.scrape_youtube_channel(
            channel_url=channel_url,
            max_videos=max_videos,
            subtitles_language='en',
            timeout=600,  # 10 minutes
            progress_callback=callback
        )

        print(f"\n✓ Successfully scraped {len(videos)} videos!")
        return videos

    except ApifyActorError as e:
        print(f"\n✗ Actor execution failed: {e}")
        return []
    except ApifyServiceError as e:
        print(f"\n✗ Service error: {e}")
        return []
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        logger.exception("Unexpected error during scraping")
        return []


def display_video_summary(videos: List[Dict[str, Any]]) -> None:
    """
    Display a summary of scraped videos.

    Args:
        videos: List of video dictionaries
    """
    if not videos:
        print("\nNo videos to display.")
        return

    print("\n" + "="*70)
    print("SCRAPED VIDEOS SUMMARY")
    print("="*70)

    for i, video in enumerate(videos, 1):
        print(f"\n{i}. {video['title']}")
        print(f"   {'─'*66}")
        print(f"   URL:         {video['url']}")
        print(f"   Date:        {video['date']}")
        print(f"   Duration:    {video['duration']}")
        print(f"   Views:       {video['view_count']:,}")
        print(f"   Likes:       {video['like_count']:,}")
        print(f"   Channel:     {video['channel_name']}")

        # Transcript preview
        transcript = video['transcript']
        if transcript:
            preview = transcript[:200] + "..." if len(transcript) > 200 else transcript
            print(f"   Transcript:  {len(transcript):,} characters")
            print(f"   Preview:     {preview}")
        else:
            print(f"   Transcript:  (not available)")


def save_transcripts(videos: List[Dict[str, Any]], output_dir: str = "temp_transcripts") -> None:
    """
    Save video transcripts to individual text files.

    Args:
        videos: List of video dictionaries
        output_dir: Directory to save transcript files
    """
    if not videos:
        print("\nNo videos to save.")
        return

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    print("\n" + "="*70)
    print("SAVING TRANSCRIPTS")
    print("="*70)

    saved_count = 0
    for i, video in enumerate(videos, 1):
        # Create safe filename from video title
        safe_title = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in video['title'])
        safe_title = safe_title[:100]  # Limit filename length

        filename = f"{i:02d}_{safe_title}.txt"
        filepath = os.path.join(output_dir, filename)

        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                # Write metadata
                f.write(f"Title: {video['title']}\n")
                f.write(f"URL: {video['url']}\n")
                f.write(f"Date: {video['date']}\n")
                f.write(f"Channel: {video['channel_name']}\n")
                f.write(f"Duration: {video['duration']}\n")
                f.write(f"Views: {video['view_count']:,}\n")
                f.write(f"\n{'='*70}\n")
                f.write(f"TRANSCRIPT\n")
                f.write(f"{'='*70}\n\n")

                # Write transcript
                f.write(video['transcript'])

            print(f"✓ Saved: {filename}")
            saved_count += 1

        except Exception as e:
            print(f"✗ Failed to save {filename}: {e}")

    print(f"\n✓ Saved {saved_count} transcript files to {output_dir}/")


def main():
    """
    Main function - demonstrates complete workflow.
    """
    # Example channel URL - Claude Code focused AI development channel
    # Replace with actual channel URL you want to scrape
    example_url = "https://www.youtube.com/@example"

    print("""
╔══════════════════════════════════════════════════════════════════╗
║         APIFY YOUTUBE SCRAPER - USAGE EXAMPLE                    ║
║                                                                   ║
║  This script demonstrates how to scrape YouTube channels for     ║
║  AI development content, specifically focused on agentic coding  ║
║  LLMs like Claude Code.                                          ║
╚══════════════════════════════════════════════════════════════════╝
    """)

    # Check for API token
    api_token = os.getenv('APIFY_API_TOKEN')
    if not api_token:
        print("⚠️  Warning: APIFY_API_TOKEN not found in environment variables.")
        print("   Please set it in your .env file to run this example.")
        print("\n   Example .env entry:")
        print("   APIFY_API_TOKEN=your_token_here\n")
        return

    # Get user input for channel URL
    print("Enter YouTube channel URL to scrape:")
    print(f"(Press Enter to use example: {example_url})")
    user_input = input("> ").strip()

    channel_url = user_input if user_input else example_url

    # Get number of videos
    print("\nEnter number of videos to scrape (default: 5):")
    max_videos_input = input("> ").strip()

    try:
        max_videos = int(max_videos_input) if max_videos_input else 5
        max_videos = max(1, min(max_videos, 50))  # Limit between 1-50
    except ValueError:
        max_videos = 5
        print(f"Invalid input, using default: {max_videos}")

    # Run the scraping example
    videos = scrape_channel_example(
        channel_url=channel_url,
        max_videos=max_videos,
        show_progress=True
    )

    if videos:
        # Display summary
        display_video_summary(videos)

        # Ask if user wants to save transcripts
        print("\n" + "="*70)
        print("Save transcripts to files? (y/n):")
        save_choice = input("> ").strip().lower()

        if save_choice in ('y', 'yes'):
            save_transcripts(videos)

        print("\n✓ Example completed successfully!")
    else:
        print("\n✗ Example failed - no videos were scraped.")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.exception("Unexpected error in main")
        print(f"\n✗ Fatal error: {e}")
        sys.exit(1)
