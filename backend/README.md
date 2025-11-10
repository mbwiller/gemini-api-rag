# Backend API Documentation

## Overview

This Flask backend provides a REST API for scraping YouTube channel videos and querying their transcripts using Google Gemini's RAG (Retrieval-Augmented Generation) capabilities.

---

## GeminiFileSearchService Module

### Overview

The `GeminiFileSearchService` is a comprehensive Python module for integrating with Google's Gemini API File Search functionality. It provides production-ready RAG capabilities specifically designed for YouTube video transcript search and analysis.

### Key Features

- **File Search Store Management**: Create, retrieve, and delete corpus stores
- **Video Transcript Upload**: Upload transcripts with rich metadata (title, URL, date, video ID)
- **Optimal Chunking**: Configured for 500 tokens per chunk with 50 token overlap
- **RAG Query System**: Query transcripts with automatic citation support
- **Store Persistence**: Save/load store IDs to JSON for session persistence
- **Comprehensive Error Handling**: Try-catch blocks with detailed logging
- **Production Ready**: Timeouts, polling, retry logic, and edge case handling

### Installation & Setup

#### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

Required packages:
- `google-genai>=1.0.1` - Gemini API SDK
- `python-dotenv>=1.0.0` - Environment variable management

#### 2. Configure API Key

Set your Google API key in `.env`:

```env
GOOGLE_API_KEY=your_google_api_key_here
```

Or pass directly to the service:

```python
from backend.gemini_service import GeminiFileSearchService

service = GeminiFileSearchService(api_key="your_api_key")
```

### Quick Start

```python
from backend.gemini_service import GeminiFileSearchService

# Initialize service
service = GeminiFileSearchService()

# Create a store
store = service.create_file_search_store(
    display_name="AI_Coding_Channel",
    description="Transcripts about AI development"
)

# Upload a transcript
video_data = {
    "title": "Claude Code Tutorial",
    "url": "https://youtube.com/watch?v=abc123",
    "date": "2025-11-10",
    "video_id": "abc123"
}
service.upload_transcript_to_store(
    "AI_Coding_Channel",
    video_data,
    "/path/to/transcript.txt"
)

# Query the store
result = service.query_transcripts(
    "AI_Coding_Channel",
    "How do I use Claude Code for API integration?"
)
print(result['answer'])
```

### Complete API Reference

#### Class: `GeminiFileSearchService`

##### Constructor

```python
GeminiFileSearchService(api_key: Optional[str] = None)
```

**Parameters:**
- `api_key` (str, optional): Google API key. Uses `GOOGLE_API_KEY` env var if not provided.

**Raises:**
- `ValueError`: If no API key found

**Example:**
```python
service = GeminiFileSearchService()  # Uses env var
service = GeminiFileSearchService(api_key="key")  # Direct key
```

---

##### Method: `create_file_search_store()`

Create a new file search store (corpus) for storing video transcripts.

```python
create_file_search_store(
    display_name: str,
    description: Optional[str] = None
) -> Optional[types.Corpus]
```

**Parameters:**
- `display_name` (str): Human-readable name for the store
- `description` (str, optional): Description of the store's purpose

**Returns:**
- `Corpus` object if successful, `None` otherwise

**Example:**
```python
store = service.create_file_search_store(
    display_name="AI_Coding_Channel",
    description="Transcripts from AI coding tutorials"
)
```

---

##### Method: `upload_transcript_to_store()`

Upload a video transcript to a file search store with metadata.

```python
upload_transcript_to_store(
    store_name: str,
    video_data: Dict[str, Any],
    transcript_file_path: str
) -> Optional[str]
```

**Parameters:**
- `store_name` (str): Display name of the store
- `video_data` (dict): Video metadata dictionary containing:
  - `title` (str): Video title
  - `url` (str): Video URL
  - `date` (str|datetime): Upload/publish date
  - `video_id` (str): Unique video identifier
- `transcript_file_path` (str): Path to the transcript text file

**Returns:**
- Document name (str) if successful, `None` otherwise

**Example:**
```python
video_data = {
    "title": "Claude Code Tutorial",
    "url": "https://youtube.com/watch?v=abc123",
    "date": "2025-11-10",
    "video_id": "abc123"
}
doc_name = service.upload_transcript_to_store(
    "AI_Coding_Channel",
    video_data,
    "/path/to/transcript.txt"
)
```

---

##### Method: `query_transcripts()`

Query video transcripts using RAG with citation support.

