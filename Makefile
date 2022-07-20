all:
	pyinstaller --clean --onefile ecg_viewer.py*
clean:
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm -rf profile
	rm -f *.bin
	rm -f *.spec
rebuild:
	make clean
	make build-ui
	make
build-ui:
	pyuic5 ecg_viewer_window.ui > ecg_viewer_window.py
