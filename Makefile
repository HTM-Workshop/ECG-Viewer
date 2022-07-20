.ONESHELL:
all:
	pyinstaller --clean --onefile ecg_viewer.py*
clean:
	rm -rf build
	rm -rf __pycache__
	rm -rf profile
	rm -f *.bin
	rm -f *.spec
clean-all:
	make clean
	rm -rf dist
rebuild:
	make clean
	make build-ui
	make
build-ui:
	pyuic5 ecg_viewer_window.ui > ecg_viewer_window.py
ve-build:
	virtualenv ecg_viewer_build
	. ./ecg_viewer_build/bin/activate
	make install-reqs
	make rebuild
	deactivate
ve-delete:
	rm -rf ecg_viewer_build
install-reqs:
	pip3 install -r requirements.txt
	pip3 install pyinstaller
