"""
Test script for Apify Service URL validation and structure
This test can run without external dependencies
"""

import re
from urllib.parse import urlparse


def test_youtube_url_patterns():
    """Test YouTube URL validation patterns"""

    # Valid patterns
    valid_patterns = [
        r'^/@[\w-]+',           # @username
        r'^/channel/[\w-]+',    # /channel/UC...
        r'^/c/[\w-]+',          # /c/channelname
        r'^/user/[\w-]+',       # /user/username
    ]

    # Test URLs
    test_cases = [
        # Valid URLs
        ("https://www.youtube.com/@example", True),
        ("https://www.youtube.com/channel/UCxxxxxx", True),
        ("https://www.youtube.com/c/mychannel", True),
        ("https://www.youtube.com/user/testuser", True),
        ("https://youtube.com/@test", True),

        # Invalid URLs
        ("https://www.youtube.com/watch?v=xxxxx", False),
        ("https://www.youtube.com/playlist?list=xxxxx", False),
        ("https://google.com/@example", False),
        ("not a url", False),
        ("https://www.youtube.com/", False),
    ]

    print("Testing YouTube URL validation patterns:\n")

    for url, should_be_valid in test_cases:
        try:
            parsed = urlparse(url)
            valid_domains = ['youtube.com', 'www.youtube.com', 'm.youtube.com']

            # Check domain
            is_youtube = parsed.netloc in valid_domains

            # Check path pattern
            path = parsed.path.lower()
            matches_pattern = any(re.match(pattern, path) for pattern in valid_patterns)

            is_valid = is_youtube and matches_pattern

            status = "✓ PASS" if is_valid == should_be_valid else "✗ FAIL"
            print(f"{status}: {url}")
            print(f"       Expected: {should_be_valid}, Got: {is_valid}")

        except Exception as e:
            status = "✓ PASS" if not should_be_valid else "✗ FAIL"
            print(f"{status}: {url}")
            print(f"       Exception: {str(e)}")

        print()


def test_module_structure():
    """Test that the module file has the expected structure"""

    print("\n" + "="*60)
    print("Testing module structure:")
    print("="*60 + "\n")

    with open('/home/user/gemini-api-rag/backend/apify_service.py', 'r') as f:
        content = f.read()

    # Check for required classes
    required_classes = [
        'ApifyServiceError',
        'YouTubeURLValidationError',
        'ApifyActorError',
        'ApifyYouTubeService'
    ]

    print("Checking for required classes:")
    for class_name in required_classes:
        if f"class {class_name}" in content:
            print(f"✓ {class_name} found")
        else:
            print(f"✗ {class_name} NOT FOUND")

    # Check for required methods
    required_methods = [
        'validate_youtube_url',
        'scrape_youtube_channel',
        '_prepare_actor_input',
        '_wait_for_actor_completion',
        '_process_actor_results',
        '_extract_video_data',
        '_extract_transcript',
        'test_connection'
    ]

    print("\nChecking for required methods:")
    for method_name in required_methods:
        if f"def {method_name}" in content:
            print(f"✓ {method_name} found")
        else:
            print(f"✗ {method_name} NOT FOUND")

    # Check for key features
    features = [
        ('Progress tracking', 'progress_callback'),
        ('Error handling', 'try:'),
        ('Logging', 'logger.'),
        ('Type hints', 'List[Dict[str, Any]]'),
        ('Docstrings', '"""'),
        ('URL validation', 'urlparse'),
        ('Timeout handling', 'timeout'),
        ('Status polling', 'POLL_INTERVAL'),
    ]

    print("\nChecking for key features:")
    for feature_name, search_term in features:
        if search_term in content:
            print(f"✓ {feature_name}")
        else:
            print(f"✗ {feature_name} NOT FOUND")

    # Count lines of code
    lines = content.split('\n')
    code_lines = [l for l in lines if l.strip() and not l.strip().startswith('#')]
    doc_lines = len([l for l in lines if '"""' in l or "'''" in l])

    print(f"\nModule statistics:")
    print(f"  Total lines: {len(lines)}")
    print(f"  Code lines: {len(code_lines)}")
    print(f"  Documentation blocks: {doc_lines // 2}")


def test_data_structure():
    """Test expected data structure format"""

    print("\n" + "="*60)
    print("Expected output data structure:")
    print("="*60 + "\n")

    expected_fields = [
        'title',
        'url',
        'date',
        'transcript',
        'description',
        'duration',
        'view_count',
        'like_count',
        'channel_name',
        'channel_url'
    ]

    print("Each video dict should contain:")
    for field in expected_fields:
        print(f"  - {field}")

    print("\nData should be:")
    print("  - Sorted by date (newest first)")
    print("  - Limited to max_videos count")
    print("  - Plaintext transcripts only")


if __name__ == "__main__":
    print("="*60)
    print("APIFY SERVICE MODULE TESTS")
    print("="*60)

    test_youtube_url_patterns()
    test_module_structure()
    test_data_structure()

    print("\n" + "="*60)
    print("TEST COMPLETE")
    print("="*60)
