import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class SettingsLayoutTests(unittest.TestCase):
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

    def _open_settings(self, page):
        page.goto(
            f"http://127.0.0.1:{self.server.server_port}/simple.html",
            wait_until="networkidle",
        )
        page.evaluate("toggleSettings(true); updateUiScale()")
        page.wait_for_timeout(50)

    def test_settings_scroll_area_starts_below_native_titlebar(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 500, "height": 700})
            self._open_settings(page)

            metrics = page.evaluate(
                """
                () => {
                    const panel = document.getElementById('settingsPanel');
                    const content = panel.querySelector('.settings-content');
                    const panelRect = panel.getBoundingClientRect();
                    const contentRect = content.getBoundingClientRect();
                    return {
                        panelTop: panelRect.top,
                        panelBottom: panelRect.bottom,
                        panelOverflow: getComputedStyle(panel).overflowY,
                        contentTop: contentRect.top,
                        contentBottom: contentRect.bottom,
                        contentOverflow: getComputedStyle(content).overflowY,
                    };
                }
                """
            )

            self.assertAlmostEqual(metrics["panelTop"], 44, delta=0.5)
            self.assertAlmostEqual(metrics["panelBottom"], 700, delta=0.5)
            self.assertEqual(metrics["panelOverflow"], "hidden")
            self.assertAlmostEqual(metrics["contentTop"], 44, delta=0.5)
            self.assertAlmostEqual(metrics["contentBottom"], 700, delta=1)
            self.assertEqual(metrics["contentOverflow"], "auto")
            browser.close()

    def test_settings_scale_tracks_window_size(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 760, "height": 980})
            self._open_settings(page)

            large = page.evaluate(
                """
                () => ({
                    width: document.getElementById('settingsPanel').getBoundingClientRect().width,
                    scale: Number(getComputedStyle(document.documentElement)
                        .getPropertyValue('--settings-scale')),
                })
                """
            )
            page.set_viewport_size({"width": 500, "height": 700})
            page.wait_for_timeout(200)
            small = page.evaluate(
                """
                () => ({
                    width: document.getElementById('settingsPanel').getBoundingClientRect().width,
                    scale: Number(getComputedStyle(document.documentElement)
                        .getPropertyValue('--settings-scale')),
                })
                """
            )

            self.assertGreater(large["scale"], small["scale"])
            self.assertGreater(large["width"], small["width"])
            self.assertLess(small["width"], 320)
            self.assertGreaterEqual(small["scale"], 0.72)
            browser.close()

    def test_titlebar_material_matches_native_hit_zones(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            self._open_settings(page)
            material = page.locator("#windowDragSurface").evaluate(
                """
                el => ({
                    background: getComputedStyle(el).backgroundColor,
                    backdrop: getComputedStyle(el).backdropFilter,
                })
                """
            )
            self.assertEqual(material["background"], "rgb(232, 237, 240)")
            self.assertEqual(material["backdrop"], "none")
            browser.close()


if __name__ == "__main__":
    unittest.main()
