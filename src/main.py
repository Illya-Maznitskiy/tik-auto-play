import time

from src.auth import (
    get_authenticated_page_and_context,
)
from src.search import perform_search
from logs.logger import logger
from src.viewer import watch_tiktok_feed


def main():
    """
    Runs the main TikTok automation script,
    handling login, search, and cleanup.
    """
    logger.info("Starting TikTok automation script.")

    # Initialize variables to prevent errors
    page = None
    context = None
    p_instance = None

    try:
        # Get browser controls (page), session (context),
        # and the Playwright program (p_instance)
        page, context, p_instance = get_authenticated_page_and_context()

        # Perform the search operation on TikTok.
        perform_search(page)

        # Now that the search is done, start watching videos from the feed.
        watch_tiktok_feed(page)

    except Exception as e:
        logger.error(f"An error occurred during the script's work: {e}")

    # Ensures the browser window and its background processes
    # are shut down, even if your script crashes
    finally:
        # Check if context was successfully assigned
        if context:
            logger.info(
                "Keeping browser open for 10 seconds "
                "for review before closing..."
            )
            time.sleep(10)
            # Close the browser context (which closes the browser window)
            context.close()
            logger.info("Browser context closed.")

        # Check if Playwright instance was successfully assigned
        if p_instance:
            # Properly exit the Playwright instance
            # created by sync_playwright().__enter__()
            p_instance.stop()
            logger.info("Playwright instance exited.")
        else:
            logger.warning("No Playwright instance to close.")

    logger.info("TikTok automation script finished.")


if __name__ == "__main__":
    main()
