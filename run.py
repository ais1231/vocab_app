import http.server
import socketserver
import os
import webbrowser
import threading
import time
import json

os.chdir(os.path.dirname(os.path.abspath(__file__)))

PORT = 9000

# 数据文件路径
DATA_DIR = 'D:\\vocab_app_data'
DATA_FILE = os.path.join(DATA_DIR, 'vocab_save.json')

# 确保目录存在
os.makedirs(DATA_DIR, exist_ok=True)

class VocabHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # 禁用日志
    
    def do_GET(self):
        # API: 读取数据
        if self.path == '/api/load':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
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
        super().do_GET()
    
    def do_POST(self):
        # API: 保存数据
        if self.path == '/api/save':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            try:
                data = json.loads(post_data.decode('utf-8'))
                # 读取现有数据
                existing_data = {}
                if os.path.exists(DATA_FILE):
                    with open(DATA_FILE, 'r', encoding='utf-8-sig') as f:
                        existing_data = json.load(f)
                
                # 如果是平铺格式，转换为v1.0格式
                if 'vocab_book_kaoyan' in data or 'vocab_progress_kaoyan' in data:
                    if 'books' not in existing_data:
                        existing_data = {'version': '1.0', 'books': {}}
                    
                    # 提取book IDs
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
                        
                        # 更新state
                        state_key = 'vocab_book_' + book_id
                        if state_key in data:
                            state_data = json.loads(data[state_key]) if isinstance(data[state_key], str) else data[state_key]
                            existing_data['books'][book_id]['state'] = state_data
                        
                        # 更新progress
                        progress_key = 'vocab_progress_' + book_id
                        if progress_key in data:
                            progress_data = json.loads(data[progress_key]) if isinstance(data[progress_key], str) else data[progress_key]
                            existing_data['books'][book_id]['progress'] = progress_data
                            # 同时更新state.S
                            if 'state' not in existing_data['books'][book_id]:
                                existing_data['books'][book_id]['state'] = {}
                            existing_data['books'][book_id]['state']['S'] = progress_data
                        
                        # 更新unlearned
                        unlearned_key = 'vocab_unlearned_' + book_id
                        if unlearned_key in data:
                            unlearned_data = json.loads(data[unlearned_key]) if isinstance(data[unlearned_key], str) else data[unlearned_key]
                            existing_data['books'][book_id]['unlearned'] = unlearned_data
                    
                    # 更新currentBook
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
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()

Handler = VocabHandler

print("=" * 40)
print("  考研词汇背单词")
print("=" * 40)
print(f"\n服务器: http://127.0.0.1:{PORT}")
print(f"数据目录: {DATA_DIR}")
print("\n按 Ctrl+C 停止")
print("=" * 40)

class ThreadedTCPServer(socketserver.ThreadingMixIn, socketserver.TCPServer):
    allow_reuse_address = True

with ThreadedTCPServer(("127.0.0.1", PORT), Handler) as httpd:
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")
