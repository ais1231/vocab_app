import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class NativeWindowInputContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.backend = (ROOT / "main_desktop.py").read_text(encoding="utf-8")
        cls.frontend = (ROOT / "simple.html").read_text(encoding="utf-8")

    def test_drag_does_not_use_pywebview_incremental_move_loop(self):
        drag_tag = '<div class="window-drag-surface" id="windowDragSurface"></div>'
        self.assertIn(drag_tag, self.frontend)
        self.assertNotIn("pywebview-drag-region", self.frontend)

    def test_move_and_resize_start_synchronously_on_native_ui_thread(self):
        self.assertIn("def install_webview_input_zones", self.backend)
        self.assertIn("_native_bootstrap_refs.extend((continue_on_ui, callback))", self.backend)
        self.assertNotIn("_native_input_refs.extend((continue_on_ui, callback))", self.backend)
        self.assertIn("panel.MouseDown += down", self.backend)
        action = self.backend.split("def begin_native_window_action", 1)[1].split("def set_win", 1)[0]
        self.assertIn("user32.SendMessageW(hwnd, 0x00A1, hit_test, lparam)", action)
        self.assertNotIn("PostMessageW", action)
        self.assertNotIn("handle.addEventListener('mousedown'", self.frontend)

    def test_hit_zones_match_canvas_without_layered_alpha_or_sizing_frame(self):
        self.assertIn("panel.BackColor = Color.FromArgb(232, 237, 240)", self.backend)
        self.assertIn("SetParent", self.backend)
        self.assertIn("monitor_timer.Interval = 400", self.backend)
        self.assertNotIn("WS_EX_LAYERED", self.backend)
        self.assertNotIn("SetLayeredWindowAttributes", self.backend)
        self.assertNotIn("WS_THICKFRAME", self.backend)


if __name__ == "__main__":
    unittest.main()
