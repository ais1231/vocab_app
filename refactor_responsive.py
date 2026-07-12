# -*- coding: utf-8 -*-
"""Rewrite layout: body flex center + responsive vw/vh + JS drag via API + resize handle"""

path = r'E:\code\vocab_app\simple.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# ===== 1) CSS: body, card, meaning =====

# Body: flex center, 100vh, no scroll
old_body = 'body{font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:0;background:#e8ecf1;width:100vw;height:100vh;overflow:hidden}'
new_body = 'body{font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:0;background:#e8ecf1;width:100vw;height:100vh;overflow:hidden;display:flex;align-items:center;justify-content:center}'
html = html.replace(old_body, new_body)

# Remove #scaleContainer CSS (no longer using transform)
html = html.replace('#scaleContainer{transform-origin:top left;position:absolute;top:50px;left:50%}\nbody{font-family:', 'body{font-family:')

# Card: responsive width/height
old_card = '.card{background:white;border-radius:16px;padding:25px 35px;margin:0 auto;width:600px;min-height:650px;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important}'
new_card = '.card{background:white;border-radius:16px;padding:2.5vh 3vw;margin:0 auto;width:min(70vw,650px);max-height:min(75vh,750px);box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important;overflow:hidden}'
html = html.replace(old_card, new_card)

# Meaning: responsive vh height
old_meaning = '.meaning{font-size:20px;text-align:center;color:#333;padding:20px;background:#e8e8e8;border-radius:12px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden;height:250px}'
new_meaning = '.meaning{font-size:clamp(14px,2vw,20px);text-align:center;color:#333;padding:1.5vh 2vw;background:#e8e8e8;border-radius:12px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden;height:clamp(120px,30vh,300px)}'
html = html.replace(old_meaning, new_meaning)

# Word: responsive font
html = html.replace('.word{font-size:48px', '.word{font-size:clamp(28px,5vw,52px)')
html = html.replace('.show-btn{display:block;margin:10px auto;padding:10px 30px', '.show-btn{display:block;margin:1.5vh auto;padding:1.2vh 3vw')
# Make show-btn font responsive
html = html.replace('.show-btn{display:block;margin:1.5vh auto;padding:1.2vh 3vw;background:#2196F3;color:white;border:none;border-radius:25px;cursor:pointer;font-size:16px', '.show-btn{display:block;margin:1.5vh auto;padding:1.2vh 3vw;background:#2196F3;color:white;border:none;border-radius:25px;cursor:pointer;font-size:clamp(12px,1.6vw,16px)')

# Buttons: responsive padding
html = html.replace('.btn{flex:1;padding:15px', '.btn{flex:1;padding:1.2vh')
html = html.replace(';border:none;border-radius:12px;font-size:16px;cursor:pointer', ';border:none;border-radius:12px;font-size:clamp(12px,1.6vw,16px);cursor:pointer')

# Navigation buttons
html = html.replace('.nbtn{flex:1;padding:12px', '.nbtn{flex:1;padding:1vh')
html = html.replace('.btns{display:flex;gap:10px;margin-top:20px}', '.btns{display:flex;gap:1vw;margin-top:1.5vh}')
html = html.replace('.nav{display:flex;gap:10px;margin-top:15px}', '.nav{display:flex;gap:1vw;margin-top:1.5vh}')

# Settings button: responsive size
html = html.replace('.settings-btn{position:absolute;top:15px;right:15px;width:36px;height:36px', '.settings-btn{position:absolute;top:1.5vh;right:1.5vw;width:clamp(28px,4vw,40px);height:clamp(28px,4vw,40px)')

# Progress info: responsive
html = html.replace('.progress-info{text-align:center;margin:10px 0;color:#666;font-size:14px}', '.progress-info{text-align:center;margin:1vh 0;color:#666;font-size:clamp(11px,1.4vw,14px)}')

# ===== 2) Add resize handle CSS =====
html = html.replace(
    '.toast{position:fixed;bottom:40px;left:50%',
    '.resize-handle{position:fixed;bottom:0;right:0;width:20px;height:20px;cursor:nwse-resize;z-index:99999}\n.resize-handle::after{content:"";position:absolute;bottom:4px;right:4px;width:12px;height:12px;border-right:2px solid #aaa;border-bottom:2px solid #aaa;border-radius:0 0 3px 0}\n.toast{position:fixed;bottom:40px;left:50%'
)

