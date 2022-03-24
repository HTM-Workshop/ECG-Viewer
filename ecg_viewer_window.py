# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'ecg_viewer_window.ui'
#
# Created by: PyQt5 UI code generator 5.14.1
#
# WARNING! All changes made in this file will be lost!


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setMinimumSize(QtCore.QSize(800, 600))
        MainWindow.setMaximumSize(QtCore.QSize(800, 600))
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graph = PlotWidget(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(10, 10, 781, 361))
        self.graph.setObjectName("graph")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 380, 781, 191))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout()
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.button_refresh = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_refresh.setMaximumSize(QtCore.QSize(16777215, 50))
        self.button_refresh.setObjectName("button_refresh")
        self.horizontalLayout_3.addWidget(self.button_refresh)
        self.button_connect = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_connect.setMaximumSize(QtCore.QSize(16777215, 50))
        self.button_connect.setObjectName("button_connect")
        self.horizontalLayout_3.addWidget(self.button_connect)
        self.gridLayout.addLayout(self.horizontalLayout_3, 4, 0, 1, 1)
        self.lcdNumber = QtWidgets.QLCDNumber(self.gridLayoutWidget)
        self.lcdNumber.setMinimumSize(QtCore.QSize(50, 115))
        self.lcdNumber.setObjectName("lcdNumber")
        self.gridLayout.addWidget(self.lcdNumber, 4, 1, 1, 1)
        self.port_combo_box = QtWidgets.QComboBox(self.gridLayoutWidget)
        self.port_combo_box.setObjectName("port_combo_box")
        self.gridLayout.addWidget(self.port_combo_box, 3, 0, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 3, 1, 1, 1)
        self.label_2 = QtWidgets.QLabel(self.gridLayoutWidget)
        self.label_2.setObjectName("label_2")
        self.gridLayout.addWidget(self.label_2, 2, 0, 1, 1)
        self.horizontalLayout = QtWidgets.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.show_track = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.show_track.setToolTip("")
        self.show_track.setToolTipDuration(60)
        self.show_track.setWhatsThis("")
        self.show_track.setObjectName("show_track")
        self.horizontalLayout.addWidget(self.show_track)
        self.button_reset = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_reset.setObjectName("button_reset")
        self.horizontalLayout.addWidget(self.button_reset)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 1, 1, 1)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.gridLayout.addItem(spacerItem, 0, 1, 1, 1)
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "ECG Viewer"))
        self.button_refresh.setText(_translate("MainWindow", "Refresh"))
        self.button_connect.setText(_translate("MainWindow", "Connect"))
        self.label.setText(_translate("MainWindow", "Approximate BPM"))
        self.label_2.setText(_translate("MainWindow", "Device:"))
        self.show_track.setText(_translate("MainWindow", "Show signal tracking"))
        self.button_reset.setText(_translate("MainWindow", "Reset Graph"))
from pyqtgraph import PlotWidget
