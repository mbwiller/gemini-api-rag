#!/usr/bin/env python3
"""
Gemini File Search Service - Comprehensive Usage Examples

This script demonstrates all the key features of the GeminiFileSearchService
for YouTube video transcript RAG functionality.

Prerequisites:
1. Set GOOGLE_API_KEY environment variable
2. Install required packages: pip install -r requirements.txt
3. Have video transcript files ready to upload

Author: Claude Code
Date: 2025-11-10
"""

import os
import sys
from pathlib import Path
from datetime import datetime

# Add parent directory to path to import backend module
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.gemini_service import GeminiFileSearchService


def example_1_initialize_service():
    """Example 1: Initialize the Gemini File Search Service"""
    print("\n" + "="*70)
    print("EXAMPLE 1: Initialize Service")
    print("="*70)

    try:
        # Initialize with environment variable
        service = GeminiFileSearchService()
        print(" Service initialized successfully")
        return service
    except ValueError as e:
        print(f" Error: {e}")
        print("\nMake sure GOOGLE_API_KEY is set in your environment or .env file")
        return None


def example_2_create_store(service):
    """Example 2: Create a new file search store"""
    print("\n" + "="*70)
    print("EXAMPLE 2: Create File Search Store")
    print("="*70)

    store_name = f"AI_Coding_Channel_{datetime.now().strftime('%Y%m%d_%H%M%S')}"

    store = service.create_file_search_store(
        display_name=store_name,
        description="YouTube transcripts about AI development, Claude Code, and agentic coding"
    )

    if store:
        print(f" Created store: {store.display_name}")
        print(f"  Resource name: {store.resource_name}")
        return store_name
    else:
        print(" Failed to create store")
        return None


def example_3_upload_transcript(service, store_name):
    """Example 3: Upload a video transcript to the store"""
    print("\n" + "="*70)
    print("EXAMPLE 3: Upload Video Transcript")
    print("="*70)

    # Create a sample transcript file for demonstration
    transcript_dir = Path("temp_transcripts")
    transcript_dir.mkdir(exist_ok=True)

    sample_transcript = transcript_dir / "sample_video.txt"

    # Sample content
    video_content = """
# Claude Code Tutorial - Advanced API Integration

Welcome to this tutorial on Claude Code. In this video, we'll explore how to build
advanced API integrations using Claude's powerful code generation capabilities.

## Key Points Covered:

1. Setting up your development environment
2. Configuring API keys and environment variables
3. Using the google-genai SDK for RAG implementations
4. Best practices for file search and document retrieval
5. Implementing citation support in your responses

## Detailed Walkthrough:

First, let's talk about the importance of proper error handling when working with
LLM APIs. You should always wrap your API calls in try-except blocks and handle
both APIError exceptions and general exceptions separately.

The Gemini File Search API provides powerful capabilities for building RAG applications.
You can create a corpus to store your documents, upload files with metadata, and then
query them using natural language. The system automatically chunks your documents and
creates embeddings for semantic search.

When implementing chunking, consider using 500 tokens per chunk with 50 token overlap.
This ensures good context preservation while maintaining efficient retrieval.

For production systems, implement store persistence by saving corpus IDs to a JSON file.
This allows your application to reconnect to existing stores across sessions.

Remember to poll for operation completion when uploading files. Use exponential backoff
and set reasonable timeouts to avoid hanging operations.

## Summary:

Building effective RAG systems with Claude Code requires careful attention to:
- Proper API configuration and error handling
- Optimal chunking strategies
- Metadata management for better retrieval
- Citation support for transparency
- Production-ready persistence and logging

Thank you for watching! Don't forget to check out the documentation links in the
description below.
    """.strip()

    # Write sample transcript
    with open(sample_transcript, 'w') as f:
        f.write(video_content)

    # Prepare video metadata
    video_data = {
        "title": "Claude Code Tutorial - Advanced API Integration",
        "url": "https://youtube.com/watch?v=example_abc123",
        "date": datetime.now().isoformat(),
        "video_id": "example_abc123",
        "duration": "15:30",
        "view_count": "10,523"
    }

    # Upload to store
    doc_name = service.upload_transcript_to_store(
        store_name=store_name,
        video_data=video_data,
        transcript_file_path=str(sample_transcript)
    )

    if doc_name:
        print(f" Successfully uploaded transcript")
        print(f"  Video: {video_data['title']}")
        print(f"  Document ID: {doc_name}")
        return doc_name
    else:
        print(" Failed to upload transcript")
        return None


