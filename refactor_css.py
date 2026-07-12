# -*- coding: utf-8 -*-
"""Rewrite CSS/HTML: win-btns container + drag-bar + elastic card layout"""

path = r'E:\code\vocab_app\simple.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# ===== CSS replacements =====

# 1) Body: remove -webkit-app-region:drag, set height:100vh, overflow:hidden
html = html.replace(
    'body{-webkit-app-region:drag;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:75px 20px 20px;background:#e8ecf1;min-height:100vh;display:flex;align-items:center;justify-content:center}',
    'body{font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:75px 20px 20px;background:#e8ecf1;height:100vh;overflow:hidden;display:flex;align-items:flex-start;justify-content:center}'
)

# 2) Replace individual button styles with win-btns container + shared button style
# Remove .exit-btn, .min-btn, .max-btn individual positioning and .hide variants
# Add .win-btns container style and .win-btn shared style
old_btns = (
    '.exit-btn{position:fixed;top:18px;right:18px;width:40px;height:40px;background:rgba(200,200,200,0.25);color:#888;border:none;border-radius:12px;cursor:pointer;font-size:22px;z-index:10000;display:flex;align-items:center;justify-content:center;transition:all 0.2s;backdrop-filter:blur(4px);border:1px solid rgba(0,0,0,0.06)}\n'
    '.exit-btn:hover{background:rgba(244,67,54,0.12);color:#e53935;transform:scale(1.08)}\n'
    '.exit-btn.hide{display:none}\n'
    '.min-btn{position:fixed;top:18px;right:114px;width:40px;height:40px;background:rgba(200,200,200,0.25);color:#888;border:none;border-radius:12px;cursor:pointer;font-size:22px;z-index:10000;display:flex;align-items:center;justify-content:center;transition:all 0.2s;backdrop-filter:blur(4px);border:1px solid rgba(0,0,0,0.06)}\n'
    '.min-btn:hover{background:rgba(33,150,243,0.12);color:#2196F3;transform:scale(1.08)}\n'
    '.min-btn.hide{display:none}\n'
    '.max-btn{position:fixed;top:18px;right:66px;width:40px;height:40px;background:rgba(200,200,200,0.25);color:#888;border:none;border-radius:12px;cursor:pointer;font-size:18px;z-index:10000;display:flex;align-items:center;justify-content:center;transition:all 0.2s;backdrop-filter:blur(4px);border:1px solid rgba(0,0,0,0.06)}\n'
    '.max-btn:hover{background:rgba(76,175,80,0.12);color:#4CAF50;transform:scale(1.08)}\n'
    '.max-btn.hide{display:none}'
)
new_btns = (
    '.win-btns{position:fixed;top:18px;right:18px;display:flex;gap:10px;z-index:10000;}\n'
    '.win-btns.hide{display:none}\n'
    '.win-btn{width:40px;height:40px;display:flex;align-items:center;justify-content:center;background:rgba(200,200,200,0.25);color:#888;border:none;border-radius:12px;cursor:pointer;font-size:22px;transition:all 0.2s;backdrop-filter:blur(4px);border:1px solid rgba(0,0,0,0.06)}\n'
    '.win-btn:hover{transform:scale(1.08)}\n'
    '.win-btn.exit:hover{background:rgba(244,67,54,0.12);color:#e53935}\n'
    '.win-btn.min:hover{background:rgba(33,150,243,0.12);color:#2196F3}\n'
    '.win-btn.max:hover{background:rgba(76,175,80,0.12);color:#4CAF50}\n'
    '.win-btn.max{font-size:18px}'
)
html = html.replace(old_btns, new_btns)

# 3) Card: flex column, height fills viewport
html = html.replace(
    '.card{background:white;border-radius:16px;padding:35px;margin:20px auto;max-width:550px;width:100%;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important}',
    '.card{background:white;border-radius:16px;padding:25px 35px;margin:70px auto 10px;max-width:520px;width:100%;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important;display:flex;flex-direction:column;flex:1;height:calc(100vh - 100px);overflow:hidden}'
)

