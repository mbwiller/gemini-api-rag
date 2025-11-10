I want you to build a RAG tool for any YouTube channel... ask me the Channel URL and how many videos to store from the newest to older. You'll then use Apify to grab the video title and subtitles, create a file for each video that you'll add to Gemini API File Search. When that's done you'll give me a chat box to chat with the video transcripts from that channel. The channels are going to be focused on AI Development, namely videos that analyze Claude Code and other agentic coding LLMs and are focused on teaching/showing all of the most cutting edge updates/usages/tricks/improvements, such that I can just scrape the YouTube video and get the key points.

You'll need to store .env variables for Gemini API and Apify API.

Apify actor to use: https://apify.com/streamers/youtube-scraper.md

Doc links below:
https://ai.google.dev/gemini-api/docs/file-search
https://docs.apify.com/llms.txt
