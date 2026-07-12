# -*- coding: utf-8 -*-

# === Read files ===
with open(r'E:\code\vocab_app\main_desktop.py', 'r', encoding='utf-8') as f:
    py = f.read()
with open(r'E:\code\vocab_app\simple.html', 'r', encoding='utf-8') as f:
    html = f.read()

# === main_desktop.py ===

# 1. frameless=True
py = py.replace(
    '    fullscreen=True,\n',
    '    fullscreen=True,\n    frameless=True,\n'
)

# 2. toggle_maximize instead of maximize+restore
py = py.replace(
    '    def maximize(self):\n        try:\n            if self._win:\n                self._win.toggle_fullscreen()\n        except:\n            pass\n\n    def restore(self):\n        try:\n            if self._win:\n                self._win.restore()\n        except:\n            pass',
    '    def toggle_maximize(self):\n        try:\n            if self._win:\n                self._win.toggle_fullscreen()\n        except:\n            pass'
)

with open(r'E:\code\vocab_app\main_desktop.py', 'w', encoding='utf-8') as f:
    f.write(py)
print('main_desktop.py done')

# === simple.html ===

# 1. Body drag region
html = html.replace(
    'body{font-family',
    'body{-webkit-app-region:drag;font-family'
)

# 2. No-drag on interactive elements (before the button:focus rule)
html = html.replace(
    'button:focus{outline:none}\n',
    'button:focus{outline:none}\ninput,select,textarea,.btn,.nbtn,.show-btn,.exit-btn,.min-btn,.max-btn,.settings-btn,.close-btn,.confirm-btn,.reset-btn,.mode-btn,.settings-mode-btn,.book-item,.save-btn,.remove-btn,.tab,.settings-panel,.reset-option,.keymap-input{-webkit-app-region:no-drag}\n'
)

# 3. Fix maximizeApp - remove icon toggle
old = 'function maximizeApp(){\n    var btn=document.getElementById(\'maxBtn\');\n    if(window.pywebview&&window.pywebview.api){\n        if(btn.textContent===\'\u229e\'){\n            window.pywebview.api.maximize();\n            btn.textContent=\'\u229f\';\n            btn.title=\'\u8fd8\u539f\';\n        } else {\n            window.pywebview.api.restore();\n            btn.textContent=\'\u229e\';\n            btn.title=\'\u6700\u5927\u5316\';\n        }\n    }\n}'
new = 'function maximizeApp(){\n    if(window.pywebview&&window.pywebview.api){\n        window.pywebview.api.toggle_maximize();\n    }\n}'
html = html.replace(old, new)

# 4. Add max-btn to toggleSettings
html = html.replace(
    'document.querySelector(\'.min-btn\').classList.toggle(\'hide\', panel.classList.contains(\'show\'));',
    'document.querySelector(\'.min-btn\').classList.toggle(\'hide\', panel.classList.contains(\'show\'));\n    document.querySelector(\'.max-btn\').classList.toggle(\'hide\', panel.classList.contains(\'show\'));'
)

with open(r'E:\code\vocab_app\simple.html', 'w', encoding='utf-8') as f:
    f.write(html)
print('simple.html done')
print('OK')
