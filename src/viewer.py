import time
import random

from playwright.sync_api import Page

from logs.logger import (
    logger,
)
from src.config import (
    DEFAULT_SKIP_PERCENT,
    MIN_WATCH_DURATION_SECONDS,
    MAX_WATCH_DURATION_SECONDS,
    MAX_FEED_SCROLLS,
    MAX_VIDEOS_TO_PROCESS,
)


def watch_tiktok_feed(
    page: Page,
    skip_percent: int = DEFAULT_SKIP_PERCENT,
    max_videos_to_process: int = MAX_VIDEOS_TO_PROCESS,
):
    """
    Walks through TikTok search results, watching
    or skipping videos based on skip_percent,
    scrolling to load more, and logging actions.
    Processes up to max_videos_to_process videos.
    """
    logger.info(
        f"Starting to watch TikTok feed with {skip_percent}% skip chance."
    )

    processed_videos_count = 0
    unique_video_urls = set()
    scroll_count = 0
    last_scroll_height = -1

    # Loop as long as we haven't processed enough videos and can still scroll
    while (
        processed_videos_count < max_videos_to_process
        and scroll_count < MAX_FEED_SCROLLS
    ):
        # Get the current scroll height of the page
        current_scroll_height = page.evaluate("document.body.scrollHeight")

        # Check if we're stuck (no new content loaded after scrolling)
        if current_scroll_height == last_scroll_height and scroll_count > 0:
            logger.info(
                "Reached end of scrollable content or "
                "no new videos found after scrolling."
            )
            break

        last_scroll_height = current_scroll_height

        # Scroll down to load more videos in the feed
        logger.info(
            f"Scrolling down the feed "
            f"(Scroll {scroll_count + 1}/{MAX_FEED_SCROLLS})..."
        )
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")

        # Give some time for new content to load and render after scrolling
        time.sleep(2)
        scroll_count += 1

        video_links = page.locator(
            'div[data-e2e="search-video-card"] a[href*="/video/"]'
        ).all()
        logger.info(f"Found {len(video_links)} video links on current view.")

        new_videos_found_this_scroll = False

        for link_element in video_links:
            try:
                video_url = link_element.get_attribute("href")
                if not video_url:
                    continue  # Skip if the URL attribute is missing

                # Remove query params to normalize and track unique URLs
                base_video_url = video_url.split("?")[0]

                if base_video_url in unique_video_urls:
                    continue  # Skip if this video has already been processed

                unique_video_urls.add(base_video_url)
                new_videos_found_this_scroll = True
                processed_videos_count += 1

                # Extract a simple video ID from the URL for logging purposes
                video_id = (
                    base_video_url.split("/")[-1]
                    if base_video_url.split("/")[-1]
                    else base_video_url
                )

                # Decide to skip based on skip_percent
                should_skip = random.randint(1, 100) <= skip_percent

                if should_skip:
                    logger.info(
                        f"Video ID: {video_id}, Link: {video_url} - Skipped."
                    )
                else:
                    logger.info(
                        f"Video ID: {video_id}, "
                        f"Link: {video_url} - Watching..."
                    )

                    # Click the link to navigate to the individual video page
                    link_element.click()

                    # Wait for video page to fully load
                    # ('networkidle' = no active requests)
                    page.wait_for_load_state("networkidle", timeout=30000)

                    # Pick random watch time within set range
                    watch_time = random.randint(
                        MIN_WATCH_DURATION_SECONDS, MAX_WATCH_DURATION_SECONDS
                    )
                    logger.info(f"Watching video for {watch_time} seconds.")
                    time.sleep(watch_time)

                    logger.info(
                        f"Video ID: {video_id}, Link: {video_url} "
                        f"- Watched fully. Returning to search results."
                    )

                    # Go back to the previous page (the search results feed)
                    page.go_back()

                    # Wait for search results to reload
                    page.wait_for_load_state("networkidle", timeout=30000)

                # Stop if max videos processed
                if processed_videos_count >= max_videos_to_process:
                    logger.info(
                        f"Reached maximum number of "
                        f"videos to process: {max_videos_to_process}."
                    )
                    break

            except Exception as e:
                # Log error and continue
                logger.error(
                    f"Error processing video link {link_element}: {e}"
                )
                continue

        if processed_videos_count >= max_videos_to_process:
            break

        # it suggests we've reached the end of new content for now.
        if (
            not new_videos_found_this_scroll
            and scroll_count > 0
            and processed_videos_count > 0
        ):
            logger.info(
                "No new unique videos found after scrolling. "
                "Ending feed watch."
            )
            break

    logger.info(
        f"Finished watching TikTok feed. "
        f"Processed {processed_videos_count} unique videos."
    )