```python
query_transcripts(
    store_name: str,
    query: str,
    max_results: int = 5,
    temperature: float = 0.7
) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `store_name` (str): Display name of the store to query
- `query` (str): User's question or search query
- `max_results` (int): Maximum chunks to retrieve (default: 5)
- `temperature` (float): Model temperature 0.0-1.0 (default: 0.7)

**Returns:**
Dictionary containing:
- `answer` (str): Generated response
- `citations` (list): Source citations with titles, URLs, excerpts
- `grounding_metadata` (dict): Additional grounding information
- `query` (str): Original query
- `timestamp` (str): ISO timestamp

**Example:**
```python
result = service.query_transcripts(
    "AI_Coding_Channel",
    "How do I use Claude Code for API integration?"
)
print(result['answer'])
for citation in result['citations']:
    print(f"Source: {citation['title']}")
```

---

##### Method: `get_store_info()`

Get detailed information about a store.

```python
get_store_info(display_name: str) -> Optional[Dict[str, Any]]
```

**Parameters:**
- `display_name` (str): Display name of the store

**Returns:**
Dictionary containing:
- `name` (str): Store name
- `display_name` (str): Display name
- `description` (str): Store description
- `resource_name` (str): Full resource identifier
- `document_count` (int): Number of documents
- `created_time` (str): ISO timestamp
- `updated_time` (str): ISO timestamp

**Example:**
```python
info = service.get_store_info("AI_Coding_Channel")
print(f"Store has {info['document_count']} documents")
```

---

##### Method: `delete_store()`

Delete a file search store and all its contents.

```python
delete_store(display_name: str) -> bool
```

**Parameters:**
- `display_name` (str): Display name of the store to delete

**Returns:**
- `True` if deletion successful, `False` otherwise

**Warning:** This operation is irreversible!

**Example:**
```python
success = service.delete_store("AI_Coding_Channel")
```

---

##### Method: `list_stores()`

List all registered stores.

```python
list_stores() -> List[Dict[str, str]]
```

**Returns:**
List of dictionaries with:
- `display_name` (str)
- `resource_name` (str)

**Example:**
```python
stores = service.list_stores()
for store in stores:
    print(f"{store['display_name']}: {store['resource_name']}")
```

---

##### Method: `list_documents_in_store()`

List all documents in a store.

```python
list_documents_in_store(store_name: str) -> Optional[List[Dict[str, Any]]]
```

**Parameters:**
- `store_name` (str): Display name of the store

**Returns:**
List of document dictionaries with:
- `name` (str): Document ID
- `display_name` (str): Document title
- `metadata` (dict): Custom metadata
- `created_time` (str): ISO timestamp

**Example:**
```python
docs = service.list_documents_in_store("AI_Coding_Channel")
for doc in docs:
    print(f"{doc['display_name']} - {doc['created_time']}")
```

---

##### Method: `delete_document_from_store()`

Delete a specific document from a store.

```python
delete_document_from_store(
    store_name: str,
    document_name: str
) -> bool
```

**Parameters:**
- `store_name` (str): Display name of the store
- `document_name` (str): Document ID to delete

**Returns:**
- `True` if successful, `False` otherwise

---

##### Method: `get_service_stats()`

Get overall service statistics.

```python
get_service_stats() -> Dict[str, Any]
```

**Returns:**
Dictionary containing:
- `total_stores` (int)
- `total_documents` (int)
- `registered_stores` (list)
- `timestamp` (str)

**Example:**
```python
stats = service.get_service_stats()
print(f"Total stores: {stats['total_stores']}")
print(f"Total documents: {stats['total_documents']}")
```

---

### Module-Level Functions

#### `get_service()`

Get or create a singleton service instance.

```python
from backend.gemini_service import get_service

service = get_service()  # Uses cached instance
service = get_service(api_key="key")  # Override API key
```

#### `reset_service()`

Reset the singleton service instance.

```python
from backend.gemini_service import reset_service

reset_service()  # Clear cached instance
```

---

### Configuration Constants

```python
DEFAULT_MODEL = "gemini-2.0-flash"
CHUNK_SIZE_TOKENS = 500
CHUNK_OVERLAP_TOKENS = 50
MAX_POLL_ATTEMPTS = 60
POLL_INTERVAL_SECONDS = 2
STORE_CONFIG_FILE = "store_config.json"
```

---

### Error Handling

The module provides comprehensive error handling:

1. **APIError**: Gemini API-specific errors
2. **ValueError**: Invalid parameters
3. **FileNotFoundError**: Missing transcript files
4. **Generic Exception**: All other errors

All errors are logged with detailed messages.

**Example Error Handling:**
```python
try:
    result = service.query_transcripts(store_name, query)
    if result.get('error'):
        print(f"Query failed: {result['error']}")
    else:
        print(result['answer'])
except Exception as e:
    print(f"Unexpected error: {e}")
