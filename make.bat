@echo off
type ecg_viewer.py > ecg_viewer.pyw
pip3 install -r requirements.txt
pip3 install pyinstaller pyqt5-tools Pillow
pyuic5 ecg_viewer_window.ui > ecg_viewer_window.py
pyrcc5 -o images_qr.py images.qrc
pyinstaller --clean --onefile --icon=icon/icon.png ecg_viewer.pyw
del /f /q ecg_viewer.pyw
