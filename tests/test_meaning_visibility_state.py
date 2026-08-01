import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class MeaningVisibilityStateTests(unittest.TestCase):
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

    def test_visibility_is_restored_per_word_when_navigating(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            page.goto(
                f"http://127.0.0.1:{self.server.server_port}/simple.html",
                wait_until="networkidle",
            )
            page.evaluate(
                """
                D=[
                  {word:'alpha',definition:'first',pos:''},
                  {word:'beta',definition:'second',pos:''}
                ];
                L=D.slice(); I=0; S={alpha:2,beta:2}; shownWords={};
                currentWordClicked=false; show();
                """
            )

            page.locator(".show-btn").click()
            self.assertTrue(page.locator("#meaning").evaluate("el => el.classList.contains('show')"))

            page.evaluate("go(1); go(-1)")
            self.assertEqual(page.locator("#word").inner_text(), "alpha")
            self.assertTrue(page.locator("#meaning").evaluate("el => el.classList.contains('show')"))

            page.locator(".show-btn").click()
            page.evaluate("go(1); go(-1)")
            self.assertFalse(page.locator("#meaning").evaluate("el => el.classList.contains('show')"))
            browser.close()


if __name__ == "__main__":
    unittest.main()
