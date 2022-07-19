all:
	pyinstaller --clean --onefile ecg_viewer.py*
clean:
	rm -rf dist
	rm -rf build
	rm -rf __pycache__
	rm -rf profile
rebuild:
	make clean
	make
