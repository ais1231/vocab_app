# -*- coding: utf-8 -*-
import re

# ===== main_desktop.py: 改用 win32gui 控制全屏 =====
with open(r'E:\code\vocab_app\main_desktop.py', 'r', encoding='utf-8') as f:
    py = f.read()

# Replace create_window - use frameless=True, remove fullscreen=True
old_win = '''window = webview.create_window(
    '考研英语二词汇',
    url=f'http://127.0.0.1:{PORT}/simple.html',
    width=700,
    height=900,
    min_size=(500, 600),
    text_select=False,
    fullscreen=True,
    frameless=True,
    js_api=api,
    background_color='#e8ecf1'
)'''

new_win = '''window = webview.create_window(
    '考研英语二词汇',
    url=f'http://127.0.0.1:{PORT}/simple.html',
    width=800,
    height=920,
    min_size=(500, 600),
    text_select=False,
    frameless=True,
    js_api=api,
    background_color='#e8ecf1'
)'''

py = py.replace(old_win, new_win)

# Replace toggle_maximize with win32gui approach
old_api = '''    def toggle_maximize(self):
        try:
            if self._win:
                self._win.toggle_fullscreen()
        except:
            pass'''

new_api = '''    _maximized = False
    _normal_rect = None

    def toggle_maximize(self):
        try:
            import win32gui, win32con
            hwnd = win32gui.FindWindow(None, "考研英语二词汇")
            if not hwnd:
                return
            if self._maximized:
                # 还原
                if self._normal_rect:
                    win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
                    x,y,w,h = self._normal_rect
                    win32gui.SetWindowPos(hwnd, 0, x, y, w, h, win32con.SWP_NOZORDER)
                self._maximized = False
            else:
                # 保存当前窗口位置
                x,y,w,h = win32gui.GetWindowRect(hwnd)
                self._normal_rect = (x,y,w-x,h-y)
                # 最大化到屏幕尺寸
                monitor = win32gui.MonitorFromWindow(hwnd, 2)
                mi = win32gui.GetMonitorInfo(monitor)
                work_area = mi['rcMonitor']
                win32gui.SetWindowPos(hwnd, 0,
                    work_area[0], work_area[1],
                    work_area[2]-work_area[0], work_area[3]-work_area[1],
                    win32con.SWP_NOZORDER)
                self._maximized = True
        except:
            pass'''

py = py.replace(old_api, new_api)

# Add win32gui win32con to imports if not there
with open(r'E:\code\vocab_app\main_desktop.py', 'w', encoding='utf-8') as f:
    f.write(py)

print('main_desktop.py: updated')

# ===== simple.html: fix overlap =====
with open(r'E:\code\vocab_app\simple.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add padding-top to body to prevent overlap with top-right buttons
# Buttons occupy top ~18px to ~66px (18px offset + 40px height + 8px gap)
# Push card below buttons
html = html.replace(
    'body{font-family',
    'body{padding-top:75px;font-family'
)

# But keep the original padding value - remove the existing padding:20px
# Actually the body already has padding set in the style. Let me check the current body style.
# Current: body{font-family...;margin:0;padding:20px;...}
# I need to change padding:20px to padding:75px 20px 20px

html = html.replace(
    'padding:20px;',
    'padding:75px 20px 20px;'
)

with open(r'E:\code\vocab_app\simple.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('simple.html: body padding-top 75px')
print('OK')
