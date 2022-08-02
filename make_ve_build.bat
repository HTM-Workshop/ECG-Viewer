@echo off
pip install virtualenv
type ecg_viewer.py > ecg_viewer.pyw
virtualenv ecg_viewer_build
ecg_viewer_build\Scripts\pip.exe install -r requirements.txt
ecg_viewer_build\Scripts\pip.exe install pyinstaller
ecg_viewer_build\Scripts\pyuic5.exe ecg_viewer_window.ui > ecg_viewer_window.py
ecg_viewer_build\Scripts\pyinstaller.exe --clean --onefile --icon=icon/icon.png ecg_viewer.pyw
del /f /q ecg_viewer.pyw
