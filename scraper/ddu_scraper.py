"""
DDU Web Scraper Module
Crawls official sections of https://www.ddu.ac.in and saves structured content into the knowledge repository.
"""

import os
import re
import logging
from typing import Dict, List, Optional
import requests
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

DDU_BASE_URL = "https://www.ddu.ac.in"

# Target public pages to scrape
TARGET_PAGES = {
    "admissions": [
        "https://www.ddu.ac.in/admission/",
        "https://www.ddu.ac.in/admission-b-tech/",
        "https://www.ddu.ac.in/admission-m-tech/",
        "https://www.ddu.ac.in/admission-mca-mba/",
    ],
    "departments": [
        "https://www.ddu.ac.in/faculty-of-technology/",
        "https://www.ddu.ac.in/department-of-information-technology/",
        "https://www.ddu.ac.in/department-of-computer-engineering/",
        "https://www.ddu.ac.in/department-of-chemical-engineering/",
        "https://www.ddu.ac.in/faculty-of-pharmacy/",
        "https://www.ddu.ac.in/faculty-of-dental-science/",
    ],
    "placements": [
        "https://www.ddu.ac.in/placement-cell/",
        "https://www.ddu.ac.in/training-and-placement/",
    ],
    "circulars_notices": [
        "https://www.ddu.ac.in/circulars/",
        "https://www.ddu.ac.in/notices/",
        "https://www.ddu.ac.in/academic-calendar/",
    ],
}


class DDUScraper:
    def __init__(self, output_dir: str = "./data"):
        self.output_dir = output_dir
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            ),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        })
        os.makedirs(self.output_dir, exist_ok=True)

    def clean_text(self, text: str) -> str:
        """Sanitizes scraped HTML text."""
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\n+', '\n', text)
        return text.strip()

    def scrape_url(self, url: str) -> Optional[Dict[str, str]]:
        """Fetches and parses a single page URL."""
        try:
            logger.info(f"Fetching URL: {url}")
            response = self.session.get(url, timeout=10, verify=False)
            if response.status_code != 200:
                logger.warning(f"Failed to fetch {url} (Status: {response.status_code})")
                return None

            soup = BeautifulSoup(response.text, "html.parser")

            # Remove unwanted elements
            for tag in soup(["script", "style", "nav", "footer", "aside", "noscript", "header"]):
                tag.decompose()

            title = soup.title.string if soup.title else url
            content_blocks = []

            # Extract main content areas
            main_container = soup.find("main") or soup.find("div", class_=re.compile(r"content|entry|post|body")) or soup.body

            if main_container:
                for elem in main_container.find_all(["h1", "h2", "h3", "h4", "p", "li", "table"]):
                    if elem.name in ["h1", "h2", "h3", "h4"]:
                        header_text = self.clean_text(elem.get_text())
                        if header_text:
                            content_blocks.append(f"\n### {header_text}\n")
                    elif elem.name == "p":
                        p_text = self.clean_text(elem.get_text())
                        if p_text and len(p_text) > 20:
                            content_blocks.append(p_text)
                    elif elem.name == "li":
                        li_text = self.clean_text(elem.get_text())
                        if li_text:
                            content_blocks.append(f"- {li_text}")
                    elif elem.name == "table":
                        rows = elem.find_all("tr")
                        for row in rows:
                            cols = [self.clean_text(col.get_text()) for col in row.find_all(["td", "th"])]
                            if cols and any(cols):
                                content_blocks.append(" | ".join(cols))

            body_text = "\n".join(content_blocks).strip()
            if not body_text:
                body_text = self.clean_text(soup.get_text())

            return {
                "url": url,
                "title": self.clean_text(title) if title else "DDU Information",
                "content": body_text,
            }
        except Exception as e:
            logger.warning(f"Error scraping {url}: {e}")
            return None

    def run_scraper(self) -> Dict[str, any]:
        """Scrapes configured university pages and saves updated text files."""
        results = {
            "pages_scraped": 0,
            "failed_urls": [],
            "files_updated": [],
        }

        for category, urls in TARGET_PAGES.items():
            category_content = []
            for url in urls:
                page_data = self.scrape_url(url)
                if page_data and len(page_data["content"]) > 100:
                    results["pages_scraped"] += 1
                    category_content.append(
                        f"=== SOURCE: {page_data['title']} ({page_data['url']}) ===\n\n{page_data['content']}\n\n"
                    )
                else:
                    results["failed_urls"].append(url)

            if category_content:
                filepath = os.path.join(self.output_dir, f"scraped_{category}.txt")
                with open(filepath, "w", encoding="utf-8") as f:
                    f.write(f"# DDU Scraped Knowledge - {category.upper()}\n\n")
                    f.write("\n".join(category_content))
                results["files_updated"].append(filepath)
                logger.info(f"Updated {filepath} with {len(category_content)} pages.")

        return results


if __name__ == "__main__":
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    scraper = DDUScraper()
    stats = scraper.run_scraper()
    print("Scraping completed:", stats)
