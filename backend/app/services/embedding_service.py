import json
import time
from typing import Dict, List
from pathlib import Path
from openai import OpenAI, RateLimitError
from app.config import settings


class EmbeddingService:
    """Service for generating and caching OpenAI embeddings."""

    def __init__(self, cache_file: str):
        self.cache_file = Path(cache_file)
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.embedding_model
        self._cache: Dict[str, List[float]] = {}

    def generate_embedding(self, text: str, retry_count: int = 3) -> List[float]:
        """
        Generate an embedding for a single text using OpenAI API with retry logic.

        Args:
            text: The text to generate an embedding for
            retry_count: Number of retries on rate limit errors

        Returns:
            List of floats representing the embedding vector
        """
        for attempt in range(retry_count):
            try:
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text
                )
                return response.data[0].embedding
            except RateLimitError as e:
                if attempt < retry_count - 1:
                    # Exponential backoff: wait longer each time
                    wait_time = (attempt + 1) * 2
                    print(f"Rate limit hit, waiting {wait_time}s before retry {attempt + 1}/{retry_count}")
                    time.sleep(wait_time)
                else:
                    raise e

        raise Exception("Failed to generate embedding after retries")

    def generate_tender_embeddings(self, tenders: list) -> Dict[str, List[float]]:
        """
        Generate embeddings for all tenders and cache them with rate limiting.

        Args:
            tenders: List of Tender objects

        Returns:
            Dictionary mapping tender_id to embedding vector
        """
        embeddings = {}
        total = len(tenders)

        print(f"\n=== Generating embeddings for {total} tenders ===")
        print(f"This will take approximately {(total * 0.7) / 60:.1f} minutes due to rate limits")
        print("Progress will be saved every 50 tenders.\n")

        start_time = time.time()

        for idx, tender in enumerate(tenders):
            # Create text representation of the tender
            tender_text = f"Title: {tender.metadata.name}\nOrganization: {tender.metadata.organization}"

            # Generate embedding
            embedding = self.generate_embedding(tender_text)
            embeddings[tender.id] = embedding

            # Rate limiting: Wait 700ms between requests to stay under 100 RPM
            # 100 requests/min = 1.67 requests/sec = 600ms per request
            # We use 700ms to be safe
            if idx < total - 1:  # Don't wait after the last one
                time.sleep(0.7)

            # Progress indicator and periodic saves
            if (idx + 1) % 50 == 0:
                elapsed = time.time() - start_time
                rate = (idx + 1) / elapsed
                eta = (total - idx - 1) / rate if rate > 0 else 0

                print(f"Progress: {idx + 1}/{total} ({(idx + 1) / total * 100:.1f}%) | "
                      f"ETA: {eta / 60:.1f} min")

                # Save progress every 50 tenders
                self.save_cached_embeddings(embeddings)
                print(f"  → Progress saved to cache")

            elif (idx + 1) == total:
                print(f"Progress: {idx + 1}/{total} (100%) - Complete!")

        # Final save
        self.save_cached_embeddings(embeddings)

        elapsed = time.time() - start_time
        print(f"\n✓ All embeddings generated in {elapsed / 60:.1f} minutes")
        print(f"✓ Cached to {self.cache_file}")

        return embeddings

    def load_cached_embeddings(self) -> Dict[str, List[float]]:
        """
        Load embeddings from cache file.

        Returns:
            Dictionary mapping tender_id to embedding vector
        """
        if self._cache:
            return self._cache

        if not self.cache_file.exists():
            return {}

        with open(self.cache_file, 'r', encoding='utf-8') as f:
            self._cache = json.load(f)

        print(f"Loaded {len(self._cache)} embeddings from cache")
        return self._cache

    def save_cached_embeddings(self, embeddings: Dict[str, List[float]]):
        """
        Save embeddings to cache file.

        Args:
            embeddings: Dictionary mapping tender_id to embedding vector
        """
        # Ensure directory exists
        self.cache_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.cache_file, 'w', encoding='utf-8') as f:
            json.dump(embeddings, f)

        self._cache = embeddings

    def get_or_generate_tender_embeddings(self, tenders: list) -> Dict[str, List[float]]:
        """
        Get embeddings from cache or generate if not cached.

        Args:
            tenders: List of Tender objects

        Returns:
            Dictionary mapping tender_id to embedding vector
        """
        cached_embeddings = self.load_cached_embeddings()

        # Check if all tenders have cached embeddings
        tender_ids = {tender.id for tender in tenders}
        cached_ids = set(cached_embeddings.keys())

        if tender_ids == cached_ids:
            print("Using cached embeddings for all tenders")
            return cached_embeddings

        # Some embeddings missing, regenerate all
        print("Cache incomplete or outdated, generating new embeddings...")
        return self.generate_tender_embeddings(tenders)
