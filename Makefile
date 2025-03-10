.ONESHELL:

# Get operating system
UNAME_S := $(shell uname -s)

all:
	make install-reqs
	pip3 install pyinstaller
	@if [ "$(UNAME_S)" = "Darwin" ]; then \
		PYINSTALLER_FLAG="--onedir"; \
	else \
		PYINSTALLER_FLAG="--onefile"; \
	fi; \
	python3 -m PyInstaller --name="ECG Viewer" --windowed --clean $$PYINSTALLER_FLAG --icon=icon/icon.png ecg_viewer.py*

clean:
	rm -rf build
	rm -rf __pycache__
	rm -f *.bin
	rm -f *.spec
	rm -f ECG_*.png
	rm -f *csv
	rm -rf .mypy_cache

clean-all:
	rm -f *.spec
	make clean
	rm -rf dist

rebuild:
	make clean
	make

build-ui:
	pyuic5 ecg_viewer_window.ui > ecg_viewer_window.py
	pyuic5 about.ui > about.py
	pyuic5 license.ui > license.py

ve-build:
	pip3 install virtualenv --user
	virtualenv ecg_viewer_build
	. ./ecg_viewer_build/bin/activate
	make install-reqs
	make rebuild
	deactivate

ve-delete:
	rm -rf ecg_viewer_build

install-reqs:
	pip3 install -r requirements.txt --user

build-icon:
	pyrcc5 -o images_qr.py images.qrc
