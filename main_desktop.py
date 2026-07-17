import webview
import threading
import http.server
import socketserver
import os
import json
import time
import sys
import urllib.request
import urllib.error
import ctypes

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
    BASE_DIR = sys._MEIPASS
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PORT = 19000
DATA_DIR = 'D:\\vocab_app_data'
DATA_FILE = os.path.join(DATA_DIR, 'vocab_save.json')
STARTUP_ERROR = None
try:
    os.makedirs(DATA_DIR, exist_ok=True)
    probe_path = os.path.join(DATA_DIR, '.write_test')
    with open(probe_path, 'w', encoding='utf-8') as probe:
        probe.write('ok')
    os.remove(probe_path)
except OSError as exc:
    STARTUP_ERROR = f'数据目录不可写：{DATA_DIR}\n{exc}'

with open(os.path.join(BASE_DIR, 'simple.html'), 'r', encoding='utf-8') as f:
    _SIMPLE_HTML = f.read()

# 注入loading遮罩到simple.html的<body>标签后
_LOADING_INJECT = '''
<div id="pywebviewLoading" style="position:fixed;top:0;left:0;width:100%;height:100%;background:#e8ecf1;z-index:99999;display:flex;justify-content:center;align-items:center;font-family:'Maple Mono NF CN','Segoe UI Emoji',monospace">
<div style="text-align:center">
<div style="font-size:72px;margin-bottom:30px;animation:pvf 3s ease-in-out infinite">\U0001F4D6</div>
<div style="font-size:36px;font-weight:700;margin-bottom:8px;letter-spacing:4px;color:#2d3748">\u8003\u7814\u82f1\u8bed\u4e8c\u8bcd\u6c47</div>
<div style="font-size:16px;color:#718096;margin-bottom:40px;letter-spacing:2px">Vocabulary Learning App</div>
<div style="display:flex;gap:8px;justify-content:center;margin-bottom:20px">
<div style="width:12px;height:12px;border-radius:50%;background:#a78bfa;animation:pvb 1.4s ease-in-out infinite"></div>
<div style="width:12px;height:12px;border-radius:50%;background:#60a5fa;animation:pvb 1.4s ease-in-out .2s infinite"></div>
<div style="width:12px;height:12px;border-radius:50%;background:#34d399;animation:pvb 1.4s ease-in-out .4s infinite"></div>
<div style="width:12px;height:12px;border-radius:50%;background:#fbbf24;animation:pvb 1.4s ease-in-out .6s infinite"></div>
<div style="width:12px;height:12px;border-radius:50%;background:#f87171;animation:pvb 1.4s ease-in-out .8s infinite"></div>
</div>
<div style="font-size:13px;color:#a0aec0;letter-spacing:1px">\u6b63\u5728\u52a0\u8f7d\u8bcd\u5e93\u6570\u636e...</div>
</div></div>
<style>@keyframes pvf{0%,100%{transform:translateY(0)}50%{transform:translateY(-15px)}}@keyframes pvb{0%,80%,100%{transform:scale(.6);opacity:.4}40%{transform:scale(1);opacity:1}}</style>
<script>
(function(){
    function removeOverlay(){
        var ov=document.getElementById('pywebviewLoading');
        if(ov){ov.style.transition='opacity 0.5s';ov.style.opacity='0';setTimeout(function(){ov.remove();},500);}
    }
    // 页面加载完成后2秒移除
    if(document.readyState==='complete'){setTimeout(removeOverlay,2000);}
    else{window.addEventListener('load',function(){setTimeout(removeOverlay,2000);});}
})();
</script>
'''
_SIMPLE_HTML = _SIMPLE_HTML.replace('<body>', '<body>' + _LOADING_INJECT, 1)

class VocabHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass
    def _origin(self):
        o = self.headers.get('Origin', '')
        return o if o else '*'
    def translate_path(self, path):
        path = path.split('?', 1)[0].split('#', 1)[0]
        path = os.path.normpath(path.lstrip('/'))
        return os.path.join(BASE_DIR, path)
    def do_GET(self):
        if self.path == '/api/load':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', self._origin())
            self.end_headers()
            try:
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
                        data = json.load(f)
                    self.wfile.write(json.dumps(data).encode('utf-8'))
                else:
                    self.wfile.write(b'null')
            except Exception as e:
                self.wfile.write(json.dumps({'error': str(e)}).encode('utf-8'))
            return
        if self.path == '/' or self.path == '/simple.html' or self.path.startswith('/simple.html?'):
            self.send_response(200)
            self.send_header('Content-Type', 'text/html; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', self._origin())
            self.end_headers()
            self.wfile.write(_SIMPLE_HTML.encode('utf-8'))
            return
        super().do_GET()
    def do_POST(self):
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', self._origin())
            self.end_headers()
            try:
                data = json.loads(post_data.decode('utf-8'))
                existing_data = {}
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
                        existing_data = json.load(f)
                if 'vocab_book_kaoyan' in data or 'vocab_progress_kaoyan' in data:
                    if 'books' not in existing_data:
                        existing_data = {'version': '1.0', 'books': {}}
                    book_ids = set()
                    for key in data:
                        if key.startswith('vocab_book_'):
                            book_ids.add(key.replace('vocab_book_', ''))
                        elif key.startswith('vocab_progress_'):
                            book_ids.add(key.replace('vocab_progress_', ''))
                        elif key.startswith('vocab_unlearned_'):
                            book_ids.add(key.replace('vocab_unlearned_', ''))
                    for book_id in book_ids:
                        if book_id not in existing_data['books']:
                            existing_data['books'][book_id] = {'state': {}, 'progress': {}, 'unlearned': {}}
                        state_key = 'vocab_book_' + book_id
                        if state_key in data:
                            state_data = json.loads(data[state_key]) if isinstance(data[state_key], str) else data[state_key]
                            existing_data['books'][book_id]['state'] = state_data
                        progress_key = 'vocab_progress_' + book_id
                        if progress_key in data:
                            progress_data = json.loads(data[progress_key]) if isinstance(data[progress_key], str) else data[progress_key]
                            existing_data['books'][book_id]['progress'] = progress_data
                            if 'state' not in existing_data['books'][book_id]:
                                existing_data['books'][book_id]['state'] = {}
                            existing_data['books'][book_id]['state']['S'] = progress_data
                        unlearned_key = 'vocab_unlearned_' + book_id
                        if unlearned_key in data:
                            unlearned_data = json.loads(data[unlearned_key]) if isinstance(data[unlearned_key], str) else data[unlearned_key]
                            existing_data['books'][book_id]['unlearned'] = unlearned_data
                    if 'vocab_current_book' in data:
                        existing_data['currentBook'] = data['vocab_current_book']
                    data = existing_data
                tmp = DATA_FILE + '.tmp'
                with open(tmp, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                os.replace(tmp, DATA_FILE)
                self.wfile.write(b'{"success": true}')
            except Exception as e:
                self.wfile.write(json.dumps({'success': False, 'error': str(e)}).encode('utf-8'))
            return
        super().do_POST()
    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header('Access-Control-Allow-Origin', self._origin())
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True
    daemon_threads = True

httpd = None
server_ready = threading.Event()
server_error = None

def start_server():
    global httpd, server_error
    try:
        httpd = ThreadedTCPServer(("127.0.0.1", PORT), VocabHandler)
        server_ready.set()
        httpd.serve_forever(poll_interval=0.2)
    except OSError as exc:
        server_error = f'本地服务无法启动（端口 {PORT} 可能被占用）：\n{exc}'
        server_ready.set()
    finally:
        if httpd:
            httpd.server_close()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()
server_ready.wait(timeout=5)

if not server_error and not STARTUP_ERROR:
    for _ in range(100):
        try:
            urllib.request.urlopen(f'http://127.0.0.1:{PORT}/api/load', timeout=0.1)
            break
        except (OSError, urllib.error.URLError):
            time.sleep(0.05)
class Api:
    def __init__(self):
        self._win = None
        self._maximized = False
        self._size_limit_pending = False
        self.HIT_MAP = {
        'drag': 2,   # HTCAPTION
        'e': 11,     # HTRIGHT
        'w': 10,     # HTLEFT
        's': 15,     # HTBOTTOM
        'n': 12,     # HTTOP
        'ne': 14,    # HTTOPRIGHT
        'nw': 13,    # HTTOPLEFT
        'se': 17,    # HTBOTTOMRIGHT
        'sw': 16,    # HTBOTTOMLEFT
    }
    def begin_native_window_action(self, hit_test):
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
            return False
    def set_win(self, win):
        self._win = win
    def exit(self):
        if self._win:
            self._win.destroy()
        return True
    def minimize(self):
        if self._win:
            self._win.minimize()
        return True
    def start_drag(self):
        if not self._win or not getattr(self._win, 'native', None):
            return None
        return {'left': int(self._win.native.Left), 'top': int(self._win.native.Top)}
    def drag_window(self, left, top):
        if self._win:
            self._win.move(int(left), int(top))
        return True
    def resize_from_grid(self, width, height, anchor):
        if not self._win or self._maximized:
            return False
        requested_width = int(round(float(width)))
        requested_height = int(round(float(height)))
        limited = requested_width < 500 or requested_height < 700
        target_width = max(500, requested_width)
        target_height = max(700, requested_height)
        anchors = {
            'e': FixPoint.WEST,
            'w': FixPoint.EAST,
            'n': FixPoint.SOUTH,
            's': FixPoint.NORTH,
            'ne': FixPoint.SOUTH | FixPoint.WEST,
            'nw': FixPoint.SOUTH | FixPoint.EAST,
            'se': FixPoint.NORTH | FixPoint.WEST,
            'sw': FixPoint.NORTH | FixPoint.EAST,
        }
        self._win.resize(target_width, target_height, anchors.get(anchor, FixPoint.NORTH | FixPoint.WEST))
        return {'limited': limited, 'width': target_width, 'height': target_height}
    def consume_size_limit_hint(self):
        pending = self._size_limit_pending
        self._size_limit_pending = False
        return pending
    def enable_resize(self):
        enable_native_resize()
        return True
    def toggle_maximize(self):
        if not self._win:
            return False
        if self._maximized:
            self._win.restore()
        else:
            self._win.maximize()
        self._maximized = not self._maximized
        time.sleep(0.08)
        apply_dwm_window_style()
        return self._maximized
    def fit_window(self):
        if not self._win:
            return False
        self._win.restore()
        self._maximized = False
        self._size_limit_pending = False
        self._win.resize(620, 850)
        return True
api = Api()

error_message = STARTUP_ERROR or server_error
window_url = f'http://127.0.0.1:{PORT}/simple.html'
if error_message:
    safe_error = error_message.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;').replace('\n', '<br>')
    window_url = ('<html><meta charset="utf-8"><body style="font-family:Maple Mono NF CN,Segoe UI Emoji,monospace;'
                  'background:#e8ecf1;padding:48px;color:#263238"><h2>应用启动失败</h2>'
                  f'<p style="line-height:1.8">{safe_error}</p><p>请关闭占用端口的程序或检查数据目录权限后重试。</p></body></html>')

window = webview.create_window(
    '考研英语二词汇',
    url=window_url,
    width=620,
    height=850,
    min_size=(500, 700),
    text_select=False,
    fullscreen=False,
    resizable=True,
    frameless=True,
    easy_drag=False,
    js_api=api,
    background_color='#e8ecf1'
)

api.set_win(window)

def apply_dwm_window_style():
    if sys.platform != 'win32' or not getattr(window, 'native', None):
        return
    hwnd = window.native.Handle.ToInt64()
    dwmapi = ctypes.windll.dwmapi
    dwmapi.DwmSetWindowAttribute.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_void_p, ctypes.c_uint]
    dwmapi.DwmSetWindowAttribute.restype = ctypes.c_long
    corner = ctypes.c_int(2)  # DWMWCP_ROUND
    no_border = ctypes.c_uint(0xFFFFFFFE)  # DWMWA_COLOR_NONE
    dwmapi.DwmSetWindowAttribute(hwnd, 33, ctypes.byref(corner), ctypes.sizeof(corner))
    dwmapi.DwmSetWindowAttribute(hwnd, 34, ctypes.byref(no_border), ctypes.sizeof(no_border))

_native_input_refs = []
_native_input_scheduled = False

def install_webview_input_overlays(*args):
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
            # 缩放方向：直接用 SetBounds 跟踪拖动
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
    _native_input_refs.extend((layout_timer, delayed_layout))
_native_window_configured = False

def enable_native_resize():
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
    _native_window_configured = True
window.events.shown += enable_native_resize
window.events.loaded += install_webview_input_overlays

webview.start()

if httpd:
    httpd.shutdown()
