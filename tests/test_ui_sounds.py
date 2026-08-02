import functools
import http.server
import math
import re
import struct
import threading
import unittest
import wave
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
        cls.package_spec = (ROOT / "vocab_app.spec").read_text(encoding="utf-8")

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

    def test_global_shortcut_clears_stale_button_focus_but_tab_focus_still_works(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            self._open_page(page)

            page.locator(".b2").focus()
            before = page.evaluate(
                """
                () => ({
                    isButton: document.activeElement.matches('button'),
                    focusVisible: document.activeElement.matches(':focus-visible'),
                })
                """
            )
            page.keyboard.press("2")
            after_shortcut = page.evaluate(
                """
                () => ({
                    isButton: document.activeElement.matches('button'),
                    focusedButtons: document.querySelectorAll('button:focus-visible').length,
                })
                """
            )
            page.keyboard.press("Tab")
            after_tab = page.evaluate(
                """
                () => ({
                    isButton: document.activeElement.matches('button'),
                    focusVisible: document.activeElement.matches(':focus-visible'),
                })
                """
            )

            self.assertEqual(before, {"isButton": True, "focusVisible": True})
            self.assertEqual(
                after_shortcut, {"isButton": False, "focusedButtons": 0}
            )
            self.assertEqual(after_tab, {"isButton": True, "focusVisible": True})
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

    def test_secondary_sounds_remain_lightweight_runtime_synthesis(self):
        self.assertIn("new AudioContextClass()", self.frontend)
        self.assertIn("oscillator.frequency.exponentialRampToValueAtTime", self.frontend)
        self.assertNotIn(".mp3", self.frontend.lower())

    def test_synthesized_sound_output_is_soft_limited_and_uses_a_gentle_attack(self):
        match = re.search(r"var UI_SOUND_OUTPUT_GAIN=([0-9.]+);", self.frontend)
        self.assertIsNotNone(match)
        self.assertGreaterEqual(float(match.group(1)), 1.0)
        self.assertLessEqual(float(match.group(1)), 1.4)
        self.assertIn("var UI_SOUND_ATTACK=.012;", self.frontend)
        self.assertIn("var UI_SOUND_MAX_GAIN=.045;", self.frontend)
        self.assertIn("note.gain*UI_SOUND_OUTPUT_GAIN", self.frontend)
        self.assertIn("start+UI_SOUND_ATTACK", self.frontend)
        self.assertIn("Math.min(UI_SOUND_MAX_GAIN", self.frontend)
        self.assertNotIn("type:'triangle'", self.frontend)

    def test_primary_learning_feedback_uses_a_quiet_original_audio_sprite(self):
        sprite_path = ROOT / "assets" / "ui-feedback.wav"
        self.assertTrue(sprite_path.is_file())
        self.assertIn("assets/ui-feedback.wav", self.frontend)
        self.assertIn("UI_SOUND_SPRITES", self.frontend)
        self.assertIn("source.start(now,sprite.offset,sprite.duration)", self.frontend)
        self.assertIn("var UI_SOUND_CROSSFADE=.024;", self.frontend)
        self.assertIn("latencyHint:'interactive'", self.frontend)
        self.assertIn(
            "uiAudioContext.resume().then(function(){playUiSound(name,force);})",
            self.frontend,
        )
        self.assertIn("var now=uiAudioContext.currentTime+.002;", self.frontend)
        self.assertIn("uiPendingSoundName=name;", self.frontend)
        self.assertIn("prior.level.gain.exponentialRampToValueAtTime", self.frontend)
        self.assertIn("prior.source.stop(now+UI_SOUND_CROSSFADE", self.frontend)
        self.assertNotIn("uiPrimarySoundSource.stop()", self.frontend)
        self.assertIn("('assets/ui-feedback.wav', 'assets')", self.package_spec)

        mappings = {}
        for name in ("unknown", "fuzzy", "known"):
            mapping = re.search(
                rf"\b{name}:\{{offset:([0-9.]+),duration:([0-9.]+),gain:([0-9.]+)\}}",
                self.frontend,
            )
            self.assertIsNotNone(mapping)
            mappings[name] = tuple(float(value) for value in mapping.groups())
            self.assertNotRegex(self.frontend, rf"{name}:\[\{{from:")

        self.assertGreaterEqual(mappings["fuzzy"][1], 0.16)
        self.assertGreaterEqual(mappings["known"][1], 0.20)

        with wave.open(str(sprite_path), "rb") as sound:
            self.assertEqual(sound.getnchannels(), 1)
            self.assertEqual(sound.getsampwidth(), 2)
            self.assertEqual(sound.getframerate(), 44100)
            duration = sound.getnframes() / sound.getframerate()
            frames = sound.readframes(sound.getnframes())

        samples = struct.unpack(f"<{len(frames) // 2}h", frames)
        peak = max(abs(sample) for sample in samples) / 32767
        rms = math.sqrt(sum(sample * sample for sample in samples) / len(samples)) / 32767
        self.assertGreaterEqual(duration, 0.42)
        self.assertLessEqual(duration, 0.55)
        self.assertLessEqual(peak, 0.32)
        self.assertLessEqual(rms, 0.065)

        for name, (offset, cue_duration, gain) in mappings.items():
            start = round(offset * 44100)
            end = round((offset + cue_duration) * 44100)
            cue_peak = max(abs(sample) for sample in samples[start:end]) / 32767
            audible_peak = cue_peak * gain
            self.assertGreaterEqual(audible_peak, 0.05, name)
            self.assertLessEqual(audible_peak, 0.075, name)

    def test_primary_audio_sprite_decodes_and_plays_through_web_audio(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            page.goto(
                f"http://127.0.0.1:{self.server.server_port}/simple.html",
                wait_until="networkidle",
            )
            page.evaluate("() => loadUiSoundSprite()")
            state = page.evaluate(
                """
                () => ({
                    loaded: !!uiSoundSpriteBuffer,
                    duration: uiSoundSpriteBuffer && uiSoundSpriteBuffer.duration,
                    sampleRate: uiSoundSpriteBuffer && uiSoundSpriteBuffer.sampleRate,
                    played: playUiSoundSprite('unknown',uiAudioContext.currentTime+.006),
                    active: !!uiPrimarySoundVoice,
                })
                """
            )
            self.assertTrue(state["loaded"])
            self.assertAlmostEqual(state["duration"], 0.48, places=2)
            self.assertIn(state["sampleRate"], (44100, 48000))
            self.assertTrue(state["played"])
            self.assertTrue(state["active"])
            browser.close()

    def test_audio_sprite_preloads_before_slow_data_initialization(self):
        with sync_playwright() as playwright:
            browser = playwright.chromium.launch(headless=True)
            page = browser.new_page(viewport={"width": 620, "height": 850})
            page.add_init_script(
                """
                const nativeFetch=window.fetch.bind(window);
                window.__apiLoadResolved=false;
                window.fetch=function(input,init){
                    if(String(input).includes('/api/load')){
                        return new Promise(function(resolve){
                            setTimeout(function(){
                                window.__apiLoadResolved=true;
                                resolve(new Response('{}',{status:200,headers:{'Content-Type':'application/json'}}));
                            },1200);
                        });
                    }
                    return nativeFetch(input,init);
                };
                """
            )
            page.goto(
                f"http://127.0.0.1:{self.server.server_port}/simple.html",
                wait_until="domcontentloaded",
            )
            page.wait_for_function("uiSoundSpriteBuffer !== null", timeout=700)
            self.assertFalse(page.evaluate("window.__apiLoadResolved"))
            browser.close()


if __name__ == "__main__":
    unittest.main()