def example_4_query_store(service, store_name):
    """Example 4: Query the store using RAG"""
    print("\n" + "="*70)
    print("EXAMPLE 4: Query Transcripts with RAG")
    print("="*70)

    queries = [
        "What are the key points about API integration?",
        "What chunking strategy is recommended?",
        "How should I handle errors when working with LLM APIs?",
    ]

    for i, query in enumerate(queries, 1):
        print(f"\nQuery {i}: {query}")
        print("-" * 70)

        result = service.query_transcripts(
            store_name=store_name,
            query=query,
            max_results=3,
            temperature=0.7
        )

        if result and not result.get('error'):
            print(f"\nAnswer:\n{result['answer']}\n")

            if result.get('citations'):
                print(f"Citations ({len(result['citations'])}):")
                for j, citation in enumerate(result['citations'], 1):
                    print(f"  [{j}] {citation.get('title', 'Unknown')}")
                    if citation.get('url'):
                        print(f"      URL: {citation['url']}")
                    if citation.get('excerpt'):
                        print(f"      Excerpt: {citation['excerpt'][:100]}...")
        else:
            error_msg = result.get('error', 'Unknown error') if result else 'No result returned'
            print(f" Query failed: {error_msg}")


def example_5_list_stores(service):
    """Example 5: List all stores"""
    print("\n" + "="*70)
    print("EXAMPLE 5: List All Stores")
    print("="*70)

    stores = service.list_stores()

    if stores:
        print(f" Found {len(stores)} store(s):")
        for i, store in enumerate(stores, 1):
            print(f"  {i}. {store['display_name']}")
            print(f"     Resource: {store['resource_name']}")
    else:
        print("No stores found")


def example_6_get_store_info(service, store_name):
    """Example 6: Get detailed store information"""
    print("\n" + "="*70)
    print("EXAMPLE 6: Get Store Information")
    print("="*70)

    info = service.get_store_info(store_name)

    if info:
        print(f" Store Information:")
        print(f"  Name: {info['display_name']}")
        print(f"  Description: {info.get('description', 'N/A')}")
        print(f"  Document Count: {info['document_count']}")
        print(f"  Created: {info.get('created_time', 'N/A')}")
        print(f"  Updated: {info.get('updated_time', 'N/A')}")
        return info
    else:
        print(f" Could not retrieve store info")
        return None


def example_7_list_documents(service, store_name):
    """Example 7: List all documents in a store"""
    print("\n" + "="*70)
    print("EXAMPLE 7: List Documents in Store")
    print("="*70)

    docs = service.list_documents_in_store(store_name)

    if docs:
        print(f" Found {len(docs)} document(s):")
        for i, doc in enumerate(docs, 1):
            print(f"\n  {i}. {doc['display_name']}")
            print(f"     Document ID: {doc['name']}")
            print(f"     Created: {doc.get('created_time', 'N/A')}")

            if doc.get('metadata'):
                print(f"     Metadata:")
                for key, value in doc['metadata'].items():
                    print(f"       - {key}: {value}")
    else:
        print("No documents found")


def example_8_service_stats(service):
    """Example 8: Get service-wide statistics"""
    print("\n" + "="*70)
    print("EXAMPLE 8: Service Statistics")
    print("="*70)

    stats = service.get_service_stats()

    print(f" Service Statistics:")
    print(f"  Total Stores: {stats['total_stores']}")
    print(f"  Total Documents: {stats['total_documents']}")
    print(f"  Registered Stores:")
    for store in stats.get('registered_stores', []):
        print(f"    - {store}")
    print(f"  Timestamp: {stats['timestamp']}")


