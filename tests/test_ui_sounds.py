import functools
import http.server
import threading
import unittest
from pathlib import Path

from playwright.sync_api import sync_playwright


ROOT = Path(__file__).resolve().parents[1]


class UiSoundTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        handler = functools.partial(
            http.server.SimpleHTTPRequestHandler,
            directory=str(ROOT),
        )
        cls.server = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.frontend = (ROOT / "simple.html").read_text(encoding="utf-8")
        cls.desktop_backend = (ROOT / "main_desktop.py").read_text(encoding="utf-8")
        cls.browser_backend = (ROOT / "run.py").read_text(encoding="utf-8")

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()

    def _open_page(self, page):
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
            L=D.slice(); I=0; S={alpha:2,beta:2}; marked=true; show();
            window.__uiSounds=[];
            playUiSound=function(name,force){window.__uiSounds.push({name,force:!!force});};
            """
        )
        page.wait_for_timeout(50)
        page.evaluate("window.__uiSounds=[]")

    def _pointer_down(self, page, selector):
        page.locator(selector).dispatch_event(
            "pointerdown", {"pointerType": "mouse", "button": 0}
        )

    def test_primary_pointer_actions_have_distinct_sound_cues(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            self._open_page(page)

            for selector in (".show-btn", ".b3", ".b2", ".b1", "#nextBtn"):
                self._pointer_down(page, selector)
            page.evaluate("I=1; marked=true; show()")
            self._pointer_down(page, "#prevBtn")

            names = page.evaluate("window.__uiSounds.map(item => item.name)")
            self.assertEqual(
                names,
                ["reveal", "unknown", "fuzzy", "known", "next", "previous"],
            )
            browser.close()

    def test_keyboard_and_automatic_calls_do_not_emit_pointer_sounds(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            self._open_page(page)

            page.evaluate("showMeaning(); go(1); toggleSettings(true)")
            self.assertEqual(page.evaluate("window.__uiSounds"), [])
            browser.close()

    def test_sound_preference_is_remembered_and_synced_by_both_servers(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            self._open_page(page)

            page.evaluate("setSoundEnabled(false)")
            state = page.evaluate(
                """
                () => ({
                    enabled: uiSoundEnabled,
                    stored: electronStorage.getItem('vocab_sound_enabled'),
                    checked: document.getElementById('soundEnabledToggle').checked,
                })
                """
            )
            self.assertEqual(
                state, {"enabled": False, "stored": "false", "checked": False}
            )
            browser.close()

        self.assertIn("existing_data['soundEnabled']", self.desktop_backend)
        self.assertIn("existing_data['soundEnabled']", self.browser_backend)
        self.assertIn("soundEnabled:uiSoundEnabled", self.frontend)

    def test_sounds_are_runtime_synthesized_without_audio_assets(self):
        self.assertIn("new AudioContextClass()", self.frontend)
        self.assertIn("oscillator.frequency.exponentialRampToValueAtTime", self.frontend)
        self.assertNotIn(".mp3", self.frontend.lower())
        self.assertNotIn(".wav", self.frontend.lower())


if __name__ == "__main__":
    unittest.main()
