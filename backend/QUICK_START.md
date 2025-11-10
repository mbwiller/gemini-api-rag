# Apify Service - Quick Start Guide

## 🚀 Quick Setup (30 seconds)

### 1. Set API Token
Add to your `.env` file:
```bash
APIFY_API_TOKEN=your_token_here
```
Get token from: https://console.apify.com/account/integrations

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Use the Service
```python
from backend.apify_service import ApifyYouTubeService

# Initialize
service = ApifyYouTubeService()

# Scrape
videos = service.scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=10
)

# Process
for video in videos:
    print(f"{video['title']}: {video['transcript'][:100]}...")
```

## 📦 What You Get

Each video returns:
```python
{
    'title': str,          # Video title
    'url': str,            # YouTube URL
    'date': str,           # Upload date
    'transcript': str,     # Full transcript (plaintext)
    'description': str,    # Video description
    'duration': str,       # Duration
    'view_count': int,     # Views
    'like_count': int,     # Likes
    'channel_name': str,   # Channel name
    'channel_url': str     # Channel URL
}
```

## ✅ Valid URL Formats

```python
# All of these work:
"https://www.youtube.com/@username"
"https://www.youtube.com/channel/UCxxxxxx"
"https://www.youtube.com/c/channelname"
"https://www.youtube.com/user/username"
```

## 🎯 Common Use Cases

### 1. Basic Scraping
```python
from backend.apify_service import scrape_youtube_channel

videos = scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=5
)
```

### 2. With Progress Tracking
```python
def show_progress(status, elapsed, info):
    print(f"[{elapsed:.1f}s] {status}")

service = ApifyYouTubeService()
videos = service.scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=10,
    progress_callback=show_progress
)
```

### 3. Validate URL First
```python
service = ApifyYouTubeService()

try:
    service.validate_youtube_url(url)
    videos = service.scrape_youtube_channel(url, max_videos=10)
except YouTubeURLValidationError as e:
    print(f"Invalid URL: {e}")
```

### 4. Custom Language & Timeout
```python
videos = service.scrape_youtube_channel(
    channel_url="https://www.youtube.com/@example",
    max_videos=10,
    subtitles_language='es',  # Spanish
    timeout=900               # 15 minutes
)
```

### 5. Error Handling
```python
try:
    videos = service.scrape_youtube_channel(url, max_videos=10)
except YouTubeURLValidationError as e:
    print(f"Bad URL: {e}")
except ApifyActorError as e:
    print(f"Scraping failed: {e}")
except ApifyServiceError as e:
    print(f"Service error: {e}")
```

## 🧪 Testing

```bash
# Run test suite
python3 backend/test_apify_service.py

# Run example script
python3 backend/example_usage.py

# Syntax check
python3 -m py_compile backend/apify_service.py
```

## ⚙️ Configuration

### Available Parameters

```python
ApifyYouTubeService(
    api_token=None           # Optional, defaults to env var
)

scrape_youtube_channel(
    channel_url,             # Required: YouTube channel URL
    max_videos,              # Required: Number of videos (1-50)
    subtitles_language='en', # Optional: Language code
    timeout=600,             # Optional: Seconds to wait
    progress_callback=None   # Optional: Progress function
)
```

### Constants (in apify_service.py)

```python
ACTOR_ID = "streamers/youtube-scraper"
DEFAULT_TIMEOUT = 600  # 10 minutes
POLL_INTERVAL = 5      # Poll every 5 seconds
```

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "API token not found" | Set `APIFY_API_TOKEN` in `.env` |
| "Timed out" | Increase `timeout` or reduce `max_videos` |
| "No transcript" | Some videos don't have subtitles (normal) |
| Import errors | Run `pip install -r requirements.txt` |
| "Invalid URL" | Check URL format (must be channel URL) |

## 📊 Performance

- **Setup**: <1 second
- **URL validation**: Instant
- **Per video**: ~30-60 seconds
- **10 videos**: ~5-15 minutes
- **Memory**: <50 MB

## 📚 Full Documentation

- **Complete API Reference**: `backend/APIFY_SERVICE_README.md`
- **Integration Guide**: `APIFY_INTEGRATION_SUMMARY.md`
- **Example Script**: `backend/example_usage.py`
- **Test Suite**: `backend/test_apify_service.py`

## 🎓 Best Practices

1. ✅ Start with 5 videos for testing
2. ✅ Always validate URLs first
3. ✅ Use progress callbacks for visibility
4. ✅ Handle exceptions properly
5. ✅ Set appropriate timeouts
6. ✅ Test connection before big jobs
7. ✅ Check logs when debugging

## 💡 Pro Tips

```python
# 1. Test connection before scraping
service = ApifyYouTubeService()
if service.test_connection():
    videos = service.scrape_youtube_channel(url, 10)

# 2. Filter videos with transcripts
videos_with_text = [v for v in videos if len(v['transcript']) > 100]

# 3. Sort by views
sorted_videos = sorted(videos, key=lambda x: x['view_count'], reverse=True)

# 4. Save to files
for i, video in enumerate(videos, 1):
    with open(f'video_{i}.txt', 'w') as f:
        f.write(video['transcript'])

# 5. Get video metadata only
for video in videos:
    print(f"{video['title']} ({video['date']})")
    print(f"  {video['view_count']:,} views, {video['like_count']:,} likes")
```

## 🔗 Quick Links

- Apify Actor: https://apify.com/streamers/youtube-scraper
- Python SDK Docs: https://docs.apify.com/api/client/python
- Get API Token: https://console.apify.com/account/integrations

## 📞 Support

Need help?
1. Check `backend/APIFY_SERVICE_README.md` for detailed docs
2. Run `python3 backend/example_usage.py` for interactive demo
3. Review error messages (they're detailed!)
4. Check logs with `logging.basicConfig(level=logging.DEBUG)`

---

**Ready to scrape?** Start with the example above! 🎬
