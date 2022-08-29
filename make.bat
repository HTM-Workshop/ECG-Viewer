@echo off
pip3 install -r requirements.txt
pip3 install pyinstaller
pyinstaller --clean --window --onefile --icon=icon/icon.png ecg_viewer.py
