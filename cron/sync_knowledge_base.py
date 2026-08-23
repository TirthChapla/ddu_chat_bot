"""
Scheduled Knowledge Base Sync Script
Suitable for Cron jobs or Windows Task Scheduler.
Crawls ddu.ac.in, ingests new documents, and rebuilds ChromaDB embeddings.
"""

import os
import sys
import datetime
import logging

# Ensure project root is in sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper.ddu_scraper import DDUScraper
from embeddings.indexer import ChromaIndexer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("ddu_cron_sync")


def run_scheduled_sync():
    logger.info(f"=== Starting Scheduled DDU Knowledge Sync at {datetime.datetime.now()} ===")
    
    # 1. Scrape DDU website
    scraper = DDUScraper(output_dir="./data")
    scrape_results = scraper.run_scraper()
    logger.info(f"Scraper finished: {scrape_results['pages_scraped']} pages saved.")
    
    # 2. Re-index into ChromaDB
    indexer = ChromaIndexer(
        persist_dir="./vectordb",
        collection_name="ddu_knowledge_base",
        data_dir="./data",
        uploads_dir="./data/raw_uploads"
    )
    stats = indexer.rebuild_index()
    logger.info(f"ChromaDB re-indexing finished: {stats['total_chunks']} total chunks across {stats['total_documents']} documents.")
    logger.info("=== Knowledge Base Sync Completed Successfully ===")


if __name__ == "__main__":
    run_scheduled_sync()
