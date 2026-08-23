import pytest
from scraper.ddu_scraper import DDUScraper


def test_scraper_clean_text():
    scraper = DDUScraper()
    raw = "   DDU   Information   \n\n\n\nTechnology   "
    cleaned = scraper.clean_text(raw)
    assert cleaned == "DDU Information Technology"


def test_scraper_init(tmp_path):
    scraper = DDUScraper(output_dir=str(tmp_path))
    assert scraper.output_dir == str(tmp_path)
