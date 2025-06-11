import os
import sys

import pytest
from unittest.mock import MagicMock, patch
import src.auth as auth


# Add the '../src' directory to the front of sys.path
# to enable absolute imports of project modules during testing
sys.path.insert(
    0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../src"))
)


STORAGE_STATE_PATH = auth.STORAGE_STATE_PATH


@patch("src.auth.os.path.exists")
@patch("src.auth._perform_login_and_save_session")
@patch("src.auth.sync_playwright")
def test_get_authenticated_page_and_context_no_storage(
    mock_playwright, mock_perform_login, mock_exists
):
    """
    Test get_authenticated_page_and_context performs manual login when
    no saved session exists and returns expected page and context.
    """
    mock_exists.return_value = False
    mock_perform_login.return_value = "page_mock"

    mock_browser = MagicMock()
    mock_browser.new_context.return_value = "context_mock"
    mock_playwright().__enter__.return_value.chromium.launch.return_value = (
        mock_browser
    )

    page, context, p = auth.get_authenticated_page_and_context()

    mock_perform_login.assert_called_once_with("context_mock")
    assert page == "page_mock"
    assert context == "context_mock"


@patch("src.auth.STORAGE_STATE_PATH", "mocked_path.json")
@patch("src.auth.os.path.exists")
@patch("src.auth._reuse_session")
@patch("src.auth.sync_playwright")
def test_get_authenticated_page_and_context_with_storage(
    mock_playwright, mock_reuse_session, mock_exists
):
    """
    Test that get_authenticated_page_and_context reuses saved session
    and returns the correct page and context when storage state file exists.
    """
    mock_exists.return_value = True
    mock_reuse_session.return_value = "page_mock"

    mock_browser = MagicMock()

    # mock new_context to accept storage_state arg and return "context_mock"
    def new_context_mock(*args, **kwargs):
        assert kwargs.get("storage_state") == "mocked_path.json"
        return "context_mock"

    mock_browser.new_context.side_effect = new_context_mock
    mock_playwright().__enter__.return_value.chromium.launch.return_value = (
        mock_browser
    )

    page, context, p = auth.get_authenticated_page_and_context()

    mock_reuse_session.assert_called_once_with("context_mock")
    assert page == "page_mock"
    assert context == "context_mock"


@patch("auth.logger")
def test_perform_login_and_save_session_wait_for_url_success(mock_logger):
    """
    Test _perform_login_and_save_session successfully waits for login
    to complete, saves the session, and returns the page object.
    """
    page_mock = MagicMock()
    context_mock = MagicMock()
    context_mock.new_page.return_value = page_mock

    page_mock.wait_for_url.return_value = None
    page_mock.goto.return_value = None

    result_page = auth._perform_login_and_save_session(context_mock)

    page_mock.wait_for_url.assert_called_once()
    context_mock.storage_state.assert_called_once()
    assert result_page == page_mock


@patch("auth.logger")
def test_perform_login_and_save_session_wait_for_url_timeout(mock_logger):
    """
    Test _perform_login_and_save_session raises RuntimeError
    when login timeout (wait_for_url) occurs.
    """
    page_mock = MagicMock()
    context_mock = MagicMock()
    context_mock.new_page.return_value = page_mock

    # Simulate wait_for_url raising an exception (timeout)
    page_mock.wait_for_url.side_effect = Exception("Timeout")

    with pytest.raises(RuntimeError):
        auth._perform_login_and_save_session(context_mock)

    page_mock.wait_for_url.assert_called_once()