```

---

### Store Persistence

Store configurations are automatically saved to `store_config.json`:

```json
{
  "AI_Coding_Channel": "corpora/abc123/corpuses/xyz789",
  "Tech_Tutorials": "corpora/def456/corpuses/uvw012"
}
```

This allows the service to reconnect to existing stores across sessions.

---

### Best Practices

1. **Chunking Strategy**: Default 500 tokens/chunk, 50 token overlap is optimal for most use cases
2. **Metadata**: Always include title, URL, date, and video_id for better search
3. **Error Handling**: Wrap all operations in try-except blocks
4. **Store Naming**: Use descriptive names with timestamps for uniqueness
5. **Cleanup**: Delete unused stores to manage quota
6. **Logging**: Monitor logs for API errors and performance issues
7. **Citations**: Always display citations to users for transparency

---

### Example Use Cases

#### Use Case 1: Build a YouTube Channel Knowledge Base

```python
service = GeminiFileSearchService()

# Create store for channel
store = service.create_file_search_store(
    "TechChannel_2025",
    "Tech tutorials and coding videos"
)

# Upload all channel transcripts
for video in channel_videos:
    service.upload_transcript_to_store(
        "TechChannel_2025",
        {
            "title": video['title'],
            "url": video['url'],
            "date": video['published_date'],
            "video_id": video['id']
        },
        video['transcript_file']
    )

# Query the knowledge base
result = service.query_transcripts(
    "TechChannel_2025",
    "What are the latest Python frameworks?"
)
```

#### Use Case 2: Multi-Channel Comparison

```python
# Create stores for multiple channels
for channel in channels:
    store_name = f"{channel['name']}_store"
    service.create_file_search_store(store_name)
    # Upload transcripts...

# Query all channels
for store in service.list_stores():
    result = service.query_transcripts(
        store['display_name'],
        "What is the consensus on AI safety?"
    )
    print(f"{store['display_name']}: {result['answer']}")
```

---

### Running Examples

A comprehensive example script is provided:

```bash
python backend/gemini_service_example.py
```

This demonstrates all features with sample data.

---

### Troubleshooting

**Issue**: `ValueError: Google API key is required`
- **Solution**: Set `GOOGLE_API_KEY` in `.env` file

**Issue**: Store not found after creation
- **Solution**: Check `store_config.json` exists and has correct permissions

**Issue**: Upload fails silently
- **Solution**: Check logs for detailed error messages

**Issue**: Query returns empty results
- **Solution**: Wait 5-10 seconds after upload for indexing to complete

**Issue**: Citations missing in query results
- **Solution**: Ensure metadata was provided during upload

---

## Architecture

### Components

1. **app.py** - Main Flask application with API endpoints
2. **apify_service.py** - Service for scraping YouTube videos using Apify
3. **gemini_service.py** - Service for uploading transcripts and RAG queries
4. **stores.json** - Persistent storage for corpus metadata

## API Endpoints

### Health Check

```http
GET /api/health
```

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2023-11-10T12:00:00.000Z",
  "services": {
    "apify": true,
    "gemini": true,
    "apify_connection": true,
    "gemini_connection": true
  }
}
```

### Scrape YouTube Channel

```http
POST /api/scrape
```

**Request Body:**
```json
{
  "channel_url": "https://youtube.com/@channelname",
  "max_videos": 10
}
```

**Response:**
```json
{
  "status": "success",
  "store_name": "channelname_20231110_120000",
  "video_count": 10,
  "message": "Successfully processed 10 videos"
}
```

**Process:**
1. Scrapes YouTube channel using Apify
2. Creates transcript files for each video
3. Uploads files to Gemini corpus
4. Saves store metadata
5. Cleans up temporary files

### Query RAG System

```http
POST /api/query
```

**Request Body:**
```json
{
  "store_name": "channelname_20231110_120000",
  "query": "What are the latest features in Claude Code?"
}
```

**Response:**
```json
{
  "response": "Based on the video transcripts...",
  "citations": [
    {
      "source_id": 1,
      "chunk_id": "corpora/...",
      "relevance_score": 0.95
    }
  ],
  "query": "What are the latest features in Claude Code?"
}
```

### List All Stores

```http
GET /api/stores
```

**Response:**
```json
{
  "stores": {
    "channelname_20231110_120000": {
      "channel_url": "https://youtube.com/@channel",
      "video_count": 10,
      "created_at": "2023-11-10T12:00:00.000Z",
      "corpus_name": "corpora/...",
      "file_count": 10
    }
  },
  "count": 1
}
```

### Get Store Information

```http
GET /api/store/info/<store_name>
```

