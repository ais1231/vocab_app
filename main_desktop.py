import webview
import threading
import http.server
import socketserver
import os
import json
import time
import sys
import urllib.request

if getattr(sys, 'frozen', False):
    os.chdir(os.path.dirname(sys.executable))
    BASE_DIR = sys._MEIPASS
else:
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

PORT = 19000
DATA_DIR = 'D:\\vocab_app_data'
DATA_FILE = os.path.join(DATA_DIR, 'vocab_save.json')
os.makedirs(DATA_DIR, exist_ok=True)

with open(os.path.join(BASE_DIR, 'simple.html'), 'r', encoding='utf-8') as f:
    _SIMPLE_HTML = f.read()

# 注入loading遮罩到simple.html的<body>标签后
_LOADING_INJECT = '''
<div id="pywebviewLoading" style="position:fixed;top:0;left:0;width:100%;height:100%;background:#e8ecf1;z-index:99999;display:flex;justify-content:center;align-items:center;font-family:'Microsoft YaHei',sans-serif">
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

def start_server():
    handler = VocabHandler
    with ThreadedTCPServer(("127.0.0.1", PORT), handler) as httpd:
        httpd.serve_forever()

server_thread = threading.Thread(target=start_server, daemon=True)
server_thread.start()

for _ in range(200):
    try:
        urllib.request.urlopen(f'http://127.0.0.1:{PORT}/api/load', timeout=0.1)
        break
    except:
        time.sleep(0.05)

class Api:
    def __init__(self):
        self._win = None
    def set_win(self, win):
        self._win = win
    def exit(self):
        try:
            if self._win:
                self._win.hide()
        except:
            pass
        os._exit(0)

api = Api()

window = webview.create_window(
    '考研英语二词汇',
    url=f'http://127.0.0.1:{PORT}/simple.html',
    width=700,
    height=900,
    min_size=(500, 600),
    text_select=False,
    fullscreen=True,
    js_api=api,
    background_color='#e8ecf1'
)

api.set_win(window)

webview.start()
