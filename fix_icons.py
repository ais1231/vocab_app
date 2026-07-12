# -*- coding: utf-8 -*-
import os

path = r'E:\code\vocab_app\simple.html'
with open(path, 'rb') as f:
    d = f.read()

# □ (white square) -> ⊞ (squared plus) for maximize
# ❐ (restore symbol) -> ⊟ (squared minus) for restore

# HTML button text
old1 = '>\u25a1</button>'.encode('utf-8')  # □
new1 = '>\u229e</button>'.encode('utf-8')   # ⊞

# JS textContent check
old2 = "textContent==='\u25a1'".encode('utf-8')
new2 = "textContent==='\u229e'".encode('utf-8')

# JS assignment
old3 = "btn.textContent='\u25a1';".encode('utf-8')
new3 = "btn.textContent='\u229e';".encode('utf-8')

# Restore symbol
old4 = "btn.textContent='\u2750';".encode('utf-8')  # ❐
new4 = "btn.textContent='\u229f';".encode('utf-8')   # ⊟

print(f'old1 found: {old1 in d}')
print(f'old2 found: {old2 in d}')
print(f'old3 found: {old3 in d}')
print(f'old4 found: {old4 in d}')

if old1 in d:
    d = d.replace(old1, new1)
if old2 in d:
    d = d.replace(old2, new2)
if old3 in d:
    d = d.replace(old3, new3)
if old4 in d:
    d = d.replace(old4, new4)

with open(path, 'wb') as f:
    f.write(d)

# Verify
print(f'new1 count: {d.count(new1)}')
print(f'new4 count: {d.count(new4)}')
