# YouTube Channel RAG Tool

A professional Retrieval-Augmented Generation (RAG) system for analyzing YouTube channel content. This tool scrapes video transcripts from any YouTube channel and enables intelligent querying using Google's Gemini API with file search capabilities.

## Overview

This application allows you to:
- Scrape video titles and transcripts from any YouTube channel
- Store transcripts in a searchable vector database (Gemini File Search)
- Query the content using natural language
- Get AI-generated answers with citations to source videos

Perfect for analyzing AI development channels, educational content, technical tutorials, and staying up-to-date with the latest trends in your field.

## Features

- **YouTube Channel Scraping**: Extracts video metadata and full transcripts using Apify
- **RAG-Powered Search**: Leverages Google Gemini's file search for semantic understanding
- **Professional UI**: Clean, minimalist interface with EB Garamond typography
- **Citation Support**: All answers include references to source videos
- **Flexible Configuration**: Scrape from 1 to 100 videos per channel
- **Production Ready**: Comprehensive error handling and logging

## Architecture

```
┌─────────────────┐
│   Frontend      │  HTML/CSS/JS
│   (EB Garamond)│  Clean, professional UI
└────────┬────────┘
         │
         ↓ HTTP/REST
┌─────────────────┐
│  Flask Backend  │  Python API server
└────────┬────────┘
         │
    ┌────┴────┐
    ↓         ↓
┌─────────┐ ┌──────────────┐
│  Apify  │ │ Gemini API   │
│  API    │ │ File Search  │
└─────────┘ └──────────────┘
```

## Tech Stack

### Backend
- **Flask** - Web framework
- **Apify Client** - YouTube scraping
- **Google Gemini API** - RAG and file search
- **Python 3.8+** - Core language

### Frontend
- **Vanilla JavaScript** - No frameworks required
- **Modern CSS** - CSS Grid, Flexbox, custom properties
- **EB Garamond Font** - Professional typography

## Installation

### Prerequisites