def example_9_batch_upload(service, store_name):
    """Example 9: Batch upload multiple transcripts"""
    print("\n" + "="*70)
    print("EXAMPLE 9: Batch Upload Multiple Transcripts")
    print("="*70)

    # Create multiple sample transcripts
    transcript_dir = Path("temp_transcripts")
    video_data_list = [
        {
            "title": "Claude Code Best Practices",
            "url": "https://youtube.com/watch?v=example_def456",
            "video_id": "example_def456",
            "content": "This video covers best practices for using Claude Code including proper prompting, file management, and error handling."
        },
        {
            "title": "Building RAG Systems with Gemini",
            "url": "https://youtube.com/watch?v=example_ghi789",
            "video_id": "example_ghi789",
            "content": "Learn how to build production-ready RAG systems using the Gemini API. We cover corpus creation, document chunking, and query optimization."
        }
    ]

    uploaded_count = 0

    for video_data in video_data_list:
        # Create transcript file
        transcript_file = transcript_dir / f"{video_data['video_id']}.txt"
        with open(transcript_file, 'w') as f:
            f.write(video_data['content'])

        # Upload
        doc_name = service.upload_transcript_to_store(
            store_name=store_name,
            video_data={
                "title": video_data['title'],
                "url": video_data['url'],
                "date": datetime.now().isoformat(),
                "video_id": video_data['video_id']
            },
            transcript_file_path=str(transcript_file)
        )

        if doc_name:
            uploaded_count += 1
            print(f" Uploaded: {video_data['title']}")

    print(f"\n Batch upload complete: {uploaded_count}/{len(video_data_list)} successful")


def example_10_cleanup(service, store_name):
    """Example 10: Clean up - Delete store (optional)"""
    print("\n" + "="*70)
    print("EXAMPLE 10: Cleanup (Optional)")
    print("="*70)

    response = input(f"\nDo you want to delete the store '{store_name}'? (yes/no): ")

    if response.lower() == 'yes':
        success = service.delete_store(store_name)
        if success:
            print(f" Store '{store_name}' deleted successfully")
        else:
            print(f" Failed to delete store '{store_name}'")
    else:
        print("Store preserved. You can delete it later using delete_store()")


def run_all_examples():
    """Run all examples in sequence"""
    print("\n" + "="*70)
    print("GEMINI FILE SEARCH SERVICE - COMPREHENSIVE EXAMPLES")
    print("="*70)
    print("\nThis script demonstrates all key features of the GeminiFileSearchService")
    print("for building RAG applications with YouTube video transcripts.")
    print("\nPress Ctrl+C at any time to exit.\n")

    try:
        # Example 1: Initialize
        service = example_1_initialize_service()
        if not service:
            print("\n Cannot continue without valid API key")
            return

        # Example 2: Create store
        store_name = example_2_create_store(service)
        if not store_name:
            print("\n Cannot continue without a store")
            return

        # Example 3: Upload transcript
        doc_name = example_3_upload_transcript(service, store_name)

        # Example 9: Batch upload
        example_9_batch_upload(service, store_name)

        # Example 5: List stores
        example_5_list_stores(service)

        # Example 6: Get store info
        example_6_get_store_info(service, store_name)

        # Example 7: List documents
        example_7_list_documents(service, store_name)

        # Example 8: Service stats
        example_8_service_stats(service)

        # Example 4: Query store (needs time for indexing)
        print("\n[*] Waiting 5 seconds for indexing to complete...")
        import time
        time.sleep(5)
        example_4_query_store(service, store_name)

        # Example 10: Cleanup
        example_10_cleanup(service, store_name)

        print("\n" + "="*70)
        print("ALL EXAMPLES COMPLETED SUCCESSFULLY!")
        print("="*70)

    except KeyboardInterrupt:
        print("\n\n� Interrupted by user")
    except Exception as e:
        print(f"\n Unexpected error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_examples()