# ===== 3) Remove old scaleContainer wrapping =====
# Unwrap card from scaleContainer
html = html.replace('<div id="scaleContainer">\n<div class="card">', '<div class="card">')
# Remove the extra closing div
html = html.replace('</div>\n</div>\n</div>\n\n<div class="settings-panel" id="settingsPanel">', '\n</div>\n\n<div class="settings-panel" id="settingsPanel">')

# ===== 4) Replace drag-bar with JS-based drag =====
# Remove -webkit-app-region:drag from drag-bar
html = html.replace(
    '.drag-bar{position:fixed;top:0;left:0;width:100%;height:40px;-webkit-app-region:drag;z-index:9999}',
    '.drag-bar{position:fixed;top:0;left:0;width:100%;height:40px;z-index:9999;cursor:move}'
)

# Replace -webkit-app-region:no-drag line
html = html.replace(
    'input,select,textarea,.btn,.nbtn,.show-btn,.win-btn,.win-btns,.settings-btn,.close-btn,.confirm-btn,.reset-btn,.mode-btn,.settings-mode-btn,.book-item,.save-btn,.remove-btn,.tab,.settings-panel,.reset-option,.keymap-input{-webkit-app-region:no-drag}',
    '.win-btns,.settings-panel,.modal,.confirm-overlay{z-index:10001!important}'
)

# ===== 5) Replace resizeApp + init with drag/resize JS =====
# Remove old resizeApp function
old_js = '// 等比例缩放\nfunction resizeApp(){\n    var w=window.innerWidth,h=window.innerHeight;\n    var baseW=700,baseH=850;\n    var sx=w/baseW,sy=(h-50)/baseH;\n    var s=Math.min(sx,sy,1.5);\n    var c=document.getElementById(\'scaleContainer\');\n    if(c){c.style.transform=\'scale(\'+s+\')\';c.style.marginLeft=(-baseW*s/2)+\'px\';}\n}\nwindow.addEventListener(\'resize\',resizeApp);'

new_js = '''// 窗口拖拽（通过后端 API 移动窗口）
var _dragging=false,_dx=0,_dy=0;
document.addEventListener('mousedown',function(e){
    if(!e.target.closest('.drag-bar'))return;
    _dragging=true;_dx=e.screenX;_dy=e.screenY;
    e.preventDefault();
});
document.addEventListener('mousemove',function(e){
    if(!_dragging)return;
    var ndx=e.screenX-_dx,ndy=e.screenY-_dy;
    _dx=e.screenX;_dy=e.screenY;
    if(window.pywebview&&window.pywebview.api){
        try{pywebview.api.move_window(ndx,ndy);}catch(ex){}
    }
});
document.addEventListener('mouseup',function(){_dragging=false;});'''

html = html.replace(old_js, new_js)

# ===== 6) Add resize handle JS =====
html = html.replace(
    '// 数据同步已移除（单机场景不需要轮询覆盖状态）',
    '// 右下角缩放手柄\nvar _resizing=false,_rx=0,_ry=0,_rw=0,_rh=0;\n(function(){var h=document.getElementById(\'resizeHandle\')||function(){\nvar el=document.createElement(\'div\');el.className=\'resize-handle\';el.id=\'resizeHandle\';document.body.appendChild(el);\nel.addEventListener(\'mousedown\',function(e){\n_resizing=true;_rx=e.screenX;_ry=e.screenY;\n_rw=window.innerWidth;_rh=window.innerHeight;e.preventDefault();\n});\n}();})();\ndocument.addEventListener(\'mousemove\',function(e){\nif(!_resizing)return;\nvar ndx=e.screenX-_rx,ndy=e.screenY-_ry;\nvar nw=Math.max(500,_rw+ndx),nh=Math.max(400,_rh+ndy);\nif(window.pywebview&&window.pywebview.api){\ntry{pywebview.api.resize_window(nw,nh);}catch(ex){}}\n});\ndocument.addEventListener(\'mouseup\',function(){_resizing=false;});\n\n// 数据同步已移除（单机场景不需要轮询覆盖状态）'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
