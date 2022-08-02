.ONESHELL:
all:
	make install-reqs
	make build-ui
	pip3 install pyinstaller
	pyinstaller --windowed --clean --onedir --icon=icon/icon.png ecg_viewer.py*
clean:
	rm -rf build
	rm -rf __pycache__
	rm -f *.bin
	rm -f *.spec
clean-all:
	rm -f *.spec
	make clean
	rm -rf dist
rebuild:
	make clean
	make
build-ui:
	pyuic5 ecg_viewer_window.ui > ecg_viewer_window.py
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
