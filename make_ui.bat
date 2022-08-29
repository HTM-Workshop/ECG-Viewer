@echo off
pip3 install -r requirements.txt
pyuic5 ecg_viewer_window.ui > ecg_viewer_window.py
pyuic5 about.ui > about.py
pyuic5 license.ui > license.ui