# 4) Meaning area: flex:1, auto height
html = html.replace(
    '.meaning{font-size:20px;text-align:center;color:#333;padding:75px 20px 20px;background:#e8e8e8;border-radius:12px;height:200px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden}',
    '.meaning{font-size:20px;text-align:center;color:#333;padding:20px;background:#e8e8e8;border-radius:12px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden;flex:1;min-height:60px}'
)

# 5) Drag bar
html = html.replace(
    '.toast{position:fixed;bottom:40px;left:50%',
    '.drag-bar{position:fixed;top:0;left:0;width:100%;height:40px;-webkit-app-region:drag;z-index:9999}\n.toast{position:fixed;bottom:40px;left:50%'
)

# ===== HTML replacements =====

# 6) Replace individual buttons with win-btns container
old_html_btns = (
    '<button class="min-btn" onclick="minimizeApp()" title="最小化">\u2212</button>\n'
    '<button class="max-btn" id="maxBtn" onclick="maximizeApp()" title="\u6700\u5927\u5316">\u229e</button>\n'
    '<button class="exit-btn" onclick="exitApp()" title="\u9000\u51fa\u5e94\u7528">\u2715</button>'
)
new_html_btns = (
    '<div class="win-btns" id="winBtns">\n'
    '<button class="win-btn min" onclick="minimizeApp()" title="\u6700\u5c0f\u5316">\u2212</button>\n'
    '<button class="win-btn max" id="maxBtn" onclick="maximizeApp()" title="\u6700\u5927\u5316">\u229e</button>\n'
    '<button class="win-btn exit" onclick="exitApp()" title="\u9000\u51fa\u5e94\u7528">\u2715</button>\n'
    '</div>'
)
html = html.replace(old_html_btns, new_html_btns)

# 7) Add drag bar after body
html = html.replace(
    '<body>\n<div class="toast"',
    '<body>\n<div class="drag-bar"></div>\n<div class="toast"'
)

# ===== JS replacements =====

# 8) toggleSettings: use .win-btns instead of individual button hides
html = html.replace(
    '    document.querySelector(\'.exit-btn\').classList.toggle(\'hide\', panel.classList.contains(\'show\'));\n    document.querySelector(\'.min-btn\').classList.toggle(\'hide\', panel.classList.contains(\'show\'));\n    document.querySelector(\'.max-btn\').classList.toggle(\'hide\', panel.classList.contains(\'show\'));',
    '    document.querySelector(\'.win-btns\').classList.toggle(\'hide\', panel.classList.contains(\'show\'));'
)

# 9) Remove no-drag for old button classes, add .win-btns
html = html.replace(
    'input,select,textarea,.btn,.nbtn,.show-btn,.exit-btn,.min-btn,.max-btn,.settings-btn,.close-btn,.confirm-btn,.reset-btn,.mode-btn,.settings-mode-btn,.book-item,.save-btn,.remove-btn,.tab,.settings-panel,.reset-option,.keymap-input{-webkit-app-region:no-drag}',
    'input,select,textarea,.btn,.nbtn,.show-btn,.win-btn,.win-btns,.settings-btn,.close-btn,.confirm-btn,.reset-btn,.mode-btn,.settings-mode-btn,.book-item,.save-btn,.remove-btn,.tab,.settings-panel,.reset-option,.keymap-input{-webkit-app-region:no-drag}'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
print('OK checks:')
print(f'  win-btns: {html.count("win-btns")}')
print(f'  drag-bar: {html.count("drag-bar")}')
print(f'  flex:1 meaning: {"flex:1" in html}')
print(f'  calc card height: {"calc(100vh - 100px)" in html}')
print(f'  overflow:hidden body: {"height:100vh;overflow:hidden" in html}')
