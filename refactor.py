"""Refactor: remove var decls + App proxy + remove checkDataSync"""
import re

path = r'E:\code\vocab_app\simple.html'
with open(path, 'r', encoding='utf-8') as f:
    html = f.read()

script_start = html.index('<script>') + len('<script>')
script_end = html.index('</script>')
js = html[script_start:script_end]

# ========== Part 1: Remove checkDataSync ==========
# Remove the function
js = re.sub(
    r'\n// 实时同步 - 每2秒检查数据变化.*?(?=\n// 已在文件开头通过)',
    '\n// 数据同步已移除',
    js,
    count=1,
    flags=re.DOTALL
)
# Remove var lastDataHash
js = re.sub(r'\n\s*var lastDataHash\s*=\s*[^;]+;', '\n', js)

print("Part 1 done: checkDataSync removed")

# ========== Part 2: Remove var declarations for globals ==========
GLOBALS = [
    'currentWordClicked', 'wordsSinceLastReview', 'defaultKeyMapping',
    'unlearnedWords', 'saveFileHandle', 'unknownQueue', 'fuzzyQueue',
    'startLetter', 'randomList', 'coreList', 'shownWords', 'keyMapping',
    'currentBook', 'bookList', 'saveMode', 'marked',
    'mode', 'D', 'L', 'I', 'S',
]

saved = {}
# For each global, find and remove var declaration, save value
# Use r'' raw strings for regex
for var in GLOBALS:
    # Match: optional whitespace + var + whitespace + name + whitespace + = + whitespace + value + ; + newline
    p = re.compile(
        r'(\n\s*)var\s+' + re.escape(var) + r'\s*=\s*([^;]+?);\s*(\n|$)',
        re.DOTALL
    )
    m = p.search(js)
    if m:
        val = m.group(2).strip()
        saved[var] = val
        js = js[:m.start()] + m.group(1) + m.group(3)  # keep newline spacing
        print(f"  Removed var {var}")
    else:
        print(f"  WARNING: var {var} not found!")

# ========== Part 3: Inject App proxy after first JS line ==========
# Build _map content
map_entries = []
for var, val in saved.items():
    map_entries.append(f'        {var}: {val},')
map_str = '\n'.join(map_entries)

PROXY = f'''
// ===== App 状态容器 =====
var App = {{}};
(function() {{
    try {{
        var _map = {{
{map_str}
        }};
        for (var k in _map) {{ App[k] = _map[k]; }}
        for (var k in _map) {{
            (function(key) {{
                Object.defineProperty(window, key, {{
                    get: function() {{ return App[key]; }},
                    set: function(v) {{ App[key] = v; }},
                    configurable: true, enumerable: true
                }});
            }})(k);
        }}
    }} catch(e) {{ console.error('App init error:', e); }}
}})();

'''

# Insert right before the first comment line
insert_pt = js.index('// 统一数据存储层')
js = js[:insert_pt] + PROXY + js[insert_pt:]

html = html[:script_start] + js + html[script_end:]

# Fix onclick in HTML that uses unlearnedWords directly
html = html.replace(
    "Object.keys(unlearnedWords).length",
    "Object.keys(App.unlearnedWords).length"
)

with open(path, 'w', encoding='utf-8') as f:
    f.write(html)

print("Part 2+3 done: App proxy injected")
print(f"  Variables: {list(saved.keys())}")
