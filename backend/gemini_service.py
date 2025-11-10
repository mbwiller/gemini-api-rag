"""
Gemini File Search Integration Module

This module provides comprehensive integration with Google's Gemini API
for file search and RAG (Retrieval-Augmented Generation) functionality.
Designed specifically for YouTube video transcript search and analysis.

Features:
- File search store creation and management
- Video transcript upload with metadata
- RAG query functionality with citation support
- Store persistence (save/load store IDs)
- Comprehensive error handling and logging
"""

import os
import json
import time
import logging
from pathlib import Path
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

import google.genai as genai
from google.genai import types
from google.genai.errors import APIError
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class GeminiFileSearchService:
    """
    Service class for managing Gemini File Search operations.

    This class handles all interactions with the Gemini API for file search
    functionality, including store creation, file uploads, and RAG queries.
    """

    # Configuration constants
    DEFAULT_MODEL = "gemini-2.0-flash"
    CHUNK_SIZE_TOKENS = 500
    CHUNK_OVERLAP_TOKENS = 50
    MAX_POLL_ATTEMPTS = 60
    POLL_INTERVAL_SECONDS = 2
    STORE_CONFIG_FILE = "store_config.json"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini File Search Service.

        Args:
            api_key: Google API key. If not provided, will use GOOGLE_API_KEY from environment.

        Raises:
            ValueError: If no API key is provided or found in environment.
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "Google API key is required. Set GOOGLE_API_KEY environment variable "
                "or pass api_key parameter."
            )

        # Configure the Gemini client
        genai.configure(api_key=self.api_key)
        self.client = genai.Client(api_key=self.api_key)

        # Initialize store registry
        self.store_registry: Dict[str, str] = {}
        self._load_store_config()

        logger.info("GeminiFileSearchService initialized successfully")

    def _load_store_config(self) -> None:
        """Load store configuration from disk."""
        config_path = Path(self.STORE_CONFIG_FILE)
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    self.store_registry = json.load(f)
                logger.info(f"Loaded {len(self.store_registry)} stores from config")
            except Exception as e:
                logger.error(f"Error loading store config: {e}")
                self.store_registry = {}

    def _save_store_config(self) -> None:
        """Save store configuration to disk."""
        try:
            with open(self.STORE_CONFIG_FILE, 'w') as f:
                json.dump(self.store_registry, f, indent=2)
            logger.info("Store configuration saved")
        except Exception as e:
            logger.error(f"Error saving store config: {e}")

    def _wait_for_operation(
        self,
        operation_name: str,
        timeout: int = 120
    ) -> bool:
        """
        Wait for a long-running operation to complete.

        Args:
            operation_name: Name of the operation to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            True if operation completed successfully, False otherwise
        """
        start_time = time.time()
        attempts = 0

        logger.info(f"Waiting for operation: {operation_name}")

        while attempts < self.MAX_POLL_ATTEMPTS:
            if time.time() - start_time > timeout:
                logger.error(f"Operation timed out: {operation_name}")
                return False

            try:
                # Get operation status
                operation = self.client.files.get_operation(name=operation_name)

                if operation.done:
                    if operation.error:
                        logger.error(f"Operation failed: {operation.error}")
                        return False
                    logger.info(f"Operation completed successfully: {operation_name}")
                    return True

                logger.debug(f"Operation in progress... (attempt {attempts + 1})")
                time.sleep(self.POLL_INTERVAL_SECONDS)
                attempts += 1

            except Exception as e:
                logger.error(f"Error checking operation status: {e}")
                return False

        logger.error(f"Maximum polling attempts reached for: {operation_name}")
        return False

    def create_file_search_store(
        self,
        display_name: str,
        description: Optional[str] = None
    ) -> Optional[types.Corpus]:
        """
        Create a new file search store (corpus) for storing video transcripts.

        Args:
            display_name: Human-readable name for the store
            description: Optional description of the store's purpose

        Returns:
            Corpus object if successful, None otherwise

        Example:
            >>> service = GeminiFileSearchService()
            >>> store = service.create_file_search_store(
            ...     display_name="AI Coding Channel",
            ...     description="Transcripts from AI coding tutorials"
            ... )
        """
        try:
            logger.info(f"Creating file search store: {display_name}")

            # Create the corpus with chunking configuration
            corpus = self.client.corpora.create(
                name=display_name,
                display_name=display_name,
                description=description or f"YouTube transcript store: {display_name}"
            )

            logger.info(f"Successfully created store: {corpus.name} (ID: {corpus.resource_name})")

            # Register the store
            self.store_registry[display_name] = corpus.resource_name
            self._save_store_config()

            return corpus

        except APIError as e:
            logger.error(f"Gemini API error creating store: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error creating store: {e}")
            return None

    def get_store_by_name(self, display_name: str) -> Optional[types.Corpus]:
        """
        Retrieve a store by its display name.

        Args:
            display_name: The display name of the store

        Returns:
            Corpus object if found, None otherwise
        """
        try:
            resource_name = self.store_registry.get(display_name)
            if not resource_name:
                logger.warning(f"Store not found in registry: {display_name}")
                return None

            corpus = self.client.corpora.get(name=resource_name)
            logger.info(f"Retrieved store: {display_name}")
            return corpus

        except APIError as e:
            logger.error(f"Gemini API error retrieving store: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error retrieving store: {e}")
            return None

    def get_store_info(self, display_name: str) -> Optional[Dict[str, Any]]:
        """
        Get detailed information about a store.

        Args:
            display_name: The display name of the store

        Returns:
            Dictionary containing store information, or None if store not found

        Example:
            >>> info = service.get_store_info("AI Coding Channel")
            >>> print(f"Store has {info['document_count']} documents")
        """
        try:
            corpus = self.get_store_by_name(display_name)
            if not corpus:
                return None

            # Get documents in the corpus
            documents = list(self.client.corpora.documents.list(corpus_name=corpus.name))

            info = {
                "name": corpus.name,
                "display_name": corpus.display_name,
                "description": corpus.description,
                "resource_name": corpus.resource_name,
                "document_count": len(documents),
                "created_time": corpus.create_time.isoformat() if hasattr(corpus, 'create_time') else None,
                "updated_time": corpus.update_time.isoformat() if hasattr(corpus, 'update_time') else None,
            }

            logger.info(f"Retrieved info for store: {display_name}")
            return info

        except Exception as e:
            logger.error(f"Error getting store info: {e}")
            return None

    def upload_transcript_to_store(
        self,
        store_name: str,
        video_data: Dict[str, Any],
        transcript_file_path: str
    ) -> Optional[str]:
        """
        Upload a video transcript to a file search store with metadata.

        Args:
            store_name: Display name of the store
            video_data: Dictionary containing video metadata:
                - title: Video title
                - url: Video URL
                - date: Upload/publish date (ISO format or datetime)
                - video_id: Unique video identifier
            transcript_file_path: Path to the transcript text file

        Returns:
            Document name if upload successful, None otherwise

        Example:
            >>> video_data = {
            ...     "title": "Claude Code Tutorial",
            ...     "url": "https://youtube.com/watch?v=...",
            ...     "date": "2025-11-10",
            ...     "video_id": "abc123"
            ... }
            >>> doc_name = service.upload_transcript_to_store(
            ...     "AI Coding Channel",
            ...     video_data,
            ...     "/path/to/transcript.txt"
            ... )
        """
        try:
            # Validate inputs
            if not Path(transcript_file_path).exists():
                logger.error(f"Transcript file not found: {transcript_file_path}")
                return None

            # Get the corpus
            corpus = self.get_store_by_name(store_name)
            if not corpus:
                logger.error(f"Store not found: {store_name}")
                return None

            # Read transcript content
            with open(transcript_file_path, 'r', encoding='utf-8') as f:
                transcript_content = f.read()

            if not transcript_content.strip():
                logger.warning(f"Empty transcript file: {transcript_file_path}")
                return None

            # Prepare metadata
            video_title = video_data.get('title', 'Untitled Video')
            video_url = video_data.get('url', '')
            video_date = video_data.get('date', datetime.now().isoformat())
            video_id = video_data.get('video_id', Path(transcript_file_path).stem)

            # Convert date to string if it's a datetime object
            if isinstance(video_date, datetime):
                video_date = video_date.isoformat()

            logger.info(f"Uploading transcript for: {video_title}")

            # Create document with chunking configuration
            document = self.client.corpora.documents.create(
                corpus_name=corpus.name,
                display_name=video_title,
                metadata={
                    "video_title": video_title,
                    "video_url": video_url,
                    "upload_date": video_date,
                    "video_id": video_id,
                    "source": "youtube"
                }
            )

            # Create a chunk with the transcript content
            chunk = self.client.corpora.documents.chunks.create(
                document_name=document.name,
                data={
                    "string_value": transcript_content
                },
                metadata={
                    "video_title": video_title,
                    "video_url": video_url
                }
            )

            logger.info(f"Successfully uploaded transcript: {video_title} (Document: {document.name})")
            return document.name

        except APIError as e:
            logger.error(f"Gemini API error uploading transcript: {e}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error uploading transcript: {e}")
            return None

    def query_transcripts(
        self,
        store_name: str,
        query: str,
        max_results: int = 5,
        temperature: float = 0.7
    ) -> Optional[Dict[str, Any]]:
        """
        Query video transcripts using RAG with citation support.

        Args:
            store_name: Display name of the store to query
            query: The user's question or search query
            max_results: Maximum number of relevant chunks to retrieve
            temperature: Model temperature (0.0-1.0)

        Returns:
            Dictionary containing:
                - answer: The generated response
                - citations: List of sources with titles, URLs, and excerpts
                - grounding_metadata: Additional grounding information

        Example:
            >>> result = service.query_transcripts(
            ...     "AI Coding Channel",
            ...     "How do I use Claude Code for API integration?"
            ... )
            >>> print(result['answer'])
            >>> for citation in result['citations']:
            ...     print(f"Source: {citation['title']} - {citation['url']}")
        """
        try:
            # Get the corpus
            corpus = self.get_store_by_name(store_name)
            if not corpus:
                logger.error(f"Store not found: {store_name}")
                return None

            logger.info(f"Querying store '{store_name}' with: {query[:100]}...")

            # Configure the model with grounding
            model = genai.GenerativeModel(
                model_name=self.DEFAULT_MODEL,
                config={
                    "temperature": temperature,
                }
            )

            # Create grounding configuration
            grounding_config = types.GroundingConfig(
                sources=[
                    types.GroundingSource(
                        retriever=types.Retriever(
                            corpus=corpus.name
                        )
                    )
                ]
            )

            # Generate response with grounding
            response = model.generate_content(
                contents=query,
                config=types.GenerateContentConfig(
                    grounding_config=grounding_config,
                    response_modalities=["TEXT"],
                )
            )

            # Extract answer
            answer = response.text if hasattr(response, 'text') else ""

            # Extract grounding metadata and citations
            citations = []
            grounding_metadata = {}

            if hasattr(response, 'grounding_metadata') and response.grounding_metadata:
                grounding_metadata = {
                    "search_entry_point": getattr(response.grounding_metadata, 'search_entry_point', None),
                    "retrieval_queries": getattr(response.grounding_metadata, 'retrieval_queries', [])
                }

                # Extract grounding chunks (citations)
                if hasattr(response.grounding_metadata, 'grounding_chunks'):
                    for chunk in response.grounding_metadata.grounding_chunks:
                        citation = {
                            "title": "Unknown",
                            "url": "",
                            "excerpt": ""
                        }

                        # Try to extract metadata from the chunk
                        if hasattr(chunk, 'web') and chunk.web:
                            citation["title"] = getattr(chunk.web, 'title', 'Unknown')
                            citation["url"] = getattr(chunk.web, 'uri', '')

                        # Try to extract content
                        if hasattr(chunk, 'retrieved_content') and chunk.retrieved_content:
                            citation["excerpt"] = str(chunk.retrieved_content)[:300] + "..."

                        citations.append(citation)

            result = {
                "answer": answer,
                "citations": citations,
                "grounding_metadata": grounding_metadata,
                "query": query,
                "timestamp": datetime.now().isoformat()
            }

            logger.info(f"Query completed successfully with {len(citations)} citations")
            return result

        except APIError as e:
            logger.error(f"Gemini API error during query: {e}")
            return {
                "answer": f"Error: API error occurred - {str(e)}",
                "citations": [],
                "grounding_metadata": {},
                "error": str(e)
            }
        except Exception as e:
            logger.error(f"Unexpected error during query: {e}")
            return {
                "answer": f"Error: {str(e)}",
                "citations": [],
                "grounding_metadata": {},
                "error": str(e)
            }

    def delete_store(self, display_name: str) -> bool:
        """
        Delete a file search store and all its contents.

        Args:
            display_name: Display name of the store to delete

        Returns:
            True if deletion was successful, False otherwise

        Warning:
            This operation is irreversible and will delete all documents in the store.

        Example:
            >>> success = service.delete_store("AI Coding Channel")
            >>> if success:
            ...     print("Store deleted successfully")
        """
        try:
            corpus = self.get_store_by_name(display_name)
            if not corpus:
                logger.warning(f"Store not found: {display_name}")
                return False

            logger.warning(f"Deleting store: {display_name}")

            # Delete the corpus
            self.client.corpora.delete(name=corpus.name)

            # Remove from registry
            if display_name in self.store_registry:
                del self.store_registry[display_name]
                self._save_store_config()

            logger.info(f"Successfully deleted store: {display_name}")
            return True

        except APIError as e:
            logger.error(f"Gemini API error deleting store: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting store: {e}")
            return False

    def list_stores(self) -> List[Dict[str, str]]:
        """
        List all registered stores.

        Returns:
            List of dictionaries containing store display names and resource names

        Example:
            >>> stores = service.list_stores()
            >>> for store in stores:
            ...     print(f"{store['display_name']}: {store['resource_name']}")
        """
        return [
            {
                "display_name": name,
                "resource_name": resource_name
            }
            for name, resource_name in self.store_registry.items()
        ]

    def list_documents_in_store(self, store_name: str) -> Optional[List[Dict[str, Any]]]:
        """
        List all documents in a store.

        Args:
            store_name: Display name of the store

        Returns:
            List of document information dictionaries, or None if store not found

        Example:
            >>> docs = service.list_documents_in_store("AI Coding Channel")
            >>> for doc in docs:
            ...     print(f"{doc['display_name']} - Created: {doc['created_time']}")
        """
        try:
            corpus = self.get_store_by_name(store_name)
            if not corpus:
                return None

            documents = list(self.client.corpora.documents.list(corpus_name=corpus.name))

            doc_list = []
            for doc in documents:
                doc_info = {
                    "name": doc.name,
                    "display_name": doc.display_name,
                    "metadata": doc.metadata if hasattr(doc, 'metadata') else {},
                    "created_time": doc.create_time.isoformat() if hasattr(doc, 'create_time') else None,
                }
                doc_list.append(doc_info)

            logger.info(f"Listed {len(doc_list)} documents in store: {store_name}")
            return doc_list

        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return None

    def delete_document_from_store(
        self,
        store_name: str,
        document_name: str
    ) -> bool:
        """
        Delete a specific document from a store.

        Args:
            store_name: Display name of the store
            document_name: Name/ID of the document to delete

        Returns:
            True if deletion was successful, False otherwise
        """
        try:
            corpus = self.get_store_by_name(store_name)
            if not corpus:
                logger.error(f"Store not found: {store_name}")
                return False

            # Delete the document
            self.client.corpora.documents.delete(name=document_name)

            logger.info(f"Successfully deleted document: {document_name}")
            return True

        except APIError as e:
            logger.error(f"Gemini API error deleting document: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error deleting document: {e}")
            return False

    def get_service_stats(self) -> Dict[str, Any]:
        """
        Get overall service statistics.

        Returns:
            Dictionary containing service-wide statistics

        Example:
            >>> stats = service.get_service_stats()
            >>> print(f"Total stores: {stats['total_stores']}")
            >>> print(f"Total documents: {stats['total_documents']}")
        """
        try:
            total_stores = len(self.store_registry)
            total_documents = 0

            for store_name in self.store_registry.keys():
                docs = self.list_documents_in_store(store_name)
                if docs:
                    total_documents += len(docs)

            stats = {
                "total_stores": total_stores,
                "total_documents": total_documents,
                "registered_stores": list(self.store_registry.keys()),
                "timestamp": datetime.now().isoformat()
            }

            logger.info("Retrieved service statistics")
            return stats

        except Exception as e:
            logger.error(f"Error getting service stats: {e}")
            return {
                "total_stores": 0,
                "total_documents": 0,
                "error": str(e)
            }


