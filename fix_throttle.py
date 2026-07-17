# -*- coding: utf-8 -*-
"""Restore SetBounds + 60fps throttle. Keep native drag via WM_NCLBUTTONDOWN."""
path = r'E:\code\vocab_app\main_desktop.py'
with open(path, 'r', encoding='utf-8') as f:
    py = f.read()

# === Fix 1: begin_native_window_action — only drag via WM_NCLBUTTONDOWN, no SC_SIZE ===
old1 = '''    def begin_native_window_action(self, hit_test):
        """Hand an active mouse gesture to Windows' native move/resize loop."""
        if sys.platform != 'win32' or not self._win or not getattr(self._win, 'native', None):
            return False
        try:
            hwnd = self._win.native.Handle.ToInt64()
            user32 = ctypes.windll.user32
            user32.ReleaseCapture()
            # 拖拽用 WM_NCLBUTTONDOWN（HTCAPTION），缩放用 WM_SYSCOMMAND + SC_SIZE
            if hit_test == 2:
                user32.SendMessageW(hwnd, 0x00A1, hit_test, 0)
            else:
                dir_map = {10:1,11:2,12:3,13:4,14:5,15:6,16:7,17:7}
                sc_dir = dir_map.get(hit_test, 2)
                user32.SendMessageW(hwnd, 0x0112, 0xF000 + sc_dir, 0)
            return True
        except Exception:
            return False'''
new1 = '''    def begin_native_window_action(self, hit_test):
        """Hand an active mouse gesture to Windows' native move/resize loop."""
        if sys.platform != 'win32' or not self._win or not getattr(self._win, 'native', None):
            return False
        if hit_test != 2:
            return False
        try:
            hwnd = self._win.native.Handle.ToInt64()
            user32 = ctypes.windll.user32
            user32.ReleaseCapture()
            user32.SendMessageW(hwnd, 0x00A1, hit_test, 0)
            return True
        except Exception:
            return False'''
py = py.replace(old1, new1)

# === Fix 2: make_handlers — restore SetBounds with 60fps throttle ===
old2 = '''    def make_handlers(direction, panel):
        def down(sender, event):
            if event.Button != WinForms.MouseButtons.Left:
                return
            hit = api.HIT_MAP.get(direction, 2)
            api.begin_native_window_action(hit)
        def move(sender, event):
            pass
        def up(sender, event):
            pass
        return down, move, up'''
new2 = '''    def make_handlers(direction, panel):
        _last_setbounds = [0.0]
        def down(sender, event):
            if event.Button != WinForms.MouseButtons.Left:
                return
            if direction == 'drag':
                api.begin_native_window_action(2)
                return
            hit = api.HIT_MAP.get(direction, 2)
            api.begin_native_window_action(hit)
            if hit != 2:
                return
            cursor = WinForms.Cursor.Position
            state.update(active=True, direction=direction, cursor_x=cursor.X, cursor_y=cursor.Y,
                         left=form.Left, top=form.Top, width=form.Width, height=form.Height,
                         limit_notified=False)
            panel.Capture = True
        def move(sender, event):
            if not state.get('active') or state.get('direction') != direction:
                return
            import time as _t
            now = _t.time()
            if now - _last_setbounds[0] < 0.016:
                return
            _last_setbounds[0] = now
            cursor = WinForms.Cursor.Position
            dx, dy = cursor.X-state['cursor_x'], cursor.Y-state['cursor_y']
            if direction == 'drag':
                form.Location = Point(state['left']+dx, state['top']+dy)
                return
            left, top = state['left'], state['top']
            requested_width, requested_height = state['width'], state['height']
            if 'e' in direction: requested_width = state['width']+dx
            if 'w' in direction: requested_width = state['width']-dx
            if 's' in direction: requested_height = state['height']+dy
            if 'n' in direction: requested_height = state['height']-dy
            min_width, min_height = form.MinimumSize.Width, form.MinimumSize.Height
            width, height = max(min_width, requested_width), max(min_height, requested_height)
            if 'w' in direction: left = state['left']+state['width']-width
            if 'n' in direction: top = state['top']+state['height']-height
            limited = requested_width < min_width or requested_height < min_height
            if limited and not state.get('limit_notified'):
                state['limit_notified'] = True
                api._size_limit_pending = True
            form.SetBounds(left, top, width, height)
        def up(sender, event):
            if event.Button == WinForms.MouseButtons.Left:
                state['active'] = False
                panel.Capture = False
        return down, move, up'''
py = py.replace(old2, new2)

with open(path, 'w', encoding='utf-8') as f:
    f.write(py)
print('Done')
