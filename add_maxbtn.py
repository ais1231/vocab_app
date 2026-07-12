# -*- coding: utf-8 -*-
with open(r'E:\code\vocab_app\simple.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 1. Add max-btn CSS
html = html.replace(
    '.min-btn.hide{display:none}\n.exit-btn{position:fixed;top:18px;right:18px',
    '.min-btn.hide{display:none}\n.max-btn{position:fixed;top:18px;right:66px;width:40px;height:40px;background:rgba(200,200,200,0.25);color:#888;border:none;border-radius:12px;cursor:pointer;font-size:18px;z-index:10000;display:flex;align-items:center;justify-content:center;transition:all 0.2s;backdrop-filter:blur(4px);border:1px solid rgba(0,0,0,0.06)}\n.max-btn:hover{background:rgba(76,175,80,0.12);color:#4CAF50;transform:scale(1.08)}\n.max-btn.hide{display:none}\n.exit-btn{position:fixed;top:18px;right:18px'
)

# 2. Add max-btn HTML
old = '<button class="min-btn" onclick="minimizeApp()" title="最小化">\u2212</button>\n<button class="exit-btn" onclick="exitApp()" title="退出应用">\u2715</button>'
new = '<button class="min-btn" onclick="minimizeApp()" title="最小化">\u2212</button>\n<button class="max-btn" id="maxBtn" onclick="maximizeApp()" title="最大化">\u25a1</button>\n<button class="exit-btn" onclick="exitApp()" title="退出应用">\u2715</button>'
html = html.replace(old, new)

# 3. Add maximizeApp function
old_fn = 'function minimizeApp(){\n    if(window.pywebview&&window.pywebview.api){\n        window.pywebview.api.minimize();\n    } else {\n        window.focus();window.blur();\n    }\n}'
new_fn = '''function minimizeApp(){
    if(window.pywebview&&window.pywebview.api){
        window.pywebview.api.minimize();
    } else {
        window.focus();window.blur();
    }
}

function maximizeApp(){
    var btn=document.getElementById('maxBtn');
    if(window.pywebview&&window.pywebview.api){
        if(btn.textContent==='\u25a1'){
            window.pywebview.api.maximize();
            btn.textContent='\u2750';
            btn.title='\u8fd8\u539f';
        } else {
            window.pywebview.api.restore();
            btn.textContent='\u25a1';
            btn.title='\u6700\u5927\u5316';
        }
    }
}'''
html = html.replace(old_fn, new_fn)

# 4. Update toggleSettings
html = html.replace(
    'document.querySelector(".min-btn").classList.toggle("hide", panel.classList.contains("show"));',
    'document.querySelector(".min-btn").classList.toggle("hide", panel.classList.contains("show"));\n    document.querySelector(".max-btn").classList.toggle("hide", panel.classList.contains("show"));'
)

with open(r'E:\code\vocab_app\simple.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
print('OK' if 'max-btn' in html else 'FAIL')