- Python 3.8 or higher
- Apify API token ([Get one here](https://console.apify.com/account/integrations))
- Google Gemini API key ([Get one here](https://aistudio.google.com/app/apikey))

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd gemini-api-rag
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API keys:
   ```env
   APIFY_API_TOKEN=your_apify_token_here
   GOOGLE_API_KEY=your_gemini_api_key_here
   ```

4. **Start the server**
   ```bash
   python backend/app.py
   ```

5. **Open in browser**
   ```
   http://localhost:5000
   ```

## Usage

### Web Interface

1. **Enter YouTube Channel URL**
   - Format: `https://youtube.com/@channelname`
   - Also supports: `/channel/`, `/c/`, `/user/` formats

2. **Select Number of Videos**
   - Choose between 1-100 videos
   - Videos are scraped from newest to oldest

3. **Wait for Processing**
   - Scraping videos from YouTube
   - Extracting transcripts
   - Uploading to Gemini File Search

4. **Start Querying**
   - Ask questions about the content
   - Get AI-generated answers with citations
   - Click citations to view source videos

### API Endpoints

#### POST /api/scrape
Scrape a YouTube channel and create a searchable store.

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "channel_url": "https://youtube.com/@example",
    "max_videos": 10
  }'
```

**Response:**
```json
{
  "status": "success",
  "store_name": "example_20251110_120000",
  "video_count": 10,
  "message": "Successfully processed 10 videos"
}
```

#### POST /api/query
Query the RAG system with a natural language question.

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "example_20251110_120000",
    "query": "What are the main topics discussed?"
  }'
```

**Response:**
```json
{
  "response": "The main topics include...",
  "citations": [
    {
      "title": "Video Title",
      "url": "https://youtube.com/watch?v=...",
      "excerpt": "Relevant excerpt..."
    }
  ]
}
```

#### GET /api/health
Check backend health and service connectivity.

```bash
curl http://localhost:5000/api/health
```

## Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `APIFY_API_TOKEN` | Apify API authentication token | Yes |
| `GOOGLE_API_KEY` | Google Gemini API key | Yes |
| `FLASK_HOST` | Server host (default: 0.0.0.0) | No |
| `FLASK_PORT` | Server port (default: 5000) | No |
| `DEBUG` | Enable debug mode (default: True) | No |

### Apify Configuration

The tool uses the `streamers/youtube-scraper` actor with the following settings:
- **Subtitle Format**: Plaintext (optimal for RAG)
- **Sort Order**: Newest first
- **Language**: English (configurable in `apify_service.py`)

**Cost**: Approximately $0.005 per video scraped

### Gemini Configuration

File search configuration:
- **Model**: gemini-2.0-flash (fast and cost-effective)
- **Chunk Size**: 500 tokens (optimal for context)
- **Chunk Overlap**: 50 tokens (maintains continuity)
- **Storage**: Persistent (files remain until manually deleted)

**Cost**: $0.15 per 1M tokens for indexing

## Project Structure

```
gemini-api-rag/
├── backend/
│   ├── app.py                 # Flask web server
│   ├── apify_service.py       # YouTube scraping logic
│   ├── gemini_service.py      # Gemini RAG integration
│   └── utils.py               # Utility functions
├── frontend/
│   ├── index.html             # Main UI
│   ├── styles.css             # Professional styling
│   └── app.js                 # Frontend logic
├── temp_transcripts/          # Temporary transcript storage
├── .env.example               # Environment template
├── .gitignore                 # Git ignore rules
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Development

### Running in Development Mode

```bash
# Activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start server with auto-reload
FLASK_ENV=development python backend/app.py
```

### Testing

```bash
# Test service connections
python backend/test_services.py

# Test individual modules
python -m pytest tests/  # If you add tests
```

### Code Quality

The codebase follows these standards:
- **PEP 8** style guide for Python
- **Type hints** throughout
- **Comprehensive docstrings**
- **Error handling** at all levels
- **Logging** for debugging

## Troubleshooting

### Common Issues

**Backend won't start**
- Verify Python version (3.8+): `python --version`
- Check all dependencies installed: `pip install -r requirements.txt`
- Ensure `.env` file exists with valid API keys

**Scraping fails**
- Verify Apify API token is correct
- Check YouTube URL format (must be channel URL, not video URL)
- Ensure you have Apify credits available
- Check network connectivity

**RAG queries fail**
- Verify Google API key is correct
- Ensure store name exists (check `/api/stores` endpoint)
- Check Gemini API quota and billing

**Frontend not loading**
- Ensure Flask server is running: `curl http://localhost:5000/api/health`
- Check browser console for JavaScript errors
- Clear browser cache and reload

### API Rate Limits

**Apify**
- Rate limits depend on your plan
- Scraping is async, results may take 2-5 minutes
- Default timeout: 10 minutes

**Gemini**
- Free tier: 15 RPM (requests per minute)
- Pay-as-you-go: 1000 RPM
- Handle rate limit errors with exponential backoff

### Logging

Logs are output to console by default. To save to file:

```python
# In backend/app.py
import logging
logging.basicConfig(
    filename='app.log',
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
```

## Performance

### Scraping Performance
- **Time**: ~10-30 seconds per video
- **Throughput**: ~50 videos in 5-10 minutes
- **Cost**: $0.005 per video (Apify)

### Query Performance
- **Latency**: 1-3 seconds per query
- **Concurrent Users**: ~10-50 (depends on Gemini quotas)
- **Cost**: ~$0.001 per query

### Storage
- **Transcript Files**: ~10-50KB per video
- **Gemini Storage**: ~3x input size (includes embeddings)
- **Recommended**: Keep stores under 20GB for optimal performance

## Security

### Best Practices

1. **Never commit `.env` file**
   - Contains sensitive API keys
   - Already in `.gitignore`

2. **Rotate API keys regularly**
   - Especially if exposed accidentally
   - Update in `.env` file

3. **Use environment-specific keys**
   - Different keys for dev/staging/production
   - Never use production keys in development

4. **Restrict API key permissions**
   - Apify: Only enable required actors
   - Gemini: Set spending limits

### CORS Configuration

CORS is enabled for all origins by default. In production:

```python
# backend/app.py
CORS(app, resources={r"/api/*": {"origins": "https://yourdomain.com"}})
```

## Deployment

### Production Deployment

1. **Set environment to production**
   ```bash
   export FLASK_ENV=production
   export DEBUG=False
   ```

2. **Use a production server**
   ```bash
   gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
   ```

3. **Set up reverse proxy (nginx)**
   ```nginx
   server {
       listen 80;
       server_name yourdomain.com;

       location / {
           proxy_pass http://localhost:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

4. **Enable HTTPS**
   - Use Let's Encrypt for free SSL certificates
   - Configure nginx with SSL

### Docker Deployment (Optional)

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "backend.app:app"]
```

## Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Apify** - YouTube scraping infrastructure
- **Google Gemini** - Advanced RAG capabilities
- **EB Garamond** - Beautiful open-source font

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing documentation
- Review troubleshooting section

## Roadmap

Future enhancements:
- [ ] Support for multiple channels in one store
- [ ] Export chat history
- [ ] Advanced filtering (date range, video length)
- [ ] Playlist support
- [ ] Multi-language transcript support
- [ ] User authentication
- [ ] Store sharing capabilities

## Version History

### v1.0.0 (2025-11-10)
- Initial release
- YouTube channel scraping
- Gemini RAG integration
- Professional web interface
- Complete API documentation
