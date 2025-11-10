# Quick Start Guide

## Get Up and Running in 5 Minutes

### Step 1: Get API Keys (2 minutes)

1. **Apify API Key**
   - Go to: https://console.apify.com/account/integrations
   - Copy your API token

2. **Google Gemini API Key**
   - Go to: https://aistudio.google.com/app/apikey
   - Create and copy your API key

### Step 2: Configure Environment (30 seconds)

```bash
# Copy the example file
cp .env.example .env

# Edit .env and paste your API keys
# APIFY_API_TOKEN=your_token_here
# GOOGLE_API_KEY=your_key_here
```

### Step 3: Start the Server (2 minutes)

```bash
# Quick start (recommended)
./run.sh

# Or manual start
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python backend/app.py
```

Server will start at: **http://localhost:5000**

### Step 4: Test the API (30 seconds)

```bash
# Health check
curl http://localhost:5000/api/health | jq

# If you see "status": "healthy" - you're ready!
```

## First Scrape

### Scrape a YouTube Channel

```bash
curl -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{
    "channel_url": "https://youtube.com/@IndyDevDan",
    "max_videos": 3
  }' | jq
```

**Wait 1-2 minutes for completion**

You'll get a response with a `store_name` - save this!

```json
{
  "status": "success",
  "store_name": "IndyDevDan_20231110_120000",
  "video_count": 3,
  "message": "Successfully processed 3 videos"
}
```

## First Query

### Ask a Question

```bash
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d '{
    "store_name": "IndyDevDan_20231110_120000",
    "query": "What are the main topics covered in these videos?"
  }' | jq
```

You'll get an AI-generated answer based on the video transcripts!

```json
{
  "response": "Based on the video transcripts, the main topics covered include...",
  "citations": [...],
  "query": "What are the main topics covered in these videos?"
}
```

## Common Commands

### List All Stores
```bash
curl http://localhost:5000/api/stores | jq
```

### Get Store Details
```bash
curl http://localhost:5000/api/store/info/YOUR_STORE_NAME | jq
```

### Delete a Store
```bash
curl -X DELETE http://localhost:5000/api/store/YOUR_STORE_NAME | jq
```

## Recommended YouTube Channels for AI Development

Try scraping these channels focused on AI coding and LLMs:

```bash
# Example channels (replace with actual URLs)
- @IndyDevDan - Claude Code tutorials
- @AIJason - AI development insights
- @AllAboutAI - AI tool reviews
- @mreflow - Coding with AI
- @ColeMedin - AI agent development
```

## Example Queries to Try

After scraping a channel, try these questions:

```bash
# General overview
"What are the main topics covered?"

# Specific features
"What new features were mentioned for Claude Code?"

# Best practices
"What are the recommended best practices?"

# Comparisons
"How do the tools compare to each other?"

# Tips and tricks
"What productivity tips were shared?"

# Problems and solutions
"What common issues were discussed and how to solve them?"
```

## Troubleshooting

### "Services not initialized"
- Check your API keys in `.env` file
- Make sure they're not empty or have placeholder text

### "Invalid YouTube URL"
- Use format: `https://youtube.com/@channelname`
- Or: `https://youtube.com/channel/UCxxxxx`

### "No videos with valid transcripts found"
- Channel needs to have English subtitles/captions
- Try a different channel or increase max_videos

### Port 5000 already in use
```bash
# Change port in .env
FLASK_PORT=8000

# Or kill existing process
lsof -ti:5000 | xargs kill -9
```

## Full Workflow Example

```bash
# 1. Health check
curl http://localhost:5000/api/health | jq

# 2. Scrape a channel
STORE_NAME=$(curl -s -X POST http://localhost:5000/api/scrape \
  -H "Content-Type: application/json" \
  -d '{"channel_url": "https://youtube.com/@example", "max_videos": 5}' \
  | jq -r '.store_name')

echo "Store created: $STORE_NAME"

# 3. Query it
curl -X POST http://localhost:5000/api/query \
  -H "Content-Type: application/json" \
  -d "{\"store_name\": \"$STORE_NAME\", \"query\": \"What are the key points?\"}" \
  | jq '.response'
```

## What's Next?

1. ✓ Backend API is running
2. ⏳ Build a frontend UI (HTML/JavaScript)
3. ⏳ Create a chat interface
4. ⏳ Add more features

## Documentation

- **API Documentation**: `backend/README.md`
- **API Examples**: `API_EXAMPLES.md`
- **Architecture**: `ARCHITECTURE.md`
- **Full Setup**: `BACKEND_SETUP.md`

## Support

If you encounter issues:
1. Check server logs in terminal
2. Run: `python backend/test_services.py`
3. Verify API keys are correct
4. Check API quota/limits

## Tips

- Start with max_videos=3 for testing (faster)
- Good channels have English captions enabled
- Queries are more accurate with more videos
- Store names are auto-generated (save them!)
- Each channel scrape creates a new store

---

**Ready to build the frontend?** Check `CLAUDE.md` for requirements!
