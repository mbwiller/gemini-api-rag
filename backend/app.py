"""
Flask Backend API for YouTube Channel RAG Tool
Provides REST API endpoints for scraping YouTube channels and querying transcripts using RAG
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any
from pathlib import Path

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from dotenv import load_dotenv

from apify_service import ApifyService
from gemini_service import GeminiService

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__, static_folder='../frontend')
CORS(app)  # Enable CORS for all routes

# Configuration
STORES_FILE = '/home/user/gemini-api-rag/backend/stores.json'
TEMP_TRANSCRIPTS_DIR = '/home/user/gemini-api-rag/temp_transcripts'

# Initialize services
try:
    apify_service = ApifyService()
    gemini_service = GeminiService()
    logger.info("Services initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize services: {str(e)}")
    apify_service = None
    gemini_service = None


# ============================================================================
# Store Management Functions
# ============================================================================

def load_stores() -> Dict[str, Any]:
    """Load stores from JSON file"""
    try:
        if os.path.exists(STORES_FILE):
            with open(STORES_FILE, 'r') as f:
                return json.load(f)
        return {}
    except Exception as e:
        logger.error(f"Error loading stores: {str(e)}")
        return {}


def save_stores(stores: Dict[str, Any]) -> None:
    """Save stores to JSON file"""
    try:
        # Ensure directory exists
        Path(os.path.dirname(STORES_FILE)).mkdir(parents=True, exist_ok=True)

        with open(STORES_FILE, 'w') as f:
            json.dump(stores, f, indent=2)
        logger.info("Stores saved successfully")
    except Exception as e:
        logger.error(f"Error saving stores: {str(e)}")


def generate_store_name(channel_url: str) -> str:
    """Generate a unique store name from channel URL"""
    import re
    from datetime import datetime

    # Extract channel identifier from URL
    channel_id = re.search(r'[@/]([^/]+)/?$', channel_url)
    if channel_id:
        base_name = channel_id.group(1).replace('@', '').replace('/', '')
    else:
        base_name = "channel"

    # Clean the name
    clean_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)

    # Add timestamp for uniqueness
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    return f"{clean_name}_{timestamp}"


# ============================================================================
# Request Validation Functions
# ============================================================================

def validate_scrape_request(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate scrape request data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Request body is empty"

    channel_url = data.get('channel_url')
    if not channel_url:
        return False, "Missing required field: channel_url"

    if not isinstance(channel_url, str) or len(channel_url.strip()) == 0:
        return False, "channel_url must be a non-empty string"

    # Basic URL validation
    if not ('youtube.com' in channel_url or 'youtu.be' in channel_url):
        return False, "Invalid YouTube URL"

    max_videos = data.get('max_videos', 10)
    if not isinstance(max_videos, int):
        try:
            max_videos = int(max_videos)
        except (ValueError, TypeError):
            return False, "max_videos must be an integer"

    if max_videos < 1 or max_videos > 100:
        return False, "max_videos must be between 1 and 100"

    return True, ""


def validate_query_request(data: Dict[str, Any]) -> tuple[bool, str]:
    """
    Validate query request data

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not data:
        return False, "Request body is empty"

    store_name = data.get('store_name')
    if not store_name:
        return False, "Missing required field: store_name"

    if not isinstance(store_name, str) or len(store_name.strip()) == 0:
        return False, "store_name must be a non-empty string"

    query = data.get('query')
    if not query:
        return False, "Missing required field: query"

    if not isinstance(query, str) or len(query.strip()) == 0:
        return False, "query must be a non-empty string"

    if len(query) > 5000:
        return False, "query must be less than 5000 characters"

    return True, ""


# ============================================================================
# API Endpoints
# ============================================================================

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    try:
        # Check if services are initialized
        services_status = {
            'apify': apify_service is not None,
            'gemini': gemini_service is not None
        }

        # Test connections if services are available
        if apify_service:
            services_status['apify_connection'] = apify_service.test_connection()

        if gemini_service:
            services_status['gemini_connection'] = gemini_service.test_connection()

        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'services': services_status
        }), 200

    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e),
            'timestamp': datetime.utcnow().isoformat()
        }), 503


