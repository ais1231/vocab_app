@echo off
cd /d "%~dp0"
start "" http://127.0.0.1:9000/simple.html
python run.py
