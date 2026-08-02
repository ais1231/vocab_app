import functools
import http.server
import io
import threading
import unittest
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class ExitOverlayTests(unittest.TestCase):
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

    def test_exit_overlay_respects_window_corner_without_changing_box_animation(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            page.goto(
                f"http://127.0.0.1:{self.server.server_port}/simple.html",
                wait_until="networkidle",
            )
            page.evaluate(
                "requestConfirm('退出应用','确定要退出吗？学习进度会在退出前保存。','退出',function(){})"
            )
            page.wait_for_timeout(40)

            styles = page.evaluate(
                """
                () => {
                    const overlay=getComputedStyle(document.getElementById('confirmOverlay'));
                    const box=getComputedStyle(document.querySelector('.confirm-box'));
                    return {
                        radius: overlay.borderTopRightRadius,
                        bottomRadius: overlay.borderBottomRightRadius,
                        clipPath: overlay.clipPath,
                        animationName: box.animationName,
                        animationDuration: box.animationDuration,
                        animationTiming: box.animationTimingFunction,
                    };
                }
                """
            )
            screenshot = Image.open(io.BytesIO(page.screenshot())).convert("RGB")
            corner = screenshot.getpixel((617, 3))
            bottom_corner = screenshot.getpixel((617, 847))

            self.assertEqual(styles["radius"], "22px")
            self.assertEqual(styles["bottomRadius"], "0px")
            self.assertNotEqual(styles["clipPath"], "none")
            self.assertGreater(min(corner), 220)
            self.assertLess(max(bottom_corner), 210)
            self.assertEqual(styles["animationName"], "surfaceEnter")
            self.assertEqual(styles["animationDuration"], "0.19s")
            self.assertIn("0.23", styles["animationTiming"])
            browser.close()


if __name__ == "__main__":
    unittest.main()