**Response:**
```json
{
  "store_name": "channelname_20231110_120000",
  "channel_url": "https://youtube.com/@channel",
  "video_count": 10,
  "file_count": 10,
  "created_at": "2023-11-10T12:00:00.000Z",
  "corpus_name": "corpora/..."
}
```

### Delete Store

```http
DELETE /api/store/<store_name>
```

**Response:**
```json
{
  "status": "success",
  "message": "Store deleted successfully"
}
```

**Note:** This only removes the store from local metadata. The Gemini corpus remains.

## Error Handling

All endpoints return appropriate HTTP status codes:

- **200** - Success
- **400** - Bad Request (validation errors)
- **404** - Resource Not Found
- **500** - Internal Server Error
- **503** - Service Unavailable

**Error Response Format:**
```json
{
  "error": "Error message",
  "status": 400
}
```

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the project root:

```env
# Apify API Configuration
APIFY_API_TOKEN=your_apify_api_token_here

# Google Gemini API Configuration
GOOGLE_API_KEY=your_google_api_key_here

# Flask Configuration
FLASK_ENV=development
FLASK_HOST=0.0.0.0
FLASK_PORT=5000

# Optional: Enable debug mode (set to False in production)
DEBUG=True
```

### 3. Run the Server

```bash
python backend/app.py
```

Or using gunicorn for production:

```bash
gunicorn -w 4 -b 0.0.0.0:5000 backend.app:app
```

## Data Flow

### Scraping Process

```
1. User submits channel URL + max_videos
   ↓
2. Apify scrapes YouTube channel
   ↓
3. Extract video metadata + transcripts
   ↓
4. Create transcript files (.txt)
   ↓
5. Upload files to Gemini corpus
   ↓
6. Save store metadata to stores.json
   ↓
7. Clean up temporary files
   ↓
8. Return store_name to user
```

### Query Process

```
1. User submits query + store_name
   ↓
2. Load corpus_name from stores.json
   ↓
3. Query Gemini corpus for relevant chunks
   ↓
4. Build context from chunks
   ↓
5. Generate answer using Gemini
   ↓
6. Return response + citations
```

## File Structure

```
backend/
├── app.py                  # Main Flask application
├── apify_service.py        # Apify scraping service
├── gemini_service.py       # Gemini RAG service
├── stores.json            # Store metadata (auto-generated)
└── README.md              # This file
```

## Logging

The application uses Python's logging module with INFO level by default. Logs include:

- Service initialization
- API requests and responses
- Scraping progress
- File operations
- Errors and exceptions

## Validation

### Scrape Request Validation

- `channel_url` must be a valid YouTube URL
- `max_videos` must be an integer between 1 and 100

### Query Request Validation

- `store_name` must be a non-empty string
- `query` must be a non-empty string (max 5000 characters)
- Store must exist in stores.json

## Security Considerations

1. **API Keys**: Store in `.env` file, never commit to git
2. **CORS**: Currently enabled for all origins (restrict in production)
3. **Input Validation**: All inputs are validated and sanitized
4. **Error Messages**: Generic errors in production, detailed in development
5. **File Operations**: Sandboxed to specific directories

## Performance Considerations

1. **Scraping**: Can take 1-5 minutes depending on video count
2. **File Upload**: Batch uploads to Gemini (consider rate limits)
3. **Query**: Response time depends on corpus size and query complexity
4. **Cleanup**: Temporary files are cleaned up after upload

## Troubleshooting

### Services Not Initialized

- Check API keys in `.env` file
- Verify keys are valid by testing connections

### Scraping Fails

- Verify Apify API token is valid
- Check channel URL is correct
- Ensure channel has videos with English subtitles

### Query Fails

- Verify store exists (check `/api/stores`)
- Ensure Gemini API key is valid
- Check corpus was created successfully

### File Permission Errors

- Ensure write permissions for `temp_transcripts/` directory
- Check write permissions for `stores.json`

## Development

### Running in Debug Mode

Set `DEBUG=True` in `.env` file for detailed error messages and auto-reload.

### Testing Endpoints

Use tools like curl, Postman, or httpie:

```bash
# Health check
curl http://localhost:5000/api/health

# Scrape channel
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"channel_url": "https://youtube.com/@channel", "max_videos": 5}'

# Query
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"store_name": "channel_123", "query": "What is Claude Code?"}'
```

## Production Deployment

1. Set `DEBUG=False` in `.env`
2. Use gunicorn or uwsgi as WSGI server
3. Set up reverse proxy (nginx/Apache)
4. Configure CORS for specific origins
5. Set up logging to files/external service
6. Implement rate limiting
7. Add authentication/authorization if needed
8. Monitor API usage and performance

## License

See main project LICENSE file.
