@echo off
type ecg_viewer.py > ecg_viewer.pyw
pip3 install -r requirements.txt
pip3 install pyinstaller
pyuic5 ecg_viewer_window.ui > ecg_viewer_window.py
pyuic5 about.ui > about.py
pyuic5 license.ui > license.ui
pyinstaller --clean --onefile --icon=icon/icon.png ecg_viewer.pyw
del /f /q ecg_viewer.pyw
