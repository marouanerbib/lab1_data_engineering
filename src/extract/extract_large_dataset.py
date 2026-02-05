"""
Enhanced data extraction pipeline for AI note-taking apps on Google Play Store.

This script searches for multiple app variations to collect 100-200 apps:
- "note-taking AI apps"
- "AI note taker"
- "voice note transcription"
- "AI writing assistant"
- "meeting notes AI"
- "study notes AI"
- "smart note app"
- And more...

Extracts metadata and reviews (1000+ per app with pagination)
"""

import json
import time
from pathlib import Path
from typing import List, Dict, Set, Any
import logging

from google_play_scraper import search, app, reviews, Sort

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class EnhancedPlayStoreExtractor:
    """Extract large-scale app data from Google Play Store."""
    
    def __init__(self, output_dir: str = '.'):
        """Initialize the extractor."""
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        self.metadata_file = self.output_dir / 'apps_metadata_raw.json'
        self.reviews_file = self.output_dir / 'user_reviews_raw.jsonl'
        
        # Keep track of apps already extracted to avoid duplicates
        self.extracted_app_ids: Set[str] = set()
        
        # Load existing apps if files exist
        self._load_existing_data()
        
        logger.info(f"Output directory: {self.output_dir}")
        logger.info(f"Already extracted: {len(self.extracted_app_ids)} apps")
    
    def _load_existing_data(self) -> None:
        """Load already extracted app IDs to avoid duplicates."""
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    apps = json.load(f)
                    self.extracted_app_ids = set(app['appId'] for app in apps)
                    logger.info(f"Loaded {len(self.extracted_app_ids)} existing apps")
            except Exception as e:
                logger.warning(f"Could not load existing metadata: {e}")
    
    def search_multiple_queries(self, queries: List[str], target_apps: int = 200) -> List[str]:
        """
        Search for apps using multiple queries to get diverse results.
        
        Args:
            queries: List of search queries
            target_apps: Target number of unique apps to find
            
        Returns:
            List of unique app IDs
        """
        logger.info(f"Searching for {target_apps} apps using {len(queries)} queries...")
        
        all_app_ids = set(self.extracted_app_ids)  # Start with existing
        
        for query in queries:
            if len(all_app_ids) >= target_apps:
                break
            
            try:
                logger.info(f"Query: '{query}' (current: {len(all_app_ids)} apps)")
                
                results = search(
                    query,
                    lang='en',
                    country='us',
                    n_hits=30  # Max 30 per search
                )
                
                new_apps = 0
                for result in results:
                    app_id = result['appId']
                    if app_id not in all_app_ids:
                        all_app_ids.add(app_id)
                        new_apps += 1
                
                logger.info(f"  → Found {new_apps} new apps")
                time.sleep(1)  # Rate limiting between searches
            
            except Exception as e:
                logger.error(f"  → Search failed: {e}")
                continue
        
        # Remove already extracted apps from new list
        new_app_ids = sorted(list(all_app_ids - self.extracted_app_ids))
        logger.info(f"\nTotal unique apps found: {len(all_app_ids)}")
        logger.info(f"New apps to extract: {len(new_app_ids)}")
        
        return new_app_ids
    
    def extract_metadata(self, app_ids: List[str], delay: float = 1.5) -> List[Dict[str, Any]]:
        """Extract metadata for new apps."""
        logger.info(f"\nExtracting metadata for {len(app_ids)} new apps...")
        
        new_metadata = []
        failed_apps = []
        
        for i, app_id in enumerate(app_ids, 1):
            try:
                print(f"[{i}/{len(app_ids)}] {app_id} ", end="", flush=True)
                
                app_data = app(app_id, lang='en', country='us')
                new_metadata.append(app_data)
                
                print(f"✓ {app_data['title'][:40]}")
                
                if i < len(app_ids):
                    time.sleep(delay)
            
            except Exception as e:
                print(f"✗ {str(e)[:40]}")
                failed_apps.append(app_id)
                continue
        
        logger.info(f"\nSuccessfully extracted: {len(new_metadata)}")
        logger.info(f"Failed: {len(failed_apps)}")
        
        return new_metadata
    
    def merge_and_save_metadata(self, new_metadata: List[Dict[str, Any]]) -> None:
        """Merge new metadata with existing and save."""
        all_metadata = []
        
        # Load existing metadata
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r') as f:
                    all_metadata = json.load(f)
            except Exception as e:
                logger.warning(f"Could not load existing metadata: {e}")
        
        # Add new metadata
        all_metadata.extend(new_metadata)
        
        # Remove duplicates (keep first occurrence)
        seen_ids = set()
        unique_metadata = []
        for app_data in all_metadata:
            app_id = app_data['appId']
            if app_id not in seen_ids:
                unique_metadata.append(app_data)
                seen_ids.add(app_id)
        
        logger.info(f"Total unique apps: {len(unique_metadata)}")
        
        # Save
        try:
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(unique_metadata, f, indent=2, default=str)
            
            logger.info(f"✓ Saved {len(unique_metadata)} apps to {self.metadata_file}")
            logger.info(f"  File size: {self.metadata_file.stat().st_size / 1024 / 1024:.2f} MB")
        
        except Exception as e:
            logger.error(f"Failed to save metadata: {e}")
    
    def extract_reviews(self, app_ids: List[str], reviews_per_app: int = 500, delay: float = 0.8) -> int:
        """Extract reviews for apps."""
        logger.info(f"\nExtracting reviews for {len(app_ids)} apps...")
        
        total_reviews = 0
        
        with open(self.reviews_file, 'a', encoding='utf-8') as f:
            for app_idx, app_id in enumerate(app_ids, 1):
                logger.info(f"\n[{app_idx}/{len(app_ids)}] {app_id}")
                
                app_reviews_count = 0
                continuation_token = None
                
                try:
                    while app_reviews_count < reviews_per_app:
                        try:
                            print(f"  Batch (current: {app_reviews_count}) ", end="", flush=True)
                            
                            result, continuation_token = reviews(
                                app_id,
                                lang='en',
                                country='us',
                                sort=Sort.NEWEST,
                                count=200,
                                continuation_token=continuation_token
                            )
                            
                            if not result:
                                print("(no more)")
                                break
                            
                            for review in result:
                                review['appId'] = app_id
                                f.write(json.dumps(review, default=str) + '\n')
                                app_reviews_count += 1
                                total_reviews += 1
                            
                            print(f"→ {len(result)} reviews")
                            
                            if app_reviews_count >= reviews_per_app or not continuation_token:
                                break
                            
                            time.sleep(delay)
                        
                        except Exception as e:
                            logger.error(f"  Batch error: {e}")
                            break
                
                except Exception as e:
                    logger.error(f"  App error: {e}")
                    continue
                
                logger.info(f"  Total: {app_reviews_count} reviews")
                
                if app_idx < len(app_ids):
                    time.sleep(delay)
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Total reviews added: {total_reviews}")
        
        return total_reviews
    
    def print_summary(self) -> None:
        """Print final summary."""
        if not self.metadata_file.exists():
            return
        
        with open(self.metadata_file, 'r') as f:
            apps = json.load(f)
        
        total_lines = sum(1 for _ in open(self.reviews_file)) if self.reviews_file.exists() else 0
        
        logger.info("\n" + "="*70)
        logger.info("FINAL DATA SUMMARY")
        logger.info("="*70)
        logger.info(f"\nApps extracted: {len(apps)}")
        logger.info(f"Reviews extracted: {total_lines:,}")
        
        if total_lines > 0:
            avg_reviews_per_app = total_lines / len(apps)
            logger.info(f"Average reviews per app: {avg_reviews_per_app:.0f}")
        
        logger.info(f"\nFiles:")
        logger.info(f"  • {self.metadata_file} ({self.metadata_file.stat().st_size / 1024 / 1024:.2f} MB)")
        logger.info(f"  • {self.reviews_file} ({self.reviews_file.stat().st_size / 1024 / 1024:.2f} MB)")
        logger.info("="*70 + "\n")


