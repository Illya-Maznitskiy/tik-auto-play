import time

from unittest.mock import MagicMock
from src.viewer import watch_tiktok_feed


class DummyLocator:
    """
    A minimal stand-in for Playwright's Locator.
    Simulates a list of video links
    with a .all() method returning mock elements.
    """

    def __init__(self, hrefs):
        """
        Initialize with a list of href strings to simulate video links.

        :param hrefs: List of fake video URLs (e.g., ['/video/1', '/video/2']).
        """
        self.hrefs = hrefs
        self.call_count = 0

    def all(self):
        """
        Return a list of MagicMock objects, each simulating an element
        with a .get_attribute('href') method returning one of the fake URLs.
        """
        return [
            MagicMock(get_attribute=MagicMock(return_value=href))
            for href in self.hrefs
        ]


def test_watch_tiktok_feed_skip_and_watch(monkeypatch):
    """
    Test the watch_tiktok_feed function:
    - Skips the first video
    - Watches the next three
    - Ensures navigation and load state methods
    are called the expected number of times.
    """
    page = MagicMock()

    heights = [1000, 2000, 2000]
    page.evaluate = MagicMock(
        side_effect=lambda script: (
            heights.pop(0) if "scrollHeight" in script else None
        )
    )
    page.locator = MagicMock(
        return_value=DummyLocator(
            [
                "/video/1",
                "/video/2",
                "/video/3",
                "/video/4",
            ]
        )
    )
    page.wait_for_load_state = MagicMock()
    page.go_back = MagicMock()

    import random

    random_backup = random.randint

    def fake_randint(a, b):
        if fake_randint.call_count == 0:
            fake_randint.call_count += 1
            return 1
        else:
            fake_randint.call_count += 1
            return 100

    fake_randint.call_count = 0
    monkeypatch.setattr(random, "randint", fake_randint)

    # Patch time.sleep to a no-op to speed up the test
    monkeypatch.setattr(time, "sleep", lambda x: None)

    watch_tiktok_feed(page, skip_percent=50, max_videos_to_process=4)

    assert page.locator.called
    assert page.wait_for_load_state.call_count == 6
    assert page.go_back.call_count == 3

    monkeypatch.setattr(random, "randint", random_backup)
