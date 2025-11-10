# API Usage Examples

This document provides examples for testing the YouTube Channel RAG API using curl commands.

## Prerequisites

- Server running on `http://localhost:5000`
- Valid API keys configured in `.env` file

## 1. Health Check

Test if the API is running and services are connected:

```bash
curl -X GET http://localhost:5000/api/health | jq
```

**Expected Response:**
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

## 2. Scrape YouTube Channel

Scrape a YouTube channel and create a RAG corpus:

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "channel_url": "https://youtube.com/@IndyDevDan",
    "max_videos": 5
  }' | jq
```

**Expected Response:**
```json
{
  "status": "success",
  "store_name": "IndyDevDan_20231110_120000",
  "video_count": 5,
  "message": "Successfully processed 5 videos"
}
```

**Note:** This operation may take 1-5 minutes depending on the number of videos.

## 3. List All Stores

Get a list of all available stores:

```bash
curl -X GET http://localhost:5000/api/stores | jq
```

**Expected Response:**
```json
{
  "stores": {
    "IndyDevDan_20231110_120000": {
      "channel_url": "https://youtube.com/@IndyDevDan",
      "video_count": 5,
      "created_at": "2023-11-10T12:00:00.000Z",
      "corpus_name": "corpora/...",
      "file_count": 5
    }
  },
  "count": 1
}
```

## 4. Get Store Information

Get detailed information about a specific store:

```bash
curl -X GET http://localhost:5000/api/store/info/IndyDevDan_20231110_120000 | jq
```

**Expected Response:**
```json
{
  "store_name": "IndyDevDan_20231110_120000",
  "channel_url": "https://youtube.com/@IndyDevDan",
  "video_count": 5,
  "file_count": 5,
  "created_at": "2023-11-10T12:00:00.000Z",
  "corpus_name": "corpora/..."
}
```

## 5. Query RAG System

Ask questions about the video transcripts:

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "IndyDevDan_20231110_120000",
    "query": "What are the latest features in Claude Code?"
  }' | jq
```

**Expected Response:**
```json
{
  "response": "Based on the video transcripts, the latest features in Claude Code include...",
  "citations": [
    {
      "source_id": 1,
      "chunk_id": "corpora/.../documents/.../chunks/...",
      "relevance_score": 0.95
    }
  ],
  "query": "What are the latest features in Claude Code?"
}
```

## 6. Delete Store

Remove a store from local storage:

```bash
curl -X DELETE http://localhost:5000/api/store/IndyDevDan_20231110_120000 | jq
```

**Expected Response:**
```json
{
  "status": "success",
  "message": "Store deleted successfully"
}
```

**Note:** This only removes the store metadata. The Gemini corpus remains in your Google account.

## Example Queries for AI Development Channels

Here are some example queries you might ask about AI development channels:

### General Features
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "YOUR_STORE_NAME",
    "query": "What are the main features of Claude Code?"
  }' | jq
```

### Tips and Tricks
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "YOUR_STORE_NAME",
    "query": "What are the best practices for using agentic coding tools?"
  }' | jq
```

### Comparisons
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "YOUR_STORE_NAME",
    "query": "How does Claude Code compare to other AI coding assistants?"
  }' | jq
```

### Latest Updates
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "YOUR_STORE_NAME",
    "query": "What are the latest updates and improvements?"
  }' | jq
```

### Workflow Optimization
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "YOUR_STORE_NAME",
    "query": "How can I optimize my workflow with these tools?"
  }' | jq
```

### Troubleshooting
```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "YOUR_STORE_NAME",
    "query": "What are common issues and how to solve them?"
  }' | jq
```

## Error Examples

### Invalid Request (400)
```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "channel_url": "invalid-url"
  }' | jq
```

**Response:**
```json
{
  "status": "error",
  "message": "Invalid YouTube URL"
}
```

### Store Not Found (404)
```bash
curl -X GET http://localhost:5000/api/store/info/nonexistent_store | jq
```

**Response:**
```json
{
  "error": "Store 'nonexistent_store' not found"
}
```

## Testing Multiple Channels

You can scrape multiple channels and compare their content:

```bash
# Scrape first channel
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"channel_url": "https://youtube.com/@channel1", "max_videos": 5}' | jq

# Scrape second channel
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"channel_url": "https://youtube.com/@channel2", "max_videos": 5}' | jq

# Query both stores
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"store_name": "channel1_...", "query": "Your question"}' | jq

curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{"store_name": "channel2_...", "query": "Your question"}' | jq
```

## Python Examples

If you prefer Python, here are equivalent examples using the `requests` library:

```python
import requests

BASE_URL = "http://localhost:5000"

# Health check
response = requests.get(f"{BASE_URL}/api/health")
print(response.json())

# Scrape channel
response = requests.post(
    f"{BASE_URL}/api/scrape",
    json={
        "channel_url": "https://youtube.com/@IndyDevDan",
        "max_videos": 5
    }
)
store_info = response.json()
store_name = store_info["store_name"]
print(f"Created store: {store_name}")

# Query
response = requests.post(
    f"{BASE_URL}/api/query",
    json={
        "store_name": store_name,
        "query": "What are the latest features in Claude Code?"
    }
)
result = response.json()
print(f"Response: {result['response']}")
print(f"Citations: {result['citations']}")
```

## Notes

- Replace `YOUR_STORE_NAME` with the actual store name from the scrape response
- All timestamps are in UTC
- The `jq` command is used for pretty-printing JSON (install with `apt-get install jq` or `brew install jq`)
- For Windows PowerShell, replace `\` line continuations with `` ` ``