def main():
    """Main extraction pipeline."""
    
    logger.info("="*70)
    logger.info("LARGE-SCALE DATA EXTRACTION - AI NOTE-TAKING APPS")
    logger.info("Target: 100-200 apps, 500+ reviews per app")
    logger.info("="*70)
    
    # Initialize extractor
    extractor = EnhancedPlayStoreExtractor(output_dir='.')
    
    # Multiple search queries to find diverse apps
    search_queries = [
        "note-taking AI apps",
        "AI note taker",
        "voice note transcription",
        "AI writing assistant",
        "meeting notes AI",
        "study notes AI",
        "smart note app",
        "AI transcriber app",
        "note app with AI",
        "intelligent notes",
        "AI summary app",
        "note taking assistant",
        "digital notes app",
        "voice to text notes",
        "AI powered notes",
        "smart notebook",
        "note organizer",
        "documentation app",
        "meeting recorder",
        "lecture notes app",
        "note editor",
        "document scanner",
        "writing helper",
        "study app",
        "learning notes",
    ]
    
    logger.info(f"\nSearching with {len(search_queries)} different queries...")
    
    # Step 1: Search for apps
    app_ids = extractor.search_multiple_queries(search_queries, target_apps=150)
    
    if not app_ids:
        logger.warning("No new apps to extract.")
        extractor.print_summary()
        return
    
    # Step 2: Extract metadata for new apps
    logger.info("\n" + "="*70)
    logger.info("STEP 2: EXTRACT APP METADATA")
    logger.info("="*70)
    new_metadata = extractor.extract_metadata(app_ids, delay=1.5)
    
    if new_metadata:
        extractor.merge_and_save_metadata(new_metadata)
    
    # Step 3: Extract reviews
    logger.info("\n" + "="*70)
    logger.info("STEP 3: EXTRACT APP REVIEWS")
    logger.info("="*70)
    extractor.extract_reviews(app_ids, reviews_per_app=500, delay=0.8)
    
    # Final summary
    extractor.print_summary()


if __name__ == '__main__':
    main()
