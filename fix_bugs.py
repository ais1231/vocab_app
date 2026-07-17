# -*- coding: utf-8 -*-
"""Apply all bug fixes for resize lag + limit hint."""

import re

# ===== main_desktop.py fixes =====
with open(r'E:\code\vocab_app\main_desktop.py', 'r', encoding='utf-8') as f:
    py = f.read()

# Fix 1: down() - set _native_resize_active = True
old_down = '''        def down(sender, event):
            if event.Button != WinForms.MouseButtons.Left:
                return
            cursor = WinForms.Cursor.Position
            state.update(active=True, direction=direction, cursor_x=cursor.X, cursor_y=cursor.Y,
                         left=form.Left, top=form.Top, width=form.Width, height=form.Height,
                         limit_notified=False)
            panel.Capture = True'''

new_down = '''        def down(sender, event):
            if event.Button != WinForms.MouseButtons.Left:
                return
            global _native_resize_active
            _native_resize_active = True
            cursor = WinForms.Cursor.Position
            state.update(active=True, direction=direction, cursor_x=cursor.X, cursor_y=cursor.Y,
                         left=form.Left, top=form.Top, width=form.Width, height=form.Height,
                         limit_notified=False)
            panel.Capture = True'''
py = py.replace(old_down, new_down)

# Fix 1b: up() - clear _native_resize_active
old_up = '''        def up(sender, event):
            if event.Button == WinForms.MouseButtons.Left:
                state['active'] = False
                panel.Capture = False'''
new_up = '''        def up(sender, event):
            if event.Button == WinForms.MouseButtons.Left:
                global _native_resize_active
                _native_resize_active = False
                state['active'] = False
                panel.Capture = False'''
py = py.replace(old_up, new_up)

# Fix 1c: layout() - skip BringToFront + SetWindowPos during resize
old_layout = '''    def layout(sender=None, event=None):
        width = max(host.ClientSize.Width, form.ClientSize.Width, form.Width)
        height = max(host.ClientSize.Height, form.ClientSize.Height, form.Height)
        edge = 8
        panels['drag'].SetBounds(edge, edge+6, max(0, width-126), 30)
        panels['n'].SetBounds(edge, 0, max(0, width-edge*2), edge)
        panels['s'].SetBounds(edge, max(0, height-edge*2), max(0, width-edge*2), edge)
        panels['w'].SetBounds(0, edge, edge, max(0, height-edge*2))
        panels['e'].SetBounds(max(0, width-edge*2), edge, edge, max(0, height-edge*2))
        panels['nw'].SetBounds(0, 0, edge+3, edge+3)
        panels['ne'].SetBounds(max(0, width-edge*2-3), 0, edge+3, edge+3)
        panels['sw'].SetBounds(0, max(0, height-edge*2-3), edge+3, edge+3)
        panels['se'].SetBounds(max(0, width-edge*2-3), max(0, height-edge*2-3), edge+3, edge+3)
        for name in panels:
            panels[name].BringToFront()
            user32.SetWindowPos(panels[name].Handle.ToInt64(), 0, 0, 0, 0, 0, 0x0013)'''

new_layout = '''    def layout(sender=None, event=None):
        global _native_resize_active
        width = max(host.ClientSize.Width, form.ClientSize.Width, form.Width)
        height = max(host.ClientSize.Height, form.ClientSize.Height, form.Height)
        edge = 8
        panels['drag'].SetBounds(edge, edge+6, max(0, width-126), 30)
        panels['n'].SetBounds(edge, 0, max(0, width-edge*2), edge)
        panels['s'].SetBounds(edge, max(0, height-edge*2), max(0, width-edge*2), edge)
        panels['w'].SetBounds(0, edge, edge, max(0, height-edge*2))
        panels['e'].SetBounds(max(0, width-edge*2), edge, edge, max(0, height-edge*2))
        panels['nw'].SetBounds(0, 0, edge+3, edge+3)
        panels['ne'].SetBounds(max(0, width-edge*2-3), 0, edge+3, edge+3)
        panels['sw'].SetBounds(0, max(0, height-edge*2-3), edge+3, edge+3)
        panels['se'].SetBounds(max(0, width-edge*2-3), max(0, height-edge*2-3), edge+3, edge+3)
        # resize 期间跳过 BringToFront/SetWindowPos（只在非拖拽时校正 Z 序）
        if not _native_resize_active:
            for name in panels:
                panels[name].BringToFront()
                user32.SetWindowPos(panels[name].Handle.ToInt64(), 0, 0, 0, 0, 0, 0x0013)'''

py = py.replace(old_layout, new_layout)

with open(r'E:\code\vocab_app\main_desktop.py', 'w', encoding='utf-8') as f:
    f.write(py)

print('main_desktop.py: fixes applied')

# ===== simple.html fixes =====
with open(r'E:\code\vocab_app\simple.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Fix 2 (H4): Add .catch() to promise chain
old_poll = '''window.pywebview.api.consume_size_limit_hint().then(function(pending){if(pending)showSizeLimitHint();}).finally(function(){sizeLimitPollBusy=false;});'''
new_poll = '''window.pywebview.api.consume_size_limit_hint().then(function(pending){if(pending)showSizeLimitHint();}).catch(function(){}).finally(function(){sizeLimitPollBusy=false;});'''
html = html.replace(old_poll, new_poll)

# Fix 3 (H5): Make showSizeLimitHint safe against exceptions
old_hint = '''function showSizeLimitHint(){
    var hint=document.getElementById('sizeLimitToast');
    clearTimeout(sizeLimitTimer);
    hint.classList.remove('show');
    void hint.offsetWidth;
    hint.classList.add('show');
    sizeLimitTimer=setTimeout(function(){hint.classList.remove('show');},1500);
}'''
new_hint = '''function showSizeLimitHint(){
    try{
        var hint=document.getElementById('sizeLimitToast');
        if(!hint)return;
        clearTimeout(sizeLimitTimer);
        hint.classList.remove('show');
        void hint.offsetWidth;
        hint.classList.add('show');
        sizeLimitTimer=setTimeout(function(){hint.classList.remove('show');},1500);
    }catch(e){}
}'''
html = html.replace(old_hint, new_hint)

with open(r'E:\code\vocab_app\simple.html', 'w', encoding='utf-8') as f:
    f.write(html)

print('simple.html: fixes applied')
print('Done')