@app.route('/api/scrape', methods=['POST'])
def scrape_channel():
    """
    Scrape YouTube channel and create RAG corpus

    Request body:
        {
            "channel_url": "https://youtube.com/@channelname",
            "max_videos": 10
        }

    Response:
        {
            "status": "success",
            "store_name": "channelname_20231110_120000",
            "video_count": 10,
            "message": "Successfully processed 10 videos"
        }
    """
    try:
        # Validate services
        if not apify_service or not gemini_service:
            return jsonify({
                'status': 'error',
                'message': 'Services not initialized. Check API keys in .env file'
            }), 503

        # Get request data
        data = request.get_json()

        # Validate request
        is_valid, error_message = validate_scrape_request(data)
        if not is_valid:
            return jsonify({
                'status': 'error',
                'message': error_message
            }), 400

        channel_url = data['channel_url'].strip()
        max_videos = int(data.get('max_videos', 10))

        logger.info(f"Starting scrape for channel: {channel_url}, max_videos: {max_videos}")

        # Step 1: Scrape videos using Apify
        try:
            videos = apify_service.scrape_youtube_channel(
                channel_url=channel_url,
                max_videos=max_videos
            )

            if not videos:
                return jsonify({
                    'status': 'error',
                    'message': 'No videos with valid transcripts found'
                }), 404

        except Exception as e:
            logger.error(f"Apify scraping failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to scrape videos: {str(e)}'
            }), 500

        # Step 2: Create transcript files
        try:
            file_paths = gemini_service.create_transcript_files(
                videos=videos,
                output_dir=TEMP_TRANSCRIPTS_DIR
            )

            if not file_paths:
                return jsonify({
                    'status': 'error',
                    'message': 'Failed to create transcript files'
                }), 500

        except Exception as e:
            logger.error(f"File creation failed: {str(e)}")
            return jsonify({
                'status': 'error',
                'message': f'Failed to create files: {str(e)}'
            }), 500

        # Step 3: Upload to Gemini corpus
        try:
            store_name = generate_store_name(channel_url)

            corpus_info = gemini_service.upload_files_to_corpus(
                file_paths=file_paths,
                store_name=store_name,
                display_name=f"YouTube Channel - {channel_url}"
            )

        except Exception as e:
            logger.error(f"Gemini upload failed: {str(e)}")
            # Clean up files
            gemini_service.cleanup_temp_files(file_paths)
            return jsonify({
                'status': 'error',
                'message': f'Failed to upload to Gemini: {str(e)}'
            }), 500

        # Step 4: Save store information
        try:
            stores = load_stores()
            stores[store_name] = {
                'channel_url': channel_url,
                'max_videos': max_videos,
                'video_count': len(videos),
                'created_at': datetime.utcnow().isoformat(),
                'corpus_name': corpus_info['corpus_name'],
                'file_count': corpus_info['file_count']
            }
            save_stores(stores)

        except Exception as e:
            logger.error(f"Failed to save store info: {str(e)}")
            # Continue anyway, just log the error

        # Step 5: Clean up temporary files
        try:
            gemini_service.cleanup_temp_files(file_paths)
        except Exception as e:
            logger.error(f"Failed to clean up temp files: {str(e)}")
            # Continue anyway

        # Success response
        logger.info(f"Successfully processed {len(videos)} videos for store: {store_name}")
        return jsonify({
            'status': 'success',
            'store_name': store_name,
            'video_count': len(videos),
            'message': f'Successfully processed {len(videos)} videos'
        }), 200

    except Exception as e:
        logger.error(f"Unexpected error in scrape endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'status': 'error',
            'message': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/query', methods=['POST'])
def query_rag():
    """
    Query the RAG system

    Request body:
        {
            "store_name": "channelname_20231110_120000",
            "query": "What are the latest features in Claude Code?"
        }

    Response:
        {
            "response": "Based on the transcripts...",
            "citations": [{"source_id": 1, "chunk_id": "...", "relevance_score": 0.95}],
            "query": "What are the latest features in Claude Code?"
        }
    """
    try:
        # Validate service
        if not gemini_service:
            return jsonify({
                'error': 'Gemini service not initialized. Check API key in .env file'
            }), 503

        # Get request data
        data = request.get_json()

        # Validate request
        is_valid, error_message = validate_query_request(data)
        if not is_valid:
            return jsonify({
                'error': error_message
            }), 400

        store_name = data['store_name'].strip()
        query = data['query'].strip()

        logger.info(f"Query received for store '{store_name}': {query[:100]}...")

        # Load stores to get corpus name
        stores = load_stores()
        if store_name not in stores:
            return jsonify({
                'error': f"Store '{store_name}' not found"
            }), 404

        corpus_name = stores[store_name].get('corpus_name')

        # Query the corpus
        try:
            result = gemini_service.query_corpus(
                store_name=store_name,
                query=query,
                corpus_name=corpus_name
            )

            logger.info(f"Query successful for store: {store_name}")
            return jsonify(result), 200

        except Exception as e:
            logger.error(f"Query failed: {str(e)}")
            return jsonify({
                'error': f'Query failed: {str(e)}'
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in query endpoint: {str(e)}", exc_info=True)
        return jsonify({
            'error': f'Internal server error: {str(e)}'
        }), 500


@app.route('/api/stores', methods=['GET'])
def list_stores():
    """
    List all available stores

    Response:
        {
            "stores": {
                "store_name_1": {...},
                "store_name_2": {...}
            },
            "count": 2
        }
    """
    try:
        stores = load_stores()
        return jsonify({
            'stores': stores,
            'count': len(stores)
        }), 200

    except Exception as e:
        logger.error(f"Error listing stores: {str(e)}")
        return jsonify({
            'error': f'Failed to list stores: {str(e)}'
        }), 500


@app.route('/api/store/info/<store_name>', methods=['GET'])
def get_store_info(store_name: str):
    """
    Get information about a specific store

    Response:
        {
            "store_name": "channelname_20231110_120000",
            "channel_url": "https://youtube.com/@channel",
            "video_count": 10,
            "file_count": 10,
            "created_at": "2023-11-10T12:00:00",
            "corpus_name": "corpora/..."
        }
    """
    try:
        stores = load_stores()

        if store_name not in stores:
            return jsonify({
                'error': f"Store '{store_name}' not found"
            }), 404

        store_info = stores[store_name]
        store_info['store_name'] = store_name

        return jsonify(store_info), 200

    except Exception as e:
        logger.error(f"Error getting store info: {str(e)}")
        return jsonify({
            'error': f'Failed to get store info: {str(e)}'
        }), 500


@app.route('/api/store/<store_name>', methods=['DELETE'])
def delete_store(store_name: str):
    """
    Delete a store (removes from local storage only, Gemini corpus remains)

    Response:
        {
            "status": "success",
            "message": "Store deleted successfully"
        }
    """
    try:
        stores = load_stores()

        if store_name not in stores:
            return jsonify({
                'error': f"Store '{store_name}' not found"
            }), 404

        del stores[store_name]
        save_stores(stores)

        logger.info(f"Store deleted: {store_name}")
        return jsonify({
            'status': 'success',
            'message': 'Store deleted successfully'
        }), 200

    except Exception as e:
        logger.error(f"Error deleting store: {str(e)}")
        return jsonify({
            'error': f'Failed to delete store: {str(e)}'
        }), 500


# ============================================================================
# Frontend Routes
# ============================================================================

@app.route('/')
def index():
    """Serve the frontend index.html"""
    return send_from_directory(app.static_folder, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from frontend directory"""
    return send_from_directory(app.static_folder, path)


# ============================================================================
# Error Handlers
# ============================================================================

@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors"""
    return jsonify({
        'error': 'Resource not found',
        'status': 404
    }), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors"""
    logger.error(f"Internal server error: {str(error)}")
    return jsonify({
        'error': 'Internal server error',
        'status': 500
    }), 500


@app.errorhandler(Exception)
def handle_exception(error):
    """Handle all unhandled exceptions"""
    logger.error(f"Unhandled exception: {str(error)}", exc_info=True)
    return jsonify({
        'error': 'An unexpected error occurred',
        'message': str(error),
        'status': 500
    }), 500


# ============================================================================
# Main
# ============================================================================

if __name__ == '__main__':
    # Get configuration from environment
    host = os.getenv('FLASK_HOST', '0.0.0.0')
    port = int(os.getenv('FLASK_PORT', 5000))
    debug = os.getenv('DEBUG', 'False').lower() == 'true'

    logger.info(f"Starting Flask server on {host}:{port}")
    logger.info(f"Debug mode: {debug}")
    logger.info(f"Serving frontend from: {app.static_folder}")

    app.run(host=host, port=port, debug=debug)