# Backwards compatibility: Keep old class name as alias
GeminiService = GeminiFileSearchService


# Convenience functions for module-level usage
_service_instance = None


def get_service(api_key: Optional[str] = None) -> GeminiFileSearchService:
    """
    Get or create a singleton service instance.

    Args:
        api_key: Optional API key. If not provided, uses environment variable.

    Returns:
        GeminiFileSearchService instance
    """
    global _service_instance
    if _service_instance is None:
        _service_instance = GeminiFileSearchService(api_key=api_key)
    return _service_instance


def reset_service() -> None:
    """Reset the singleton service instance."""
    global _service_instance
    _service_instance = None


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage of the GeminiFileSearchService.

    This demonstrates the typical workflow:
    1. Initialize service
    2. Create a store
    3. Upload transcripts
    4. Query the store
    5. View results
    """

    # Initialize service
    service = GeminiFileSearchService()

    # Create a store
    store = service.create_file_search_store(
        display_name="AI Development Channel",
        description="Transcripts from AI coding and development videos"
    )

    if store:
        print(f"Created store: {store.display_name}")

        # Example: Upload a transcript
        # video_data = {
        #     "title": "Introduction to Claude Code",
        #     "url": "https://youtube.com/watch?v=example",
        #     "date": "2025-11-10",
        #     "video_id": "example123"
        # }
        # service.upload_transcript_to_store(
        #     "AI Development Channel",
        #     video_data,
        #     "/path/to/transcript.txt"
        # )

        # Example: Query the store
        # result = service.query_transcripts(
        #     "AI Development Channel",
        #     "What are the best practices for using Claude Code?"
        # )
        # if result:
        #     print(f"Answer: {result['answer']}")
        #     print(f"Citations: {len(result['citations'])}")

        # Get store info
        info = service.get_store_info("AI Development Channel")
        if info:
            print(f"Store has {info['document_count']} documents")

        # Get service stats
        stats = service.get_service_stats()
        print(f"Service stats: {stats}")
