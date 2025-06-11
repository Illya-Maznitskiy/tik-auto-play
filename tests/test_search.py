import pytest
from unittest.mock import MagicMock, patch
from src.search import perform_search
import sys
import os
from src.config import DEFAULT_SEARCH_QUERY

# Add the '../src' directory to the front of sys.path
# to enable absolute imports of project modules during testing
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)


@patch("src.search.expect")
@patch("src.search.logger")
def test_perform_search_with_valid_query(mock_logger, mock_expect):
    """
    Test that perform_search works correctly with a valid query,
    including element interactions and logging.
    """
    page = MagicMock()
    search_input = MagicMock()

    # Set up mocks
    page.locator.return_value = search_input
    page.keyboard.press.return_value = None
    page.wait_for_url.return_value = None

    perform_search(page, "funny cats")

    # Assertions
    page.locator.assert_called_with('input[placeholder*="Search"]')
    search_input.fill.assert_called_once_with("funny cats")
    page.keyboard.press.assert_called_once_with("Enter")
    page.wait_for_url.assert_called_once()
    mock_logger.info.assert_any_call("Search completed successfully.")

    # Fix: match how many times expect was called
    assert mock_expect.call_count == 2
    mock_expect.assert_any_call(search_input)


@patch("src.search.expect")
@patch("src.search.logger")
def test_perform_search_with_empty_query_uses_default(
    mock_logger, mock_expect
):
    """Test that empty search query falls back to default query."""
    page = MagicMock()
    search_input = MagicMock()

    page.locator.return_value = search_input
    page.keyboard.press.return_value = None
    page.wait_for_url.return_value = None

    perform_search(page, "")  # Pass empty string

    expected_query = DEFAULT_SEARCH_QUERY
    search_input.fill.assert_called_once_with(expected_query)
    page.keyboard.press.assert_called_once_with("Enter")
    page.wait_for_url.assert_called_once()
    mock_logger.info.assert_any_call("Search completed successfully.")

    # Optional: verify expect was called on the search_input locator
    mock_expect.assert_any_call(search_input)


@patch("src.search.logger")
def test_perform_search_raises_on_failure(mock_logger):
    """Test that perform_search logs error
    and raises when search input fails."""
    page = MagicMock()
    page.locator.side_effect = Exception("search bar not found")

    with pytest.raises(Exception, match="search bar not found"):
        perform_search(page, "error test")

    mock_logger.error.assert_called_once()
