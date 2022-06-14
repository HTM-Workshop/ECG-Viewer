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
        MainWindow.resize(800, 761)
        MainWindow.setMinimumSize(QtCore.QSize(800, 734))
        MainWindow.setMaximumSize(QtCore.QSize(800, 761))
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("../../../../.designer/backup/icons8-heart-monitor-100.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        MainWindow.setWindowIcon(icon)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.graph = PlotWidget(self.centralwidget)
        self.graph.setGeometry(QtCore.QRect(10, 10, 571, 421))
        self.graph.setObjectName("graph")
        self.gridLayoutWidget = QtWidgets.QWidget(self.centralwidget)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 440, 781, 161))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.lcdNumber = QtWidgets.QLCDNumber(self.gridLayoutWidget)
        self.lcdNumber.setMinimumSize(QtCore.QSize(50, 115))
        self.lcdNumber.setFrameShape(QtWidgets.QFrame.Panel)
        self.lcdNumber.setFrameShadow(QtWidgets.QFrame.Plain)
        self.lcdNumber.setObjectName("lcdNumber")
        self.gridLayout.addWidget(self.lcdNumber, 3, 1, 1, 1)
        self.label = QtWidgets.QLabel(self.gridLayoutWidget)
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setObjectName("label")
        self.gridLayout.addWidget(self.label, 2, 1, 1, 1)
        self.verticalLayout_2 = QtWidgets.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.gridLayout.addLayout(self.verticalLayout_2, 1, 0, 1, 1)
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
        self.button_run = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_run.setObjectName("button_run")
        self.horizontalLayout.addWidget(self.button_run)
        self.button_export = QtWidgets.QPushButton(self.gridLayoutWidget)
        self.button_export.setObjectName("button_export")
        self.horizontalLayout.addWidget(self.button_export)
        self.gridLayout.addLayout(self.horizontalLayout, 2, 0, 1, 1)
        self.frame = QtWidgets.QFrame(self.gridLayoutWidget)
        self.frame.setFrameShape(QtWidgets.QFrame.Panel)
        self.frame.setObjectName("frame")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.frame)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.gridLayout_2 = QtWidgets.QGridLayout()
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.button_connect = QtWidgets.QPushButton(self.frame)
        self.button_connect.setMaximumSize(QtCore.QSize(16777215, 50))
        self.button_connect.setObjectName("button_connect")
        self.gridLayout_2.addWidget(self.button_connect, 4, 1, 1, 1)
        self.button_refresh = QtWidgets.QPushButton(self.frame)
        self.button_refresh.setMaximumSize(QtCore.QSize(16777215, 50))
        self.button_refresh.setObjectName("button_refresh")
        self.gridLayout_2.addWidget(self.button_refresh, 4, 0, 1, 1)
        self.port_combo_box = QtWidgets.QComboBox(self.frame)
        self.port_combo_box.setObjectName("port_combo_box")
        self.gridLayout_2.addWidget(self.port_combo_box, 3, 0, 1, 2)
        self.label_2 = QtWidgets.QLabel(self.frame)
        self.label_2.setObjectName("label_2")
        self.gridLayout_2.addWidget(self.label_2, 2, 0, 1, 2)
        self.horizontalLayout_3.addLayout(self.gridLayout_2)
        self.gridLayout.addWidget(self.frame, 3, 0, 1, 1)
        self.gridFrame_2 = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame_2.setGeometry(QtCore.QRect(10, 610, 261, 90))
        self.gridFrame_2.setFrameShape(QtWidgets.QFrame.Box)
        self.gridFrame_2.setObjectName("gridFrame_2")
        self.gridLayout_3 = QtWidgets.QGridLayout(self.gridFrame_2)
        self.gridLayout_3.setObjectName("gridLayout_3")
        self.high_limit_box = QtWidgets.QSpinBox(self.gridFrame_2)
        self.high_limit_box.setMinimum(85)
        self.high_limit_box.setMaximum(150)
        self.high_limit_box.setProperty("value", 120)
        self.high_limit_box.setObjectName("high_limit_box")
        self.gridLayout_3.addWidget(self.high_limit_box, 1, 1, 1, 1)
        self.label_3 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_3.setObjectName("label_3")
        self.gridLayout_3.addWidget(self.label_3, 0, 0, 1, 1)
        self.label_4 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_4.setObjectName("label_4")
        self.gridLayout_3.addWidget(self.label_4, 1, 0, 1, 1)
        self.label_5 = QtWidgets.QLabel(self.gridFrame_2)
        self.label_5.setObjectName("label_5")
        self.gridLayout_3.addWidget(self.label_5, 2, 0, 1, 1)
        self.low_limit_box = QtWidgets.QSpinBox(self.gridFrame_2)
        self.low_limit_box.setMinimum(15)
        self.low_limit_box.setMaximum(70)
        self.low_limit_box.setProperty("value", 40)
        self.low_limit_box.setObjectName("low_limit_box")
        self.gridLayout_3.addWidget(self.low_limit_box, 2, 1, 1, 1)
        self.alarm_window = QtWidgets.QFrame(self.centralwidget)
        self.alarm_window.setGeometry(QtCore.QRect(280, 610, 511, 91))
        self.alarm_window.setStyleSheet("QFrame { background-color: red }")
        self.alarm_window.setFrameShape(QtWidgets.QFrame.StyledPanel)
        self.alarm_window.setFrameShadow(QtWidgets.QFrame.Raised)
        self.alarm_window.setObjectName("alarm_window")
        self.alarm_text = QtWidgets.QLabel(self.alarm_window)
        self.alarm_text.setGeometry(QtCore.QRect(10, 10, 491, 71))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.alarm_text.setFont(font)
        self.alarm_text.setScaledContents(True)
        self.alarm_text.setAlignment(QtCore.Qt.AlignCenter)
        self.alarm_text.setObjectName("alarm_text")
        self.gridFrame_21 = QtWidgets.QFrame(self.centralwidget)
        self.gridFrame_21.setGeometry(QtCore.QRect(590, 40, 201, 391))
        self.gridFrame_21.setFrameShape(QtWidgets.QFrame.Box)
        self.gridFrame_21.setObjectName("gridFrame_21")
        self.gridLayout_4 = QtWidgets.QGridLayout(self.gridFrame_21)
        self.gridLayout_4.setObjectName("gridLayout_4")
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_8 = QtWidgets.QLabel(self.gridFrame_21)
        self.label_8.setObjectName("label_8")
        self.verticalLayout.addWidget(self.label_8)
        self.holdoff_box = QtWidgets.QSpinBox(self.gridFrame_21)
        self.holdoff_box.setMaximum(300)
        self.holdoff_box.setSingleStep(10)
        self.holdoff_box.setProperty("value", 150)
        self.holdoff_box.setObjectName("holdoff_box")
        self.verticalLayout.addWidget(self.holdoff_box)
        self.label_9 = QtWidgets.QLabel(self.gridFrame_21)
        self.label_9.setObjectName("label_9")
        self.verticalLayout.addWidget(self.label_9)
        self.prominence_box = QtWidgets.QSpinBox(self.gridFrame_21)
        self.prominence_box.setProperty("value", 20)
        self.prominence_box.setObjectName("prominence_box")
        self.verticalLayout.addWidget(self.prominence_box)
        spacerItem = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout.addItem(spacerItem)
        self.gridLayout_4.addLayout(self.verticalLayout, 0, 0, 1, 1)
        self.verticalLayout_3 = QtWidgets.QVBoxLayout()
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.label_10 = QtWidgets.QLabel(self.gridFrame_21)
        self.label_10.setObjectName("label_10")
        self.verticalLayout_3.addWidget(self.label_10)
        self.window_length_box = QtWidgets.QSpinBox(self.gridFrame_21)
        self.window_length_box.setMaximum(299)
        self.window_length_box.setSingleStep(2)
        self.window_length_box.setProperty("value", 99)
        self.window_length_box.setObjectName("window_length_box")
        self.verticalLayout_3.addWidget(self.window_length_box)
        self.label_11 = QtWidgets.QLabel(self.gridFrame_21)
        self.label_11.setObjectName("label_11")
        self.verticalLayout_3.addWidget(self.label_11)
        self.polyorder_box = QtWidgets.QSpinBox(self.gridFrame_21)
        self.polyorder_box.setProperty("value", 5)
        self.polyorder_box.setObjectName("polyorder_box")
        self.verticalLayout_3.addWidget(self.polyorder_box)
        spacerItem1 = QtWidgets.QSpacerItem(20, 40, QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)
        self.verticalLayout_3.addItem(spacerItem1)
        self.autoinvert_checkbox = QtWidgets.QCheckBox(self.gridFrame_21)
        self.autoinvert_checkbox.setEnabled(True)
        self.autoinvert_checkbox.setChecked(True)
        self.autoinvert_checkbox.setObjectName("autoinvert_checkbox")
        self.verticalLayout_3.addWidget(self.autoinvert_checkbox)
        self.button_force_invert = QtWidgets.QPushButton(self.gridFrame_21)
        self.button_force_invert.setObjectName("button_force_invert")
        self.verticalLayout_3.addWidget(self.button_force_invert)
        self.label_7 = QtWidgets.QLabel(self.gridFrame_21)
        self.label_7.setObjectName("label_7")
        self.verticalLayout_3.addWidget(self.label_7)
        self.graph_zoom_slider = QtWidgets.QSlider(self.gridFrame_21)
        self.graph_zoom_slider.setMinimum(0)
        self.graph_zoom_slider.setMaximum(99)
        self.graph_zoom_slider.setSingleStep(1)
        self.graph_zoom_slider.setProperty("value", 66)
        self.graph_zoom_slider.setOrientation(QtCore.Qt.Horizontal)
        self.graph_zoom_slider.setInvertedAppearance(True)
        self.graph_zoom_slider.setInvertedControls(False)
        self.graph_zoom_slider.setTickPosition(QtWidgets.QSlider.NoTicks)
        self.graph_zoom_slider.setObjectName("graph_zoom_slider")
        self.verticalLayout_3.addWidget(self.graph_zoom_slider)
        self.gridLayout_4.addLayout(self.verticalLayout_3, 1, 0, 1, 1)
        self.label_6 = QtWidgets.QLabel(self.centralwidget)
        self.label_6.setGeometry(QtCore.QRect(590, 10, 201, 17))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.label_6.setFont(font)
        self.label_6.setAlignment(QtCore.Qt.AlignCenter)
        self.label_6.setObjectName("label_6")
        self.label_12 = QtWidgets.QLabel(self.centralwidget)
        self.label_12.setGeometry(QtCore.QRect(10, 710, 781, 20))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.label_12.setFont(font)
        self.label_12.setAlignment(QtCore.Qt.AlignCenter)
        self.label_12.setObjectName("label_12")
        MainWindow.setCentralWidget(self.centralwidget)
        self.statusBar = QtWidgets.QStatusBar(MainWindow)
        self.statusBar.setObjectName("statusBar")
        MainWindow.setStatusBar(self.statusBar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "DIYECG Viewer "))
        self.label.setText(_translate("MainWindow", "Approximate BPM"))
        self.show_track.setText(_translate("MainWindow", "Show signal tracking"))
        self.button_reset.setText(_translate("MainWindow", "Reset"))
        self.button_run.setText(_translate("MainWindow", "Stop"))
        self.button_export.setText(_translate("MainWindow", "Export"))
        self.button_connect.setText(_translate("MainWindow", "Connect"))
        self.button_refresh.setText(_translate("MainWindow", "Refresh"))
        self.label_2.setText(_translate("MainWindow", "Device:"))
        self.label_3.setText(_translate("MainWindow", "Alarm Control:"))
        self.label_4.setText(_translate("MainWindow", "High Limit:"))
        self.label_5.setText(_translate("MainWindow", "Low Limit:"))
        self.alarm_text.setText(_translate("MainWindow", "RATE ALARM"))
        self.label_8.setText(_translate("MainWindow", "PD - Holdoff"))
        self.label_9.setText(_translate("MainWindow", "PD - Prominence"))
        self.label_10.setText(_translate("MainWindow", "Filtering Window Length"))
        self.label_11.setText(_translate("MainWindow", "Filtering Polyorder"))
        self.autoinvert_checkbox.setText(_translate("MainWindow", "Auto Invert"))
        self.button_force_invert.setText(_translate("MainWindow", "Force Invert"))
        self.label_7.setText(_translate("MainWindow", "Vertical Zoom"))
        self.label_6.setText(_translate("MainWindow", "Advanced Controls"))
        self.label_12.setText(_translate("MainWindow", "This program is for educational purposes only. NOT FOR MEDICAL USE."))
from pyqtgraph import PlotWidget
