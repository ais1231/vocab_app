# -*- coding: utf-8 -*-
"""Wrap card in #scaleContainer + resizeApp() for proportional scaling."""

path = r'E:\code\vocab_app\simple.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

# 1) Add scaleContainer CSS before .card
html = html.replace(
    'body{font-family:',
    '#scaleContainer{transform-origin:top left;position:absolute;top:50px;left:50%}\nbody{font-family:'
)

# 2) Reset card to fixed-size design (800x920 base), no flex/calc
html = html.replace(
    '.card{background:white;border-radius:16px;padding:25px 35px;margin:70px auto 10px;max-width:520px;width:100%;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important;display:flex;flex-direction:column;flex:1;height:calc(100vh - 100px);overflow:hidden}',
    '.card{background:white;border-radius:16px;padding:25px 35px;margin:0 auto;width:600px;min-height:650px;box-shadow:0 2px 10px rgba(0,0,0,0.1);position:relative!important}'
)

# 3) Reset meaning - remove flex:1, restore fixed height
html = html.replace(
    '.meaning{font-size:20px;text-align:center;color:#333;padding:20px;background:#e8e8e8;border-radius:12px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden;flex:1;min-height:60px}',
    '.meaning{font-size:20px;text-align:center;color:#333;padding:20px;background:#e8e8e8;border-radius:12px;overflow-y:auto;white-space:pre-line;line-height:1.8;font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:500;visibility:hidden;height:250px}'
)

# 4) Remove the old body height/overflow that conflicts
html = html.replace(
    'body{font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:75px 20px 20px;background:#e8ecf1;height:100vh;overflow:hidden;display:flex;align-items:flex-start;justify-content:center}',
    'body{font-family:\'Montserrat\',\'Microsoft YaHei\',sans-serif;font-weight:400;margin:0;padding:0;background:#e8ecf1;width:100vw;height:100vh;overflow:hidden}'
)

# 5) Wrap card in #scaleContainer
html = html.replace(
    '<div class="win-btns" id="winBtns">\n<button class="win-btn min" onclick="minimizeApp()" title="最小化">\u2212</button>\n<button class="win-btn max" id="maxBtn" onclick="maximizeApp()" title="最大化">\u229e</button>\n<button class="win-btn exit" onclick="exitApp()" title="退出应用">\u2715</button>\n</div>\n<div class="settings-panel"',
    '<div class="win-btns" id="winBtns">\n<button class="win-btn min" onclick="minimizeApp()" title="最小化">\u2212</button>\n<button class="win-btn max" id="maxBtn" onclick="maximizeApp()" title="最大化">\u229e</button>\n<button class="win-btn exit" onclick="exitApp()" title="退出应用">\u2715</button>\n</div>\n<div id="scaleContainer">\n<div class="card">'
)

# 6) Close scaleContainer before settings-panel
html = html.replace(
    '</div>\n</div>\n\n<div class="settings-panel" id="settingsPanel">',
    '</div>\n</div>\n</div>\n\n<div class="settings-panel" id="settingsPanel">'
)

# 7) Add resizeApp() function + window resize listener
html = html.replace(
    '// 数据同步已移除（单机场景不需要轮询覆盖状态）\n\n// 已在文件开头通过electronStorage.loadFromDisk加载',
    '// 等比例缩放\nfunction resizeApp(){\n    var w=window.innerWidth,h=window.innerHeight;\n    var baseW=700,baseH=850;\n    var sx=w/baseW,sy=(h-50)/baseH;\n    var s=Math.min(sx,sy,1.5);\n    var c=document.getElementById(\'scaleContainer\');\n    if(c){c.style.transform=\'scale(\'+s+\')\';c.style.marginLeft=(-baseW*s/2)+\'px\';}\n}\nwindow.addEventListener(\'resize\',resizeApp);\n\n// 数据同步已移除（单机场景不需要轮询覆盖状态）\n\n// 已在文件开头通过electronStorage.loadFromDisk加载'
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print('Done')
print('scaleContainer:', html.count('scaleContainer'))
print('resizeApp:', 'resizeApp' in html)
print('card class:', html.count('<div class="card">'))
