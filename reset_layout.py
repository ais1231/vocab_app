# -*- coding: utf-8 -*-
"""Revert layout to original. Keep functional JS changes. Add minimal win-btns + drag-bar."""
path = r'E:\code\vocab_app\simple.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# ===== 1) Body back to original =====
html = html.replace(
    'body{font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:0;background:#e8ecf1;width:100vw;height:100vh;overflow:hidden;display:flex;align-items:center;justify-content:center}',
    'body{font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:20px;background:#e8ecf1;min-height:100vh;display:flex;align-items:center;justify-content:center}'
)

# ===== 2) Card back to original =====
html = html.replace(
    '.card{background:white;border-radius:16px;padding:2.5vh 3vw;margin:0 auto;width:min(70vw,650px);max-height:min(75vh,750px);box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important;overflow:hidden}',
    '.card{background:white;border-radius:16px;padding:35px;margin:20px auto;max-width:550px;width:100%;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important}'
)

# ===== 3) Meaning back to original =====
html = html.replace(
    '.meaning{font-size:clamp(14px,2vw,20px);text-align:center;color:#333;padding:1.5vh 2vw;background:#e8e8e8;border-radius:12px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden;height:clamp(120px,30vh,300px)}',
    '.meaning{font-size:20px;text-align:center;color:#333;padding:20px;background:#e8e8e8;border-radius:12px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden;height:200px}'
)

# ===== 4) Word font back =====
html = html.replace('clamp(28px,5vw,52px)', '48px')

# ===== 5) Show-btn back =====
html = html.replace(
    '.show-btn{display:block;margin:1.5vh auto;padding:1.2vh 3vw;background:#2196F3;color:white;border:none;border-radius:25px;cursor:pointer;font-size:clamp(12px,1.6vw,16px)}',
    '.show-btn{display:block;margin:10px auto;padding:10px 30px;background:#2196F3;color:white;border:none;border-radius:25px;cursor:pointer;font-size:16px;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500}'
)

# ===== 6) Buttons back =====
html = html.replace('.btns{display:flex;gap:1vw;margin-top:1.5vh}', '.btns{display:flex;gap:10px;margin-top:20px}')
html = html.replace('.nav{display:flex;gap:1vw;margin-top:1.5vh}', '.nav{display:flex;gap:10px;margin-top:15px}')
html = html.replace('.btn{flex:1;padding:1.2vh', '.btn{flex:1;padding:15px')
html = html.replace(';border:none;border-radius:12px;font-size:clamp(12px,1.6vw,16px);cursor:pointer', ';border:none;border-radius:12px;font-size:16px;cursor:pointer')
html = html.replace('.nbtn{flex:1;padding:1vh', '.nbtn{flex:1;padding:12px')
html = html.replace('.progress-info{text-align:center;margin:1vh 0;color:#666;font-size:clamp(11px,1.4vw,14px)}', '.progress-info{text-align:center;margin:10px 0;color:#666;font-size:14px}')

# ===== 7) Settings-btn back =====
html = html.replace('width:clamp(28px,4vw,40px);height:clamp(28px,4vw,40px)', 'width:36px;height:36px')
html = html.replace('top:1.5vh;right:1.5vw', 'top:15px;right:15px')

# ===== 8) Remove scaleContainer =====
html = html.replace('<div id="scaleContainer">\n<div class="card">', '<div class="card">')
html = html.replace('</div>\n</div>\n</div>\n\n<div class="settings-panel"', '\n</div>\n\n<div class="settings-panel"')

# ===== 9) Remove resize-handle CSS =====
html = html.replace('.resize-handle{position:fixed;bottom:0;right:0;width:20px;height:20px;cursor:nwse-resize;z-index:99999}\n.resize-handle::after{content:"";position:absolute;bottom:4px;right:4px;width:12px;height:12px;border-right:2px solid #aaa;border-bottom:2px solid #aaa;border-radius:0 0 3px 0}\n', '')

# ===== 10) Remove JS drag/resize code =====
import re
html = re.sub(
    r'// 窗口拖拽[\s\S]*?document\.addEventListener\(\'mouseup\',function\(\)\{_dragging=false;\}\);',
    '',
    html,
    count=1
)
html = re.sub(
    r'// 右下角缩放手柄[\s\S]*?document\.addEventListener\(\'mouseup\',function\(\)\{_resizing=false;\}\);',
    '',
    html,
    count=1
)

# ===== 11) Fix drag-bar to use -webkit-app-region =====
html = html.replace(
    '.drag-bar{position:fixed;top:0;left:0;width:100%;height:40px;z-index:9999;cursor:move}',
    '.drag-bar{position:fixed;top:0;left:0;width:100%;height:40px;-webkit-app-region:drag;z-index:9999}'
)

# ===== 12) Restore no-drag line =====
html = html.replace(
    '.win-btns,.settings-panel,.modal,.confirm-overlay{z-index:10001!important}',
    'input,select,textarea,.btn,.nbtn,.show-btn,.win-btn,.win-btns,.settings-btn,.close-btn,.confirm-btn,.reset-btn,.mode-btn,.settings-mode-btn,.book-item,.save-btn,.remove-btn,.tab,.settings-panel,.reset-option,.keymap-input{-webkit-app-region:no-drag}'
)

# ===== 13) Settings-panel padding back =====
html = html.replace('padding:75px 20px 20px}', 'padding:20px}')

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
# Verify
print('body original:', b'padding:20px;background:#e8ecf1;min-height:100vh' in html)
print('card original:', b'max-width:550px;width:100%' in html)
print('meaning original:', b'height:200px' in html)
print('no resize-handle:', b'resize-handle' not in html)
print('no scaleContainer:', b'scaleContainer' not in html)
print('no drag JS:', b'_dragging' not in html)
print('webkit drag:', b'-webkit-app-region:drag' in html)
print('no-drag line:', b'-webkit-app-region:no-drag' in html)
print('settings padding:', b'padding:20px}' in html[html.find(b'settings-panel{'):html.find(b'settings-panel')+250])
