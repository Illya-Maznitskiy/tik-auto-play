from playwright.sync_api import Page, expect
from logs.logger import logger
from config import DEFAULT_SEARCH_QUERY
import time


def perform_search(page: Page, query: str = DEFAULT_SEARCH_QUERY):
    """Performs a search on TikTok using the given query."""
    logger.info(f"Starting search for query: '{query}'")

    try:
        search_input_selector = 'input[placeholder*="Search"]'
        search_input = page.locator(search_input_selector)
        expect(search_input).to_be_visible()
        expect(search_input).to_be_enabled()
        logger.info("Found search input field.")

        search_input.fill(query)
        logger.info(f"Entered search query: '{query}'")
        page.keyboard.press("Enter")
        logger.info("Pressed Enter to submit search.")

        page.wait_for_url(
            lambda url: "/tag/" in url or "/search/video/" in url,
            timeout=30000,
        )
        logger.info("Successfully navigated to search results page.")

        time.sleep(3)  # Give some time for videos to load
        logger.info("Search completed successfully.")

    except Exception as e:
        logger.error(f"Error during search: {e}")
        raise
