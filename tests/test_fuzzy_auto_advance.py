import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class FuzzyAutoAdvanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler,
            directory=str(ROOT),
        )
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _new_page(self, browser):
        page = browser.new_page(viewport={"width": 620, "height": 850})
        page.goto(
            f"http://127.0.0.1:{self.server.server_port}/simple.html",
            wait_until="networkidle",
        )
        page.evaluate(
            """
            D=[
              {word:'alpha',definition:'first',pos:''},
              {word:'beta',definition:'second',pos:''},
              {word:'gamma',definition:'third',pos:''}
            ];
            L=D.slice(); I=0; S={}; shownWords={};
            currentWordClicked=false; FUZZY_AUTO_ADVANCE_MS=80; show();
            """
        )
        return page

    def test_fuzzy_always_waits_then_advances_even_if_meaning_was_visible(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)

            for was_visible in (False, True):
                page = self._new_page(browser)
                if was_visible:
                    page.evaluate("shownWords.alpha=true; show()")

                state = page.evaluate(
                    """
                    mark(1);
                    ({
                      index:I,
                      rating:S.alpha,
                      meaningVisible:document.getElementById('meaning').classList.contains('show')
                    })
                    """
                )
                self.assertEqual(state["index"], 0)
                self.assertEqual(state["rating"], 1)
                self.assertTrue(state["meaningVisible"])
                page.wait_for_function("I === 1", timeout=1000)
                page.close()

            browser.close()

    def test_manual_navigation_cancels_pending_fuzzy_advance(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = self._new_page(browser)

            page.evaluate("mark(1); go(1)")
            self.assertEqual(page.evaluate("I"), 1)
            page.wait_for_timeout(200)
            self.assertEqual(page.evaluate("I"), 1)

            browser.close()


if __name__ == "__main__":
    unittest.main()
