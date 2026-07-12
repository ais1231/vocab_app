# -*- coding: utf-8 -*-
import re

# Fix simple.html: add max-btn CSS
with open(r'E:\code\vocab_app\simple.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace(
    '.min-btn.hide{display:none}\r\n.settings-panel{',
    '.min-btn.hide{display:none}\r\n.max-btn{position:fixed;top:18px;right:66px;width:40px;height:40px;background:rgba(200,200,200,0.25);color:#888;border:none;border-radius:12px;cursor:pointer;font-size:18px;z-index:10000;display:flex;align-items:center;justify-content:center;transition:all 0.2s;backdrop-filter:blur(4px);border:1px solid rgba(0,0,0,0.06)}\r\n.max-btn:hover{background:rgba(76,175,80,0.12);color:#4CAF50;transform:scale(1.08)}\r\n.max-btn.hide{display:none}\r\n.settings-panel{'
)

with open(r'E:\code\vocab_app\simple.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('simple.html: max-btn count =', html.count('max-btn'))

# Fix main_desktop.py: add minimize/maximize/restore API methods
with open(r'E:\code\vocab_app\main_desktop.py', 'r', encoding='utf-8') as f:
    py = f.read()

if 'def minimize' not in py:
    api_block = '''
    def minimize(self):
        try:
            import win32gui
            hwnd = win32gui.FindWindow(None, "考研词汇")
            if hwnd:
                win32gui.ShowWindow(hwnd, 6)
        except:
            pass

    def maximize(self):
        try:
            import win32gui
            hwnd = win32gui.FindWindow(None, "考研词汇")
            if hwnd:
                win32gui.ShowWindow(hwnd, 3)
        except:
            pass

    def restore(self):
        try:
            import win32gui
            hwnd = win32gui.FindWindow(None, "考研词汇")
            if hwnd:
                win32gui.ShowWindow(hwnd, 9)
        except:
            pass

'''
    py = py.replace('    def exit(self):', api_block + '    def exit(self):')
    with open(r'E:\code\vocab_app\main_desktop.py', 'w', encoding='utf-8') as f:
        f.write(py)
    print('main_desktop.py: added minimize/maximize/restore')
else:
    print('main_desktop.py: already has minimize')
