# -*- coding: utf-8 -*-
"""Replace WinForms panel resize with native WM_NCLBUTTONDOWN resize loop."""

path = r'E:\code\vocab_app\main_desktop.py'
with open(path, 'r', encoding='utf-8') as f:
    py = f.read()

# === Fix 1: begin_native_window_action — self.win → self._win ===
old = '''    def begin_native_window_action(self, hit_test):
        """Hand an active mouse gesture to Windows' native move/resize loop."""
        if sys.platform != 'win32' or not self.win or not getattr(self.win, 'native', None):
            return False
        try:
            hwnd = self.win.native.Handle.ToInt64()
            user32 = ctypes.windll.user32
            user32.ReleaseCapture()
            user32.SendMessageW(hwnd, 0x00A1, int(hit_test), 0)
            return True
        except Exception:
            return False'''
new = '''    def begin_native_window_action(self, hit_test):
        """Hand an active mouse gesture to Windows' native move/resize loop."""
        if sys.platform != 'win32' or not self._win or not getattr(self._win, 'native', None):
            return False
        try:
            hwnd = self._win.native.Handle.ToInt64()
            user32 = ctypes.windll.user32
            user32.ReleaseCapture()
            user32.SendMessageW(hwnd, 0x00A1, int(hit_test), 0)
            return True
        except Exception:
            return False'''
py = py.replace(old, new)

# === Fix 2: Hit-test mapping for each direction ===
# Direction → hit-test code mapping
HIT_MAP = """\
    HIT_MAP = {
        'drag': 2,   # HTCAPTION
        'e': 11,     # HTRIGHT
        'w': 10,     # HTLEFT
        's': 15,     # HTBOTTOM
        'n': 12,     # HTTOP
        'ne': 14,    # HTTOPRIGHT
        'nw': 13,    # HTTOPLEFT
        'se': 17,    # HTBOTTOMRIGHT
        'sw': 16,    # HTBOTTOMLEFT
    }"""

# Add HIT_MAP to the Api class, after _size_limit_pending
py = py.replace(
    "        self._size_limit_pending = False",
    "        self._size_limit_pending = False"
    + HIT_MAP
)

# === Fix 3: Rewrite make_handlers — down() uses native resize ===
old_handlers = '''    def make_handlers(direction, panel):
        def down(sender, event):
            if event.Button != WinForms.MouseButtons.Left:
                return
            global _native_resize_active
            _native_resize_active = True
            cursor = WinForms.Cursor.Position
            state.update(active=True, direction=direction, cursor_x=cursor.X, cursor_y=cursor.Y,
                         left=form.Left, top=form.Top, width=form.Width, height=form.Height,
                         limit_notified=False)
            panel.Capture = True
        def move(sender, event):
            if not state.get('active') or state.get('direction') != direction:
                return
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
                global _native_resize_active
                _native_resize_active = False
                state['active'] = False
                panel.Capture = False
        return down, move, up'''

new_handlers = '''    def make_handlers(direction, panel):
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

py = py.replace(old_handlers, new_handlers)

# === Fix 4: Remove _native_resize_active from layout() ===
old_layout = '''    def layout(sender=None, event=None):
        global _native_resize_active
        width = max(host.ClientSize.Width, form.ClientSize.Width, form.Width)
        height = max(host.ClientSize.Height, form.ClientSize.Height, form.Height)
        edge = 8
        panels['drag'].SetBounds(edge, edge+6, max(0, width-126), 30)
        panels['n'].SetBounds(edge, 0, max(0, width-edge*2), edge)
        panels['s'].SetBounds(edge, max(0, height-edge*2), max(0, width-edge*2), edge)
        panels['w'].SetBounds(0, edge, edge, max(0, height-edge*2))
        panels['e'].SetBounds(max(0, width-edge*2), edge, edge, max(0, height-edge*2))
        panels['nw'].SetBounds(0, 0, edge+3, edge+3)
        panels['ne'].SetBounds(max(0, width-edge*2-3), 0, edge+3, edge+3)
        panels['sw'].SetBounds(0, max(0, height-edge*2-3), edge+3, edge+3)
        panels['se'].SetBounds(max(0, width-edge*2-3), max(0, height-edge*2-3), edge+3, edge+3)
        # resize 期间跳过 BringToFront/SetWindowPos（只在非拖拽时校正 Z 序）
        if not _native_resize_active:
            for name in panels:
                panels[name].BringToFront()
                user32.SetWindowPos(panels[name].Handle.ToInt64(), 0, 0, 0, 0, 0, 0x0013)'''
new_layout = '''    def layout(sender=None, event=None):
        width = max(host.ClientSize.Width, form.ClientSize.Width, form.Width)
        height = max(host.ClientSize.Height, form.ClientSize.Height, form.Height)
        edge = 8
        panels['drag'].SetBounds(edge, edge+6, max(0, width-126), 30)
        panels['n'].SetBounds(edge, 0, max(0, width-edge*2), edge)
        panels['s'].SetBounds(edge, max(0, height-edge*2), max(0, width-edge*2), edge)
        panels['w'].SetBounds(0, edge, edge, max(0, height-edge*2))
        panels['e'].SetBounds(max(0, width-edge*2), edge, edge, max(0, height-edge*2))
        panels['nw'].SetBounds(0, 0, edge+3, edge+3)
        panels['ne'].SetBounds(max(0, width-edge*2-3), 0, edge+3, edge+3)
        panels['sw'].SetBounds(0, max(0, height-edge*2-3), edge+3, edge+3)
        panels['se'].SetBounds(max(0, width-edge*2-3), max(0, height-edge*2-3), edge+3, edge+3)
        for name in panels:
            panels[name].BringToFront()
            user32.SetWindowPos(panels[name].Handle.ToInt64(), 0, 0, 0, 0, 0, 0x0013)'''
py = py.replace(old_layout, new_layout)

# === Fix 5: Remove _native_resize_active global ===
py = py.replace('_native_resize_active = False\n', '')

# Also remove any remaining references to state variable (no longer used in handlers)
# The state = {'active': False} is still used by... nothing now, but harmless

with open(path, 'w', encoding='utf-8') as f:
    f.write(py)

print('Done')
# Verify
print('self._win fixed:', 'not self._win' in py and 'self.win' not in py[py.find('begin_native_window_action'):py.find('begin_native_window_action')+200])
print('HIT_MAP added:', 'HIT_MAP' in py)
print('new handlers:', 'api.begin_native_window_action(hit)' in py)
print('no _native_resize_active:', '_native_resize_active' not in py)
print('no form.SetBounds in handlers:', 'form.SetBounds' not in py[py.find('make_handlers'):py.find('make_handlers')+800])
print('layout restored:', 'panels[name].BringToFront()' in py[py.find('def layout'):py.find('def layout')+600])
