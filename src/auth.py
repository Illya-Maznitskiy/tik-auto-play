import os
import time
from playwright.sync_api import (
    sync_playwright,
    Page,
    BrowserContext,
    Playwright,
)
from src.config import STORAGE_STATE_PATH
from logs.logger import logger


def _perform_login_and_save_session(context: BrowserContext) -> Page:
    """
    Manages manual user login and saves the authenticated session to a file.
    """
    page = context.new_page()
    page.goto("https://www.tiktok.com/login")
    logger.info(
        "⏳ Please log in manually. Waiting for login completion (max 90s)..."
    )

    try:
        page.wait_for_url(
            lambda url: "tiktok.com/" in url and "/login" not in url,
            timeout=90000,
        )
        logger.info("✅ Login detected and page loaded.")
    except Exception as e:
        logger.warning(f"Login not detected within timeout or error: {e}.")
        raise RuntimeError(
            "Failed to log in to TikTok within the allotted time."
        ) from e

    context.storage_state(path=STORAGE_STATE_PATH)
    logger.info("✅ Session saved.")

    return page


def _reuse_session(context: BrowserContext) -> Page:
    """Internal helper: Loads saved session and returns the page."""
    page = context.new_page()
    page.goto("https://www.tiktok.com/")
    logger.info("✅ Session loaded. You're logged in.")
    time.sleep(3)  # Give it a moment to load
    return page


def get_authenticated_page_and_context() -> (
    tuple[Page, BrowserContext, Playwright]
):
    """
    Launches Playwright, handles login, and returns the active page,
    browser context, and Playwright instance.
    """
    p = sync_playwright().__enter__()
    browser = p.chromium.launch(headless=False)

    context: BrowserContext
    page: Page

    if not os.path.exists(STORAGE_STATE_PATH):
        logger.info("No saved session found. Starting manual login process.")
        context = browser.new_context()
        page = _perform_login_and_save_session(context)
    else:
        logger.info("Saved session found. Attempting to reuse session.")
        context = browser.new_context(storage_state=STORAGE_STATE_PATH)
        page = _reuse_session(context)

    return page, context, p
