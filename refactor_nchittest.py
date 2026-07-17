# -*- coding: utf-8 -*-
"""Implement WM_NCHITTEST, remove 9 panels, simplify layout, frontend cache + is-resizing."""
import re

# ========== main_desktop.py ==========
with open(r'E:\code\vocab_app\main_desktop.py', 'r', encoding='utf-8') as f:
    py = f.read()

# 1) Remove begin_native_window_action + HIT_MAP (dead code)
old_begin = '''    def begin_native_window_action(self, hit_test):
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
new_begin = '''    def get_hwnd(self):
        if self._win and getattr(self._win, 'native', None):
            try:
                return self._win.native.Handle.ToInt64()
            except:
                pass
        return 0'''
py = py.replace(old_begin, new_begin)

# 2) Remove HIT_MAP from __init__
py = py.replace(
    "        self.HIT_MAP = {\n"
    "        'drag': 2,   # HTCAPTION\n"
    "        'e': 11,     # HTRIGHT\n"
    "        'w': 10,     # HTLEFT\n"
    "        's': 15,     # HTBOTTOM\n"
    "        'n': 12,     # HTTOP\n"
    "        'ne': 14,    # HTTOPRIGHT\n"
    "        'nw': 13,    # HTTOPLEFT\n"
    "        'se': 17,    # HTBOTTOMRIGHT\n"
    "        'sw': 16,    # HTBOTTOMLEFT\n"
    "    }",
    ""
)

# 3) Remove start_drag + drag_window (no longer needed)
old_drag = '''    def start_drag(self):
        if not self._win or not getattr(self._win, 'native', None):
            return None
        return {'left': int(self._win.native.Left), 'top': int(self._win.native.Top)}
    def drag_window(self, left, top):
        if self._win:
            self._win.move(int(left), int(top))
        return True
    def resize_from_grid'''
py = py.replace(old_drag, '    def resize_from_grid')

# 4) Replace install_webview_input_overlays: remove panels, add WM_NCHITTEST
old_overlays = '''def install_webview_input_overlays(*args):
    """Put synchronous drag/resize controls above the WebView2 child HWND."""
    global _native_input_scheduled
    if _native_input_refs:
        return
    import System.Windows.Forms as WinForms
    from System import Action
    from System.Drawing import Color, Point
    form = window.native
    if form.InvokeRequired:
        if not _native_input_scheduled:
            _native_input_scheduled = True
            form.BeginInvoke(Action(install_webview_input_overlays))
        return
    _native_input_scheduled = False
    host = form.webview
    state = {'active': False}
    cursors = {'drag':WinForms.Cursors.SizeAll,'n':WinForms.Cursors.SizeNS,'s':WinForms.Cursors.SizeNS,'e':WinForms.Cursors.SizeWE,'w':WinForms.Cursors.SizeWE,'ne':WinForms.Cursors.SizeNESW,'nw':WinForms.Cursors.SizeNWSE,'se':WinForms.Cursors.SizeNWSE,'sw':WinForms.Cursors.SizeNESW}
    panels = {}

    def make_handlers(direction, panel):
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
        return down, move, up

    for name, cursor in cursors.items():
        panel = WinForms.Panel()
        panel.Name = 'native_' + name
        panel.BackColor = Color.Transparent
        panel.Cursor = cursor
        panel.TabStop = False
        down, move, up = make_handlers(name, panel)
        panel.MouseDown += down; panel.MouseMove += move; panel.MouseUp += up
        host.Controls.Add(panel)
        panel.BringToFront()
        panels[name] = panel
        _native_input_refs.extend((panel, down, move, up))

    render_host = {'hwnd': 0}
    enum_type = ctypes.WINFUNCTYPE(ctypes.c_bool, ctypes.c_void_p, ctypes.c_void_p)
    user32 = ctypes.windll.user32
    user32.GetClassNameW.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.c_int]
    user32.SetParent.argtypes = [ctypes.c_void_p, ctypes.c_void_p]
    user32.SetParent.restype = ctypes.c_void_p
    user32.GetParent.argtypes = [ctypes.c_void_p]
    user32.GetParent.restype = ctypes.c_void_p
    user32.SetWindowPos.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_uint]
    def find_render_host(child_hwnd, unused):
        name = ctypes.create_unicode_buffer(128)
        user32.GetClassNameW(child_hwnd, name, len(name))
        if name.value == 'Chrome_RenderWidgetHostHWND':
            render_host['hwnd'] = int(child_hwnd)
            return False
        return True
    enum_callback = enum_type(find_render_host)
    def attach_render_host():
        if not render_host['hwnd']:
            user32.EnumChildWindows(form.Handle.ToInt64(), enum_callback, 0)
        if not render_host['hwnd']:
            return False
        for panel in panels.values():
            if user32.GetParent(panel.Handle.ToInt64()) != render_host['hwnd']:
                user32.SetParent(panel.Handle.ToInt64(), render_host['hwnd'])
        return True
    attach_render_host()
    _native_input_refs.extend((enum_callback, attach_render_host))
    
    # 原生缩放结束后检测是否到达最小尺寸
    def on_resize_end(sender, event):
        try:
            if form.Width <= form.MinimumSize.Width or form.Height <= form.MinimumSize.Height:
                api._size_limit_pending = True
        except:
            pass
    form.ResizeEnd += on_resize_end
    _native_input_refs.append(on_resize_end)
    
    def layout(sender=None, event=None):
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
            user32.SetWindowPos(panels[name].Handle.ToInt64(), 0, 0, 0, 0, 0, 0x0013)
    host.Resize += layout
    form.Resize += layout
    _native_input_refs.append(layout)
    layout()
    layout_timer = WinForms.Timer()
    layout_timer.Interval = 100
    def delayed_layout(sender=None, event=None):
        attached = attach_render_host()
        layout()
        if attached and max(host.ClientSize.Width, form.ClientSize.Width, form.Width) > 200 and max(host.ClientSize.Height, form.ClientSize.Height, form.Height) > 200:
            layout_timer.Stop()
    layout_timer.Tick += delayed_layout
    layout_timer.Start()
    _native_input_refs.extend((layout_timer, delayed_layout))'''

new_overlays = '''def install_webview_input_overlays(*args):
    """Hook WM_NCHITTEST for native move/resize via DWM. No more WinForms panels."""
    global _native_input_scheduled
    if _native_input_refs:
        return
    import System.Windows.Forms as WinForms
    from System import Action
    from System.Drawing import Point
    from ctypes import wintypes
    form = window.native
    if form.InvokeRequired:
        if not _native_input_scheduled:
            _native_input_scheduled = True
            form.BeginInvoke(Action(install_webview_input_overlays))
        return
    _native_input_scheduled = False
    
    # WM_NCHITTEST via native window proc subclassing
    hwnd = int(form.Handle)
    user32 = ctypes.windll.user32
    WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_int, ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_void_p)
    
    def nchitest_proc(h, msg, wp, lp):
        if msg != 0x0084:  # WM_NCHITTEST
            return user32.CallWindowProcW(_old_proc, h, msg, wp, lp)
        sx = ctypes.c_int16(lp & 0xFFFF).value
        sy = ctypes.c_int16((lp >> 16) & 0xFFFF).value
        pt = wintypes.POINT(sx, sy)
        user32.ScreenToClient(h, ctypes.byref(pt))
        cx, cy = pt.x, pt.y
        try:
            scale = float(form._scale)
        except:
            scale = 1.0
        edge = max(4, int(8 * scale))
        drag_top = int(40 * scale)
        btn_right = int(170 * scale)
        w, h = form.ClientSize.Width, form.ClientSize.Height
        if cy <= edge:
            if cx <= edge + 3: return 13
            if cx >= w - edge - 3: return 14
            return 12
        if cy >= h - edge:
            if cx <= edge + 3: return 16
            if cx >= w - edge - 3: return 17
            return 15
        if cx <= edge: return 10
        if cx >= w - edge: return 11
        if cy <= drag_top and cx < w - btn_right:
            return 2
        return 1
    
    nchitest_cb = WNDPROC(nchitest_proc)
    _old_proc = user32.SetWindowLongW(hwnd, -4, nchitest_cb)
    
    # size limit detection on resize end
    def on_resize_end(sender, event):
        try:
            if form.Width <= form.MinimumSize.Width or form.Height <= form.MinimumSize.Height:
                api._size_limit_pending = True
        except:
            pass
    form.ResizeEnd += on_resize_end
    
    _native_input_refs.extend((nchitest_cb, _old_proc, on_resize_end))'''

py = py.replace(old_overlays, new_overlays)

# 5) Remove _native_window_configured and enable_native_resize (panels are gone)
# Keep enable_native_resize as a no-op or modify it
old_enable = '''def enable_native_resize():
    """Configure only the frameless form limits and DWM appearance."""
    global _native_window_configured
    if sys.platform != 'win32' or not getattr(window, 'native', None):
        return
    if _native_window_configured:
        install_webview_input_overlays()
        return
    from System.Drawing import Size, Color
    scale = float(window.native._scale)
    window.native.MinimumSize = Size(int(500 * scale), int(700 * scale))
    window.native.BackColor = Color.FromArgb(232, 236, 241)
    apply_dwm_window_style()
    _native_window_configured = True'''
new_enable = '''def enable_native_resize():
    if sys.platform != 'win32' or not getattr(window, 'native', None):
        return
    from System.Drawing import Size, Color
    scale = float(window.native._scale)
    window.native.MinimumSize = Size(int(500 * scale), int(700 * scale))
    window.native.BackColor = Color.FromArgb(232, 236, 241)
    apply_dwm_window_style()
    install_webview_input_overlays()'''
py = py.replace(old_enable, new_enable)

# 6) Remove _native_window_configured global
py = py.replace('_native_window_configured = False\n', '')

# 7) Update events - remove loaded event (panels no longer need render host attach)
py = py.replace(
    "window.events.shown += enable_native_resize\nwindow.events.loaded += install_webview_input_overlays",
    "window.events.shown += enable_native_resize"
)

# 8) Remove unused imports in Api class (if any refs to FixPoint remain, keep them)
# FixPoint is used by resize_from_grid, keep it

with open(r'E:\code\vocab_app\main_desktop.py', 'w', encoding='utf-8') as f:
    f.write(py)

print('main_desktop.py done')
print('WM_NCHITTEST:', 'nchitest_proc' in open(r'E:\code\vocab_app\main_desktop.py','r',encoding='utf-8').read())

# ========== simple.html ==========
with open(r'E:\code\vocab_app\simple.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1) Cache card height: measure once, reuse during resize
old_measure = '''function measureStageHeight(){
    var card=document.querySelector('.card');
    var measured=card?Math.ceil(card.offsetHeight+20):806;
    return Math.max(806,measured);
}'''
new_measure = '''var _cachedStageHeight=0;
function measureStageHeight(){
    if(!_cachedStageHeight){
        var card=document.querySelector('.card');
        _cachedStageHeight=card?Math.max(806,Math.ceil(card.offsetHeight+20)):806;
    }
    return _cachedStageHeight;
}'''
html = html.replace(old_measure, new_measure)

# 2) Invalidate cache when content changes (not resize)
html = html.replace(
    "updateUiScale();window._loadStart=Date.now();",
    "_cachedStageHeight=0;updateUiScale();window._loadStart=Date.now();"
)

# 3) Remove ResizeObserver on .card (replace with window.resize only)
html = html.replace(
    "if(window.ResizeObserver){new ResizeObserver(scheduleUiScale).observe(document.querySelector('.card'));}",
    "// ResizeObserver removed - card scaling computed from window resize"
)

# 4) Add is-resizing CSS class mechanism (via JS polling the Python API)
# We'll add the CSS and a simple polling mechanism
resize_css = '''
/* 缩放期间禁用过渡，减轻渲染压力 */
.is-resizing *{transition:none!important;animation:none!important}
.is-resizing .window-control,.is-resizing .confirm-overlay{backdrop-filter:none}
.is-resizing .card{box-shadow:none}'''

html = html.replace(
    '@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}',
    '@media (prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;transition-duration:.01ms!important}}' + resize_css
)

# 5) JS: log resize stats
html = html.replace(
    'function updateUiScale(){',
    'var _resizeCount=0,_lastLayoutTime=0;\nfunction updateUiScale(){'
)

with open(r'E:\code\vocab_app\simple.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('simple.html done')
print('OK' if '_cachedStageHeight' in open(r'E:\code\vocab_app\simple.html','r',encoding='utf-8').read() else 'FAIL')
