from asyncio.windows_events import NULL
from ctypes.wintypes import HKEY
from pyexpat import version_info
import time
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore, QtGui, QtWidgets
import win32api
import win32gui
import win32con
import win32process
import psutil
import ctypes
import threading
from hook import my_hook
import csv

version = 1 # -1是6.4状态修正版 0是6.4，1是6.3mp+ 2是6.3 3是6.2 4是6.1 
#-1 是圣三
len_war = 0x24
addr_war = 0x4B2C50
cnt_wo = 15
cnt_you = 20
cnt_di = 80
cnt_item = 154
addr_tianfu = 0x5089B0
addr_zhuanshu = 0x50E800
addr_bisha = 0x511800
life = b'\xE0\x92\x40\x00'
condition_change = False  #star在6.4修正版中 修改了状态的内存约定

lock_list = []
lock_hp = []
lock_mp = []
auto_life = False

class myTextEdit(QtWidgets.QTextEdit):
    def __init__(self,parent):
        super(myTextEdit, self).__init__(parent)
        #绑定textchanged事件
        self.textChanged.connect(self.handleTextChanged)

    def handleTextChanged(self):
        tmp = self.toPlainText()
        res = ''.join(filter(str.isdigit, tmp))
        if res != tmp:
            self.setPlainText(res)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(700, 530)
        MainWindow.setFixedSize(MainWindow.width(), MainWindow.height())
        self.font = QtGui.QFont()
        self.font.setFamily("宋体")
        self.font.setPointSize(18)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.frame = QtWidgets.QFrame(self.centralwidget)
        self.frame.setGeometry(QtCore.QRect(9, 77, 681, 389))
        self.frame.setFrameShape(QtWidgets.QFrame.Box)
        self.frame.setFrameShadow(QtWidgets.QFrame.Raised)
        self.frame.setObjectName("frame")
        self.widget_1 = QtWidgets.QWidget(self.frame)
        self.widget_1.setEnabled(True)
        self.widget_1.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_1.setObjectName("widget_1")
        self.checkBox_1 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_1.setGeometry(QtCore.QRect(20, 38, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_1.setFont(font)
        self.checkBox_1.setAutoFillBackground(False)
        self.checkBox_1.setObjectName("checkBox_1")
        self.checkBox_2 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_2.setGeometry(QtCore.QRect(20, 74, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_2.setFont(font)
        self.checkBox_2.setAutoFillBackground(False)
        self.checkBox_2.setObjectName("checkBox_2")
        self.checkBox_3 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_3.setGeometry(QtCore.QRect(20, 110, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_3.setFont(font)
        self.checkBox_3.setAutoFillBackground(False)
        self.checkBox_3.setObjectName("checkBox_3")
        self.checkBox_4 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_4.setGeometry(QtCore.QRect(20, 146, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_4.setFont(font)
        self.checkBox_4.setAutoFillBackground(False)
        self.checkBox_4.setObjectName("checkBox_4")
        self.checkBox_5 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_5.setGeometry(QtCore.QRect(20, 182, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_5.setFont(font)
        self.checkBox_5.setAutoFillBackground(False)
        self.checkBox_5.setObjectName("checkBox_5")
        self.checkBox_6 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_6.setGeometry(QtCore.QRect(20, 218, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_6.setFont(font)
        self.checkBox_6.setAutoFillBackground(False)
        self.checkBox_6.setObjectName("checkBox_6")
        self.checkBox_7 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_7.setGeometry(QtCore.QRect(20, 254, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_7.setFont(font)
        self.checkBox_7.setAutoFillBackground(False)
        self.checkBox_7.setObjectName("checkBox_7")
        self.checkBox_8 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_8.setGeometry(QtCore.QRect(20, 290, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_8.setFont(font)
        self.checkBox_8.setAutoFillBackground(False)
        self.checkBox_8.setObjectName("checkBox_8")
        self.checkBox_9 = QtWidgets.QCheckBox(self.widget_1)
        self.checkBox_9.setGeometry(QtCore.QRect(20, 326, 171, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        self.checkBox_9.setFont(font)
        self.checkBox_9.setAutoFillBackground(False)
        self.checkBox_9.setObjectName("checkBox_9")
        self.widget_2 = QtWidgets.QWidget(self.frame)
        self.widget_2.setEnabled(True)
        self.widget_2.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_2.setObjectName("widget_2")
        self.listview_data = QtWidgets.QListWidget(self.widget_2)
        self.listview_data.setGeometry(QtCore.QRect(10, 13, 140, 365))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.listview_data.setFont(font)
        self.listview_data.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.listview_data.setFrameShape(QtWidgets.QFrame.Panel)
        self.listview_data.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.listview_data.setLineWidth(2)
        self.listview_data.setAutoScroll(True)
        self.listview_data.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview_data.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listview_data.setObjectName("listview_data")
        self.data_1 = QtWidgets.QLabel(self.widget_2)
        self.data_1.setGeometry(QtCore.QRect(165, 13, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_1.setFont(font)
        self.data_1.setStyleSheet("color:rgb(0,0,0);")
        self.data_1.setObjectName("data_1")
        self.data_input_1 = myTextEdit(self.widget_2)
        self.data_input_1.setGeometry(QtCore.QRect(230, 12, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_1.setFont(font)
        self.data_input_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_1.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_1.setLineWidth(2)
        self.data_input_1.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_1.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_1.setObjectName("data_input_1")
        self.data_2 = QtWidgets.QLabel(self.widget_2)
        self.data_2.setGeometry(QtCore.QRect(165, 48, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_2.setFont(font)
        self.data_2.setStyleSheet("color:rgb(0,0,0);")
        self.data_2.setObjectName("data_2")
        self.data_input_2 = myTextEdit(self.widget_2)
        self.data_input_2.setGeometry(QtCore.QRect(230, 47, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_2.setFont(font)
        self.data_input_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_2.setLineWidth(2)
        self.data_input_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_2.setObjectName("data_input_2")
        self.data_input_3 = myTextEdit(self.widget_2)
        self.data_input_3.setGeometry(QtCore.QRect(230, 82, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_3.setFont(font)
        self.data_input_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_3.setLineWidth(2)
        self.data_input_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_3.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_3.setObjectName("data_input_3")
        self.data_3 = QtWidgets.QLabel(self.widget_2)
        self.data_3.setGeometry(QtCore.QRect(165, 83, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_3.setFont(font)
        self.data_3.setStyleSheet("color:rgb(0,0,0);")
        self.data_3.setObjectName("data_3")
        self.data_input_4 = myTextEdit(self.widget_2)
        self.data_input_4.setGeometry(QtCore.QRect(230, 117, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_4.setFont(font)
        self.data_input_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_4.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_4.setLineWidth(2)
        self.data_input_4.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_4.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_4.setObjectName("data_input_4")
        self.data_4 = QtWidgets.QLabel(self.widget_2)
        self.data_4.setGeometry(QtCore.QRect(165, 118, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_4.setFont(font)
        self.data_4.setStyleSheet("color:rgb(0,0,0);")
        self.data_4.setObjectName("data_4")
        self.data_5 = QtWidgets.QLabel(self.widget_2)
        self.data_5.setGeometry(QtCore.QRect(165, 153, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_5.setFont(font)
        self.data_5.setStyleSheet("color:rgb(0,0,0);")
        self.data_5.setObjectName("data_5")
        self.data_input_5 = myTextEdit(self.widget_2)
        self.data_input_5.setGeometry(QtCore.QRect(230, 152, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_5.setFont(font)
        self.data_input_5.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_5.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_5.setLineWidth(2)
        self.data_input_5.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_5.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_5.setObjectName("data_input_5")
        self.data_6 = QtWidgets.QLabel(self.widget_2)
        self.data_6.setGeometry(QtCore.QRect(165, 188, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_6.setFont(font)
        self.data_6.setStyleSheet("color:rgb(0,0,0);")
        self.data_6.setObjectName("data_6")
        self.data_input_6 = myTextEdit(self.widget_2)
        self.data_input_6.setGeometry(QtCore.QRect(230, 187, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_6.setFont(font)
        self.data_input_6.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_6.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_6.setLineWidth(2)
        self.data_input_6.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_6.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_6.setObjectName("data_input_6")
        self.data_input_7 = myTextEdit(self.widget_2)
        self.data_input_7.setGeometry(QtCore.QRect(230, 222, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_7.setFont(font)
        self.data_input_7.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_7.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_7.setLineWidth(2)
        self.data_input_7.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_7.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_7.setObjectName("data_input_7")
        self.data_7 = QtWidgets.QLabel(self.widget_2)
        self.data_7.setGeometry(QtCore.QRect(165, 223, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_7.setFont(font)
        self.data_7.setStyleSheet("color:rgb(0,0,0);")
        self.data_7.setObjectName("data_7")
        self.data_input_8 = myTextEdit(self.widget_2)
        self.data_input_8.setGeometry(QtCore.QRect(230, 257, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_8.setFont(font)
        self.data_input_8.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_8.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_8.setLineWidth(2)
        self.data_input_8.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_8.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_8.setObjectName("data_input_8")
        self.data_8 = QtWidgets.QLabel(self.widget_2)
        self.data_8.setGeometry(QtCore.QRect(165, 258, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_8.setFont(font)
        self.data_8.setStyleSheet("color:rgb(0,0,0);")
        self.data_8.setObjectName("data_8")
        self.data_input_9 = myTextEdit(self.widget_2)
        self.data_input_9.setGeometry(QtCore.QRect(230, 292, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_9.setFont(font)
        self.data_input_9.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_9.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_9.setLineWidth(2)
        self.data_input_9.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_9.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_9.setObjectName("data_input_9")
        self.data_9 = QtWidgets.QLabel(self.widget_2)
        self.data_9.setGeometry(QtCore.QRect(165, 293, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_9.setFont(font)
        self.data_9.setStyleSheet("color:rgb(0,0,0);")
        self.data_9.setObjectName("data_9")
        self.data_input_10 = myTextEdit(self.widget_2)
        self.data_input_10.setGeometry(QtCore.QRect(230, 327, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_10.setFont(font)
        self.data_input_10.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_10.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_10.setLineWidth(2)
        self.data_input_10.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_10.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_10.setObjectName("data_input_10")
        self.data_10 = QtWidgets.QLabel(self.widget_2)
        self.data_10.setGeometry(QtCore.QRect(165, 328, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_10.setFont(font)
        self.data_10.setStyleSheet("color:rgb(0,0,0);")
        self.data_10.setObjectName("data_10")
        self.data_11 = QtWidgets.QLabel(self.widget_2)
        self.data_11.setGeometry(QtCore.QRect(270, 13, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_11.setFont(font)
        self.data_11.setStyleSheet("color:rgb(0,0,0);")
        self.data_11.setObjectName("data_11")
        self.data_input_11 = QtWidgets.QCheckBox(self.widget_2)
        self.data_input_11.setGeometry(QtCore.QRect(336, 14, 91, 19))
        self.data_input_11.setText("")
        self.data_input_11.setChecked(False)
        self.data_input_11.setObjectName("data_input_11")
        self.data_input_12 = myTextEdit(self.widget_2)
        self.data_input_12.setGeometry(QtCore.QRect(335, 47, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_12.setFont(font)
        self.data_input_12.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_12.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_12.setLineWidth(2)
        self.data_input_12.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_12.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_12.setObjectName("data_input_12")
        self.data_12 = QtWidgets.QLabel(self.widget_2)
        self.data_12.setGeometry(QtCore.QRect(270, 48, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_12.setFont(font)
        self.data_12.setStyleSheet("color:rgb(0,0,0);")
        self.data_12.setObjectName("data_12")
        self.data_input_13 = myTextEdit(self.widget_2)
        self.data_input_13.setGeometry(QtCore.QRect(335, 82, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_13.setFont(font)
        self.data_input_13.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_13.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_13.setLineWidth(2)
        self.data_input_13.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_13.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_13.setObjectName("data_input_13")
        self.data_13 = QtWidgets.QLabel(self.widget_2)
        self.data_13.setGeometry(QtCore.QRect(270, 83, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_13.setFont(font)
        self.data_13.setStyleSheet("color:rgb(0,0,0);")
        self.data_13.setObjectName("data_13")
        self.data_input_14 = myTextEdit(self.widget_2)
        self.data_input_14.setGeometry(QtCore.QRect(335, 117, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_14.setFont(font)
        self.data_input_14.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_14.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_14.setLineWidth(2)
        self.data_input_14.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_14.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_14.setObjectName("data_input_14")
        self.data_14 = QtWidgets.QLabel(self.widget_2)
        self.data_14.setGeometry(QtCore.QRect(270, 118, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_14.setFont(font)
        self.data_14.setStyleSheet("color:rgb(0,0,0);")
        self.data_14.setObjectName("data_14")
        self.data_15 = QtWidgets.QLabel(self.widget_2)
        self.data_15.setGeometry(QtCore.QRect(270, 153, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_15.setFont(font)
        self.data_15.setStyleSheet("color:rgb(0,0,0);")
        self.data_15.setObjectName("data_15")
        self.data_input_15 = myTextEdit(self.widget_2)
        self.data_input_15.setGeometry(QtCore.QRect(335, 152, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_15.setFont(font)
        self.data_input_15.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_15.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_15.setLineWidth(2)
        self.data_input_15.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_15.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_15.setObjectName("data_input_15")
        self.data_16 = QtWidgets.QLabel(self.widget_2)
        self.data_16.setGeometry(QtCore.QRect(270, 188, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_16.setFont(font)
        self.data_16.setStyleSheet("color:rgb(0,0,0);")
        self.data_16.setObjectName("data_16")
        self.data_input_16 = myTextEdit(self.widget_2)
        self.data_input_16.setGeometry(QtCore.QRect(335, 187, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_16.setFont(font)
        self.data_input_16.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_16.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_16.setLineWidth(2)
        self.data_input_16.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_16.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_16.setObjectName("data_input_16")
        self.data_input_17 = myTextEdit(self.widget_2)
        self.data_input_17.setGeometry(QtCore.QRect(335, 222, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_17.setFont(font)
        self.data_input_17.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_17.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_17.setLineWidth(2)
        self.data_input_17.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_17.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_17.setObjectName("data_input_17")
        self.data_17 = QtWidgets.QLabel(self.widget_2)
        self.data_17.setGeometry(QtCore.QRect(270, 223, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_17.setFont(font)
        self.data_17.setStyleSheet("color:rgb(0,0,0);")
        self.data_17.setObjectName("data_17")
        self.data_18 = QtWidgets.QLabel(self.widget_2)
        self.data_18.setGeometry(QtCore.QRect(270, 258, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_18.setFont(font)
        self.data_18.setStyleSheet("color:rgb(0,0,0);")
        self.data_18.setObjectName("data_18")
        self.data_input_18 = myTextEdit(self.widget_2)
        self.data_input_18.setGeometry(QtCore.QRect(335, 257, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_18.setFont(font)
        self.data_input_18.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_18.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_18.setLineWidth(2)
        self.data_input_18.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_18.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_18.setObjectName("data_input_18")
        self.data_19 = QtWidgets.QLabel(self.widget_2)
        self.data_19.setGeometry(QtCore.QRect(270, 293, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_19.setFont(font)
        self.data_19.setStyleSheet("color:rgb(0,0,0);")
        self.data_19.setObjectName("data_19")
        self.data_input_19 = myTextEdit(self.widget_2)
        self.data_input_19.setGeometry(QtCore.QRect(335, 292, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_19.setFont(font)
        self.data_input_19.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_19.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_19.setLineWidth(2)
        self.data_input_19.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_19.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_19.setObjectName("data_input_19")
        self.data_20 = QtWidgets.QLabel(self.widget_2)
        self.data_20.setGeometry(QtCore.QRect(270, 328, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_20.setFont(font)
        self.data_20.setStyleSheet("color:rgb(0,0,0);")
        self.data_20.setObjectName("data_20")
        self.data_input_20 = myTextEdit(self.widget_2)
        self.data_input_20.setGeometry(QtCore.QRect(335, 327, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_20.setFont(font)
        self.data_input_20.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_20.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_20.setLineWidth(2)
        self.data_input_20.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_20.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_20.setObjectName("data_input_20")
        self.data_21 = QtWidgets.QLabel(self.widget_2)
        self.data_21.setGeometry(QtCore.QRect(375, 13, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_21.setFont(font)
        self.data_21.setStyleSheet("color:rgb(0,0,0);")
        self.data_21.setObjectName("data_21")
        self.data_input_21 = myTextEdit(self.widget_2)
        self.data_input_21.setGeometry(QtCore.QRect(440, 12, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_21.setFont(font)
        self.data_input_21.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_21.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_21.setLineWidth(2)
        self.data_input_21.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_21.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_21.setObjectName("data_input_21")
        self.data_input_22 = myTextEdit(self.widget_2)
        self.data_input_22.setGeometry(QtCore.QRect(440, 47, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_22.setFont(font)
        self.data_input_22.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_22.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_22.setLineWidth(2)
        self.data_input_22.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_22.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_22.setObjectName("data_input_22")
        self.data_22 = QtWidgets.QLabel(self.widget_2)
        self.data_22.setGeometry(QtCore.QRect(375, 48, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_22.setFont(font)
        self.data_22.setStyleSheet("color:rgb(0,0,0);")
        self.data_22.setObjectName("data_22")
        self.data_23 = QtWidgets.QLabel(self.widget_2)
        self.data_23.setGeometry(QtCore.QRect(375, 83, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_23.setFont(font)
        self.data_23.setStyleSheet("color:rgb(0,0,0);")
        self.data_23.setObjectName("data_23")
        self.data_input_23 = myTextEdit(self.widget_2)
        self.data_input_23.setGeometry(QtCore.QRect(440, 82, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_23.setFont(font)
        self.data_input_23.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_23.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_23.setLineWidth(2)
        self.data_input_23.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_23.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_23.setObjectName("data_input_23")
        self.data_input_24 = myTextEdit(self.widget_2)
        self.data_input_24.setGeometry(QtCore.QRect(440, 117, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_24.setFont(font)
        self.data_input_24.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_24.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_24.setLineWidth(2)
        self.data_input_24.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_24.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_24.setObjectName("data_input_24")
        self.data_24 = QtWidgets.QLabel(self.widget_2)
        self.data_24.setGeometry(QtCore.QRect(375, 118, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_24.setFont(font)
        self.data_24.setStyleSheet("color:rgb(0,0,0);")
        self.data_24.setObjectName("data_24")
        self.data_input_25 = myTextEdit(self.widget_2)
        self.data_input_25.setGeometry(QtCore.QRect(440, 152, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_25.setFont(font)
        self.data_input_25.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_25.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_25.setLineWidth(2)
        self.data_input_25.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_25.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_25.setObjectName("data_input_25")
        self.data_25 = QtWidgets.QLabel(self.widget_2)
        self.data_25.setGeometry(QtCore.QRect(375, 153, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_25.setFont(font)
        self.data_25.setStyleSheet("color:rgb(0,0,0);")
        self.data_25.setObjectName("data_25")
        self.data_26 = QtWidgets.QLabel(self.widget_2)
        self.data_26.setGeometry(QtCore.QRect(375, 188, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_26.setFont(font)
        self.data_26.setStyleSheet("color:rgb(0,0,0);")
        self.data_26.setObjectName("data_26")
        self.data_input_26 = myTextEdit(self.widget_2)
        self.data_input_26.setGeometry(QtCore.QRect(440, 187, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_26.setFont(font)
        self.data_input_26.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_26.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_26.setLineWidth(2)
        self.data_input_26.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_26.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_26.setObjectName("data_input_26")
        self.data_input_27 = myTextEdit(self.widget_2)
        self.data_input_27.setGeometry(QtCore.QRect(440, 222, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_27.setFont(font)
        self.data_input_27.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_27.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_27.setLineWidth(2)
        self.data_input_27.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_27.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_27.setObjectName("data_input_27")
        self.data_27 = QtWidgets.QLabel(self.widget_2)
        self.data_27.setGeometry(QtCore.QRect(375, 223, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_27.setFont(font)
        self.data_27.setStyleSheet("color:rgb(0,0,0);")
        self.data_27.setObjectName("data_27")
        self.data_28 = QtWidgets.QLabel(self.widget_2)
        self.data_28.setGeometry(QtCore.QRect(375, 258, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_28.setFont(font)
        self.data_28.setStyleSheet("color:rgb(0,0,0);")
        self.data_28.setObjectName("data_28")
        self.data_input_28 = myTextEdit(self.widget_2)
        self.data_input_28.setGeometry(QtCore.QRect(440, 257, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_28.setFont(font)
        self.data_input_28.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_28.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_28.setLineWidth(2)
        self.data_input_28.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_28.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_28.setObjectName("data_input_28")
        self.data_29 = QtWidgets.QLabel(self.widget_2)
        self.data_29.setGeometry(QtCore.QRect(375, 293, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_29.setFont(font)
        self.data_29.setStyleSheet("color:rgb(0,0,0);")
        self.data_29.setObjectName("data_29")
        self.data_input_29 = myTextEdit(self.widget_2)
        self.data_input_29.setGeometry(QtCore.QRect(440, 292, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_29.setFont(font)
        self.data_input_29.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_29.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_29.setLineWidth(2)
        self.data_input_29.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_29.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_29.setObjectName("data_input_29")
        self.data_input_30 = myTextEdit(self.widget_2)
        self.data_input_30.setGeometry(QtCore.QRect(440, 327, 50, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_30.setFont(font)
        self.data_input_30.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_30.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_30.setLineWidth(2)
        self.data_input_30.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_30.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_30.setObjectName("data_input_30")
        self.data_30 = QtWidgets.QLabel(self.widget_2)
        self.data_30.setGeometry(QtCore.QRect(375, 328, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_30.setFont(font)
        self.data_30.setStyleSheet("color:rgb(0,0,0);")
        self.data_30.setObjectName("data_30")
        self.data_31 = QtWidgets.QLabel(self.widget_2)
        self.data_31.setGeometry(QtCore.QRect(480, 13, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_31.setFont(font)
        self.data_31.setStyleSheet("color:rgb(0,0,0);")
        self.data_31.setObjectName("data_31")
        self.data_input_31 = QtWidgets.QComboBox(self.widget_2)
        self.data_input_31.setGeometry(QtCore.QRect(545, 12, 131, 25))
        self.data_input_31.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_31.setObjectName("data_input_31")
        self.data_32 = QtWidgets.QLabel(self.widget_2)
        self.data_32.setGeometry(QtCore.QRect(480, 48, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_32.setFont(font)
        self.data_32.setStyleSheet("color:rgb(0,0,0);")
        self.data_32.setObjectName("data_32")
        self.data_input_32 = QtWidgets.QComboBox(self.widget_2)
        self.data_input_32.setGeometry(QtCore.QRect(545, 47, 131, 25))
        self.data_input_32.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_32.setEditable(False)
        self.data_input_32.setObjectName("data_input_32")
        self.data_input_33 = myTextEdit(self.widget_2)
        self.data_input_33.setGeometry(QtCore.QRect(545, 82, 121, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_33.setFont(font)
        self.data_input_33.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_33.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_33.setLineWidth(2)
        self.data_input_33.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_33.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_33.setObjectName("data_input_33")
        self.data_33 = QtWidgets.QLabel(self.widget_2)
        self.data_33.setGeometry(QtCore.QRect(480, 83, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_33.setFont(font)
        self.data_33.setStyleSheet("color:rgb(0,0,0);")
        self.data_33.setObjectName("data_33")
        self.data_34 = QtWidgets.QLabel(self.widget_2)
        self.data_34.setGeometry(QtCore.QRect(480, 118, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_34.setFont(font)
        self.data_34.setStyleSheet("color:rgb(0,0,0);")
        self.data_34.setObjectName("data_34")
        self.data_input_34 = myTextEdit(self.widget_2)
        self.data_input_34.setGeometry(QtCore.QRect(545, 117, 121, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_34.setFont(font)
        self.data_input_34.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_34.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_34.setLineWidth(2)
        self.data_input_34.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_34.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_34.setObjectName("data_input_34")
        self.data_35 = QtWidgets.QLabel(self.widget_2)
        self.data_35.setGeometry(QtCore.QRect(480, 153, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_35.setFont(font)
        self.data_35.setStyleSheet("color:rgb(0,0,0);")
        self.data_35.setObjectName("data_35")
        self.data_input_35 = QtWidgets.QComboBox(self.widget_2)
        self.data_input_35.setGeometry(QtCore.QRect(545, 152, 131, 25))
        self.data_input_35.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_35.setEditable(False)
        self.data_input_35.setObjectName("data_input_35")
        self.data_input_36 = myTextEdit(self.widget_2)
        self.data_input_36.setGeometry(QtCore.QRect(545, 187, 121, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_36.setFont(font)
        self.data_input_36.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_36.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_36.setLineWidth(2)
        self.data_input_36.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_36.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_36.setObjectName("data_input_36")
        self.data_36 = QtWidgets.QLabel(self.widget_2)
        self.data_36.setGeometry(QtCore.QRect(480, 188, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_36.setFont(font)
        self.data_36.setStyleSheet("color:rgb(0,0,0);")
        self.data_36.setObjectName("data_36")
        self.data_input_37 = myTextEdit(self.widget_2)
        self.data_input_37.setGeometry(QtCore.QRect(545, 222, 121, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.data_input_37.setFont(font)
        self.data_input_37.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_37.setFrameShape(QtWidgets.QFrame.Panel)
        self.data_input_37.setLineWidth(2)
        self.data_input_37.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_37.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.data_input_37.setObjectName("data_input_37")
        self.data_37 = QtWidgets.QLabel(self.widget_2)
        self.data_37.setGeometry(QtCore.QRect(480, 223, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_37.setFont(font)
        self.data_37.setStyleSheet("color:rgb(0,0,0);")
        self.data_37.setObjectName("data_37")
        self.data_38 = QtWidgets.QLabel(self.widget_2)
        self.data_38.setGeometry(QtCore.QRect(480, 258, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.data_38.setFont(font)
        self.data_38.setStyleSheet("color:rgb(0,0,0);")
        self.data_38.setObjectName("data_38")
        self.data_input_38 = QtWidgets.QComboBox(self.widget_2)
        self.data_input_38.setGeometry(QtCore.QRect(545, 257, 131, 25))
        self.data_input_38.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_input_38.setEditable(False)
        self.data_input_38.setObjectName("data_input_38")
        self.data_save = QtWidgets.QPushButton(self.widget_2)
        self.data_save.setGeometry(QtCore.QRect(515, 324, 151, 31))
        self.data_save.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_save.setObjectName("data_save")
        self.data_recal = QtWidgets.QPushButton(self.widget_2)
        self.data_recal.setGeometry(QtCore.QRect(515, 290, 151, 31))
        self.data_recal.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.data_recal.setObjectName("data_recal")
        self.widget_3 = QtWidgets.QWidget(self.frame)
        self.widget_3.setEnabled(True)
        self.widget_3.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_3.setObjectName("widget_3")
        self.listview_war = QtWidgets.QListWidget(self.widget_3)
        self.listview_war.setGeometry(QtCore.QRect(10, 45, 135, 301))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.listview_war.setFont(font)
        self.listview_war.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.listview_war.setFrameShape(QtWidgets.QFrame.Panel)
        self.listview_war.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.listview_war.setLineWidth(2)
        self.listview_war.setAutoScroll(True)
        self.listview_war.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview_war.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listview_war.setObjectName("listview_war")
        self.war_input_2 = myTextEdit(self.widget_3)
        self.war_input_2.setGeometry(QtCore.QRect(190, 78, 90, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_2.setFont(font)
        self.war_input_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_2.setLineWidth(2)
        self.war_input_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_2.setObjectName("war_input_2")
        self.war_2 = QtWidgets.QLabel(self.widget_3)
        self.war_2.setGeometry(QtCore.QRect(150, 80, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_2.setFont(font)
        self.war_2.setStyleSheet("color:rgb(0,0,0);")
        self.war_2.setObjectName("war_2")
        self.war_save = QtWidgets.QPushButton(self.widget_3)
        self.war_save.setGeometry(QtCore.QRect(550, 340, 121, 35))
        self.war_save.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_save.setObjectName("war_save")
        self.war_kind_1 = QtWidgets.QRadioButton(self.widget_3)
        self.war_kind_1.setGeometry(QtCore.QRect(10, 20, 41, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_kind_1.setFont(font)
        self.war_kind_1.setObjectName("war_kind_1")
        self.war_kind_2 = QtWidgets.QRadioButton(self.widget_3)
        self.war_kind_2.setGeometry(QtCore.QRect(55, 20, 41, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_kind_2.setFont(font)
        self.war_kind_2.setObjectName("war_kind_2")
        self.war_kind_3 = QtWidgets.QRadioButton(self.widget_3)
        self.war_kind_3.setGeometry(QtCore.QRect(100, 20, 41, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_kind_3.setFont(font)
        self.war_kind_3.setObjectName("war_kind_3")
        self.war_connect = QtWidgets.QPushButton(self.widget_3)
        self.war_connect.setGeometry(QtCore.QRect(10, 355, 135, 25))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.war_connect.setFont(font)
        self.war_connect.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_connect.setObjectName("war_connect")
        self.war_input_1 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_1.setGeometry(QtCore.QRect(160, 45, 121, 25))
        self.war_input_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_1.setEditable(False)
        self.war_input_1.setObjectName("war_input_1")
        self.war_input_3 = myTextEdit(self.widget_3)
        self.war_input_3.setGeometry(QtCore.QRect(190, 108, 90, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_3.setFont(font)
        self.war_input_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_3.setLineWidth(2)
        self.war_input_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_3.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_3.setObjectName("war_input_3")
        self.war_3 = QtWidgets.QLabel(self.widget_3)
        self.war_3.setGeometry(QtCore.QRect(150, 110, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_3.setFont(font)
        self.war_3.setStyleSheet("color:rgb(0,0,0);")
        self.war_3.setObjectName("war_3")
        self.war_input_4 = myTextEdit(self.widget_3)
        self.war_input_4.setGeometry(QtCore.QRect(190, 138, 90, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_4.setFont(font)
        self.war_input_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_4.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_4.setLineWidth(2)
        self.war_input_4.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_4.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_4.setObjectName("war_input_4")
        self.war_4 = QtWidgets.QLabel(self.widget_3)
        self.war_4.setGeometry(QtCore.QRect(150, 140, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_4.setFont(font)
        self.war_4.setStyleSheet("color:rgb(0,0,0);")
        self.war_4.setObjectName("war_4")
        self.war_input_5 = QtWidgets.QCheckBox(self.widget_3)
        self.war_input_5.setGeometry(QtCore.QRect(190, 171, 21, 19))
        self.war_input_5.setText("")
        self.war_input_5.setChecked(False)
        self.war_input_5.setObjectName("war_input_5")
        self.war_5 = QtWidgets.QLabel(self.widget_3)
        self.war_5.setGeometry(QtCore.QRect(150, 170, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_5.setFont(font)
        self.war_5.setStyleSheet("color:rgb(0,0,0);")
        self.war_5.setObjectName("war_5")
        self.war_6 = QtWidgets.QLabel(self.widget_3)
        self.war_6.setGeometry(QtCore.QRect(220, 169, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_6.setFont(font)
        self.war_6.setStyleSheet("color:rgb(0,0,0);")
        self.war_6.setObjectName("war_6")
        self.war_input_6 = QtWidgets.QCheckBox(self.widget_3)
        self.war_input_6.setGeometry(QtCore.QRect(260, 170, 21, 19))
        self.war_input_6.setText("")
        self.war_input_6.setChecked(False)
        self.war_input_6.setObjectName("war_input_6")
        self.war_7 = QtWidgets.QLabel(self.widget_3)
        self.war_7.setGeometry(QtCore.QRect(150, 200, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_7.setFont(font)
        self.war_7.setStyleSheet("color:rgb(0,0,0);")
        self.war_7.setObjectName("war_7")
        self.war_8 = QtWidgets.QLabel(self.widget_3)
        self.war_8.setGeometry(QtCore.QRect(220, 199, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_8.setFont(font)
        self.war_8.setStyleSheet("color:rgb(0,0,0);")
        self.war_8.setObjectName("war_8")
        self.war_input_7 = QtWidgets.QCheckBox(self.widget_3)
        self.war_input_7.setGeometry(QtCore.QRect(190, 201, 21, 19))
        self.war_input_7.setText("")
        self.war_input_7.setChecked(False)
        self.war_input_7.setObjectName("war_input_7")
        self.war_input_8 = QtWidgets.QCheckBox(self.widget_3)
        self.war_input_8.setGeometry(QtCore.QRect(260, 200, 21, 19))
        self.war_input_8.setText("")
        self.war_input_8.setChecked(False)
        self.war_input_8.setObjectName("war_input_8")
        self.war_input_9 = myTextEdit(self.widget_3)
        self.war_input_9.setGeometry(QtCore.QRect(170, 228, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_9.setFont(font)
        self.war_input_9.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_9.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_9.setLineWidth(2)
        self.war_input_9.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_9.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_9.setObjectName("war_input_9")
        self.war_9 = QtWidgets.QLabel(self.widget_3)
        self.war_9.setGeometry(QtCore.QRect(141, 230, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_9.setFont(font)
        self.war_9.setStyleSheet("color:rgb(0,0,0);")
        self.war_9.setObjectName("war_9")
        self.war_10 = QtWidgets.QLabel(self.widget_3)
        self.war_10.setGeometry(QtCore.QRect(206, 230, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_10.setFont(font)
        self.war_10.setStyleSheet("color:rgb(0,0,0);")
        self.war_10.setObjectName("war_10")
        self.war_input_10 = myTextEdit(self.widget_3)
        self.war_input_10.setGeometry(QtCore.QRect(235, 228, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_10.setFont(font)
        self.war_input_10.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_10.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_10.setLineWidth(2)
        self.war_input_10.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_10.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_10.setObjectName("war_input_10")
        self.war_11 = QtWidgets.QLabel(self.widget_3)
        self.war_11.setGeometry(QtCore.QRect(146, 260, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_11.setFont(font)
        self.war_11.setStyleSheet("color:rgb(0,0,0);")
        self.war_11.setObjectName("war_11")
        self.war_input_11 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_11.setGeometry(QtCore.QRect(170, 258, 110, 25))
        self.war_input_11.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_11.setEditable(False)
        self.war_input_11.setObjectName("war_input_11")
        self.war_input_11.addItem("")
        self.war_input_11.addItem("")
        self.war_input_11.addItem("")
        self.war_input_11.addItem("")
        self.war_input_11.addItem("")
        self.war_input_11.addItem("")
        self.war_input_11.addItem("")
        self.war_input_12 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_12.setGeometry(QtCore.QRect(185, 290, 96, 25))
        self.war_input_12.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_12.setEditable(False)
        self.war_input_12.setObjectName("war_input_12")
        self.war_12 = QtWidgets.QLabel(self.widget_3)
        self.war_12.setGeometry(QtCore.QRect(150, 292, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_12.setFont(font)
        self.war_12.setStyleSheet("color:rgb(0,0,0);")
        self.war_12.setObjectName("war_12")
        self.war_input_14 = myTextEdit(self.widget_3)
        self.war_input_14.setGeometry(QtCore.QRect(235, 323, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_14.setFont(font)
        self.war_input_14.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_14.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_14.setLineWidth(2)
        self.war_input_14.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_14.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_14.setObjectName("war_input_14")
        self.war_13 = QtWidgets.QLabel(self.widget_3)
        self.war_13.setGeometry(QtCore.QRect(145, 326, 21, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_13.setFont(font)
        self.war_13.setStyleSheet("color:rgb(0,0,0);")
        self.war_13.setObjectName("war_13")
        self.war_14 = QtWidgets.QLabel(self.widget_3)
        self.war_14.setGeometry(QtCore.QRect(210, 326, 21, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_14.setFont(font)
        self.war_14.setStyleSheet("color:rgb(0,0,0);")
        self.war_14.setObjectName("war_14")
        self.war_input_13 = myTextEdit(self.widget_3)
        self.war_input_13.setGeometry(QtCore.QRect(170, 323, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_13.setFont(font)
        self.war_input_13.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_13.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_13.setLineWidth(2)
        self.war_input_13.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_13.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_13.setObjectName("war_input_13")
        self.war_15 = QtWidgets.QLabel(self.widget_3)
        self.war_15.setGeometry(QtCore.QRect(285, 45, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_15.setFont(font)
        self.war_15.setStyleSheet("color:rgb(0,0,0);")
        self.war_15.setObjectName("war_15")
        self.war_input_15 = QtWidgets.QCheckBox(self.widget_3)
        self.war_input_15.setGeometry(QtCore.QRect(320, 46, 21, 19))
        self.war_input_15.setText("")
        self.war_input_15.setChecked(False)
        self.war_input_15.setObjectName("war_input_15")
        self.war_16 = QtWidgets.QLabel(self.widget_3)
        self.war_16.setGeometry(QtCore.QRect(285, 80, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_16.setFont(font)
        self.war_16.setStyleSheet("color:rgb(0,0,0);")
        self.war_16.setObjectName("war_16")
        self.war_input_16 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_16.setGeometry(QtCore.QRect(320, 78, 61, 25))
        self.war_input_16.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_16.setEditable(False)
        self.war_input_16.setObjectName("war_input_16")
        self.war_input_16.addItem("")
        self.war_input_16.addItem("")
        self.war_input_16.addItem("")
        self.war_input_16.addItem("")
        self.war_input_16.addItem("")
        self.war_input_17 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_17.setGeometry(QtCore.QRect(320, 108, 61, 25))
        self.war_input_17.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_17.setEditable(False)
        self.war_input_17.setObjectName("war_input_17")
        self.war_input_17.addItem("")
        self.war_input_17.addItem("")
        self.war_input_17.addItem("")
        self.war_17 = QtWidgets.QLabel(self.widget_3)
        self.war_17.setGeometry(QtCore.QRect(285, 110, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_17.setFont(font)
        self.war_17.setStyleSheet("color:rgb(0,0,0);")
        self.war_17.setObjectName("war_17")
        self.war_18 = QtWidgets.QLabel(self.widget_3)
        self.war_18.setGeometry(QtCore.QRect(285, 140, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_18.setFont(font)
        self.war_18.setStyleSheet("color:rgb(0,0,0);")
        self.war_18.setObjectName("war_18")
        self.war_input_18 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_18.setGeometry(QtCore.QRect(320, 138, 61, 25))
        self.war_input_18.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_18.setEditable(False)
        self.war_input_18.setObjectName("war_input_18")
        self.war_input_18.addItem("")
        self.war_input_18.addItem("")
        self.war_input_18.addItem("")
        self.war_input_19 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_19.setGeometry(QtCore.QRect(320, 168, 61, 25))
        self.war_input_19.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_19.setEditable(False)
        self.war_input_19.setObjectName("war_input_19")
        self.war_input_19.addItem("")
        self.war_input_19.addItem("")
        self.war_input_19.addItem("")
        self.war_19 = QtWidgets.QLabel(self.widget_3)
        self.war_19.setGeometry(QtCore.QRect(285, 170, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_19.setFont(font)
        self.war_19.setStyleSheet("color:rgb(0,0,0);")
        self.war_19.setObjectName("war_19")
        self.war_20 = QtWidgets.QLabel(self.widget_3)
        self.war_20.setGeometry(QtCore.QRect(285, 200, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_20.setFont(font)
        self.war_20.setStyleSheet("color:rgb(0,0,0);")
        self.war_20.setObjectName("war_20")
        self.war_input_20 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_20.setGeometry(QtCore.QRect(320, 198, 61, 25))
        self.war_input_20.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_20.setEditable(False)
        self.war_input_20.setObjectName("war_input_20")
        self.war_input_20.addItem("")
        self.war_input_20.addItem("")
        self.war_input_20.addItem("")
        self.war_input_21 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_21.setGeometry(QtCore.QRect(320, 228, 61, 25))
        self.war_input_21.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_21.setEditable(False)
        self.war_input_21.setObjectName("war_input_21")
        self.war_input_21.addItem("")
        self.war_input_21.addItem("")
        self.war_input_21.addItem("")
        self.war_21 = QtWidgets.QLabel(self.widget_3)
        self.war_21.setGeometry(QtCore.QRect(285, 230, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_21.setFont(font)
        self.war_21.setStyleSheet("color:rgb(0,0,0);")
        self.war_21.setObjectName("war_21")
        self.war_input_22 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_22.setGeometry(QtCore.QRect(320, 258, 61, 25))
        self.war_input_22.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_22.setEditable(False)
        self.war_input_22.setObjectName("war_input_22")
        self.war_input_22.addItem("")
        self.war_input_22.addItem("")
        self.war_input_22.addItem("")
        self.war_22 = QtWidgets.QLabel(self.widget_3)
        self.war_22.setGeometry(QtCore.QRect(285, 260, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_22.setFont(font)
        self.war_22.setStyleSheet("color:rgb(0,0,0);")
        self.war_22.setObjectName("war_22")
        self.war_input_23 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_23.setGeometry(QtCore.QRect(320, 288, 61, 25))
        self.war_input_23.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_23.setEditable(False)
        self.war_input_23.setObjectName("war_input_23")
        self.war_input_23.addItem("")
        self.war_input_23.addItem("")
        self.war_input_23.addItem("")
        self.war_input_23.addItem("")
        self.war_23 = QtWidgets.QLabel(self.widget_3)
        self.war_23.setGeometry(QtCore.QRect(285, 290, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_23.setFont(font)
        self.war_23.setStyleSheet("color:rgb(0,0,0);")
        self.war_23.setObjectName("war_23")
        self.listview_war_2 = QtWidgets.QListWidget(self.widget_3)
        self.listview_war_2.setGeometry(QtCore.QRect(390, 45, 121, 211))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.listview_war_2.setFont(font)
        self.listview_war_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.listview_war_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.listview_war_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.listview_war_2.setLineWidth(2)
        self.listview_war_2.setAutoScroll(True)
        self.listview_war_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview_war_2.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listview_war_2.setObjectName("listview_war_2")
        self.war_lockadd = QtWidgets.QPushButton(self.widget_3)
        self.war_lockadd.setGeometry(QtCore.QRect(390, 258, 121, 25))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.war_lockadd.setFont(font)
        self.war_lockadd.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_lockadd.setObjectName("war_lockadd")
        self.war_locksub = QtWidgets.QPushButton(self.widget_3)
        self.war_locksub.setGeometry(QtCore.QRect(390, 288, 121, 25))
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.war_locksub.setFont(font)
        self.war_locksub.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_locksub.setObjectName("war_locksub")
        self.war_life = QtWidgets.QPushButton(self.widget_3)
        self.war_life.setEnabled(True)
        self.war_life.setGeometry(QtCore.QRect(550, 300, 121, 35))
        self.war_life.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0)")
        self.war_life.setObjectName("war_life")
        self.war_kill = QtWidgets.QPushButton(self.widget_3)
        self.war_kill.setGeometry(QtCore.QRect(590, 10, 71, 25))
        self.war_kill.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_kill.setObjectName("war_kill")
        self.war_input_24 = myTextEdit(self.widget_3)
        self.war_input_24.setGeometry(QtCore.QRect(590, 43, 71, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_24.setFont(font)
        self.war_input_24.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_24.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_24.setLineWidth(2)
        self.war_input_24.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_24.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_24.setObjectName("war_input_24")
        self.war_24 = QtWidgets.QLabel(self.widget_3)
        self.war_24.setGeometry(QtCore.QRect(520, 45, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_24.setFont(font)
        self.war_24.setStyleSheet("color:rgb(0,0,0);")
        self.war_24.setObjectName("war_24")
        self.war_25 = QtWidgets.QLabel(self.widget_3)
        self.war_25.setGeometry(QtCore.QRect(520, 75, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_25.setFont(font)
        self.war_25.setStyleSheet("color:rgb(0,0,0);")
        self.war_25.setObjectName("war_25")
        self.war_input_25 = myTextEdit(self.widget_3)
        self.war_input_25.setGeometry(QtCore.QRect(590, 73, 71, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_25.setFont(font)
        self.war_input_25.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_25.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_25.setLineWidth(2)
        self.war_input_25.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_25.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_25.setObjectName("war_input_25")
        self.war_input_26 = myTextEdit(self.widget_3)
        self.war_input_26.setGeometry(QtCore.QRect(590, 103, 71, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_26.setFont(font)
        self.war_input_26.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_26.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_26.setLineWidth(2)
        self.war_input_26.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_26.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_26.setObjectName("war_input_26")
        self.war_26 = QtWidgets.QLabel(self.widget_3)
        self.war_26.setGeometry(QtCore.QRect(520, 105, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_26.setFont(font)
        self.war_26.setStyleSheet("color:rgb(0,0,0);")
        self.war_26.setObjectName("war_26")
        self.war_input_27 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_27.setGeometry(QtCore.QRect(590, 133, 71, 25))
        self.war_input_27.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_27.setEditable(False)
        self.war_input_27.setObjectName("war_input_27")
        self.war_input_27.addItem("")
        self.war_input_27.addItem("")
        self.war_input_27.addItem("")
        self.war_input_27.addItem("")
        self.war_input_27.addItem("")
        self.war_27 = QtWidgets.QLabel(self.widget_3)
        self.war_27.setGeometry(QtCore.QRect(520, 135, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_27.setFont(font)
        self.war_27.setStyleSheet("color:rgb(0,0,0);")
        self.war_27.setObjectName("war_27")
        self.war_input_28 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_28.setGeometry(QtCore.QRect(535, 168, 61, 25))
        self.war_input_28.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_28.setEditable(False)
        self.war_input_28.setObjectName("war_input_28")
        self.war_input_28.addItem("")
        self.war_input_28.addItem("")
        self.war_input_28.addItem("")
        self.war_28 = QtWidgets.QLabel(self.widget_3)
        self.war_28.setGeometry(QtCore.QRect(511, 170, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_28.setFont(font)
        self.war_28.setStyleSheet("color:rgb(0,0,0);")
        self.war_28.setObjectName("war_28")
        self.war_29 = QtWidgets.QLabel(self.widget_3)
        self.war_29.setGeometry(QtCore.QRect(511, 200, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_29.setFont(font)
        self.war_29.setStyleSheet("color:rgb(0,0,0);")
        self.war_29.setObjectName("war_29")
        self.war_input_29 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_29.setGeometry(QtCore.QRect(535, 198, 61, 25))
        self.war_input_29.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_29.setEditable(False)
        self.war_input_29.setObjectName("war_input_29")
        self.war_input_29.addItem("")
        self.war_input_29.addItem("")
        self.war_input_29.addItem("")
        self.war_input_29.addItem("")
        self.war_input_30 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_30.setGeometry(QtCore.QRect(615, 198, 61, 25))
        self.war_input_30.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_30.setEditable(False)
        self.war_input_30.setObjectName("war_input_30")
        self.war_input_30.addItem("")
        self.war_input_30.addItem("")
        self.war_input_30.addItem("")
        self.war_input_30.addItem("")
        self.war_30 = QtWidgets.QLabel(self.widget_3)
        self.war_30.setGeometry(QtCore.QRect(591, 200, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_30.setFont(font)
        self.war_30.setStyleSheet("color:rgb(0,0,0);")
        self.war_30.setObjectName("war_30")
        self.war_31 = QtWidgets.QLabel(self.widget_3)
        self.war_31.setGeometry(QtCore.QRect(511, 230, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_31.setFont(font)
        self.war_31.setStyleSheet("color:rgb(0,0,0);")
        self.war_31.setObjectName("war_31")
        self.war_input_31 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_31.setGeometry(QtCore.QRect(535, 228, 61, 25))
        self.war_input_31.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_31.setEditable(False)
        self.war_input_31.setObjectName("war_input_31")
        self.war_input_31.addItem("")
        self.war_input_31.addItem("")
        self.war_input_31.addItem("")
        self.war_input_31.addItem("")
        self.war_input_32 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_32.setGeometry(QtCore.QRect(615, 228, 61, 25))
        self.war_input_32.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_32.setEditable(False)
        self.war_input_32.setObjectName("war_input_32")
        self.war_input_32.addItem("")
        self.war_input_32.addItem("")
        self.war_input_32.addItem("")
        self.war_input_32.addItem("")
        self.war_32 = QtWidgets.QLabel(self.widget_3)
        self.war_32.setGeometry(QtCore.QRect(591, 230, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_32.setFont(font)
        self.war_32.setStyleSheet("color:rgb(0,0,0);")
        self.war_32.setObjectName("war_32")
        self.war_input_33 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_33.setGeometry(QtCore.QRect(535, 258, 61, 25))
        self.war_input_33.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_33.setEditable(False)
        self.war_input_33.setObjectName("war_input_33")
        self.war_input_33.addItem("")
        self.war_input_33.addItem("")
        self.war_input_33.addItem("")
        self.war_input_33.addItem("")
        self.war_33 = QtWidgets.QLabel(self.widget_3)
        self.war_33.setGeometry(QtCore.QRect(511, 260, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_33.setFont(font)
        self.war_33.setStyleSheet("color:rgb(0,0,0);")
        self.war_33.setObjectName("war_33")
        self.war_input_34 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_34.setGeometry(QtCore.QRect(615, 258, 61, 25))
        self.war_input_34.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_34.setEditable(False)
        self.war_input_34.setObjectName("war_input_34")
        self.war_input_34.addItem("")
        self.war_input_34.addItem("")
        self.war_input_34.addItem("")
        self.war_input_34.addItem("")
        self.war_34 = QtWidgets.QLabel(self.widget_3)
        self.war_34.setGeometry(QtCore.QRect(591, 260, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_34.setFont(font)
        self.war_34.setStyleSheet("color:rgb(0,0,0);")
        self.war_34.setObjectName("war_34")
        self.war_input_35 = QtWidgets.QComboBox(self.widget_3)
        self.war_input_35.setGeometry(QtCore.QRect(615, 168, 61, 25))
        self.war_input_35.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_35.setEditable(False)
        self.war_input_35.setObjectName("war_input_35")
        self.war_input_35.addItem("")
        self.war_input_35.addItem("")
        self.war_input_35.addItem("")
        self.war_input_35.addItem("")
        self.war_35 = QtWidgets.QLabel(self.widget_3)
        self.war_35.setGeometry(QtCore.QRect(591, 170, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_35.setFont(font)
        self.war_35.setStyleSheet("color:rgb(0,0,0);")
        self.war_35.setObjectName("war_35")
        self.war_input_36 = myTextEdit(self.widget_3)
        self.war_input_36.setGeometry(QtCore.QRect(305, 323, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_36.setFont(font)
        self.war_input_36.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_36.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_36.setLineWidth(2)
        self.war_input_36.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_36.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_36.setObjectName("war_input_36")
        self.war_input_37 = myTextEdit(self.widget_3)
        self.war_input_37.setGeometry(QtCore.QRect(370, 323, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_37.setFont(font)
        self.war_input_37.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_37.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_37.setLineWidth(2)
        self.war_input_37.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_37.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_37.setObjectName("war_input_37")
        self.war_36 = QtWidgets.QLabel(self.widget_3)
        self.war_36.setGeometry(QtCore.QRect(280, 326, 21, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_36.setFont(font)
        self.war_36.setStyleSheet("color:rgb(0,0,0);")
        self.war_36.setObjectName("war_36")
        self.war_37 = QtWidgets.QLabel(self.widget_3)
        self.war_37.setGeometry(QtCore.QRect(345, 326, 21, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setBold(True)
        font.setWeight(75)
        self.war_37.setFont(font)
        self.war_37.setStyleSheet("color:rgb(0,0,0);")
        self.war_37.setObjectName("war_37")
        self.war_39 = QtWidgets.QLabel(self.widget_3)
        self.war_39.setGeometry(QtCore.QRect(476, 326, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_39.setFont(font)
        self.war_39.setStyleSheet("color:rgb(0,0,0);")
        self.war_39.setObjectName("war_39")
        self.war_input_38 = myTextEdit(self.widget_3)
        self.war_input_38.setGeometry(QtCore.QRect(435, 323, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_38.setFont(font)
        self.war_input_38.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_38.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_38.setLineWidth(2)
        self.war_input_38.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_38.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_38.setObjectName("war_input_38")
        self.war_input_39 = myTextEdit(self.widget_3)
        self.war_input_39.setGeometry(QtCore.QRect(500, 323, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_39.setFont(font)
        self.war_input_39.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_39.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_39.setLineWidth(2)
        self.war_input_39.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_39.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_39.setObjectName("war_input_39")
        self.war_38 = QtWidgets.QLabel(self.widget_3)
        self.war_38.setGeometry(QtCore.QRect(411, 326, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_38.setFont(font)
        self.war_38.setStyleSheet("color:rgb(0,0,0);")
        self.war_38.setObjectName("war_38")
        self.war_input_40 = myTextEdit(self.widget_3)
        self.war_input_40.setGeometry(QtCore.QRect(170, 350, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_40.setFont(font)
        self.war_input_40.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_40.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_40.setLineWidth(2)
        self.war_input_40.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_40.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_40.setObjectName("war_input_40")
        self.war_input_41 = myTextEdit(self.widget_3)
        self.war_input_41.setGeometry(QtCore.QRect(305, 350, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_41.setFont(font)
        self.war_input_41.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_41.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_41.setLineWidth(2)
        self.war_input_41.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_41.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_41.setObjectName("war_input_41")
        self.war_input_42 = myTextEdit(self.widget_3)
        self.war_input_42.setGeometry(QtCore.QRect(435, 350, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_42.setFont(font)
        self.war_input_42.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_42.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_42.setLineWidth(2)
        self.war_input_42.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_42.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_42.setObjectName("war_input_42")
        self.war_input_43 = myTextEdit(self.widget_3)
        self.war_input_43.setGeometry(QtCore.QRect(500, 350, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_43.setFont(font)
        self.war_input_43.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_43.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_43.setLineWidth(2)
        self.war_input_43.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_43.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_43.setObjectName("war_input_43")
        self.war_input_44 = myTextEdit(self.widget_3)
        self.war_input_44.setGeometry(QtCore.QRect(235, 350, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_44.setFont(font)
        self.war_input_44.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_44.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_44.setLineWidth(2)
        self.war_input_44.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_44.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_44.setObjectName("war_input_44")
        self.war_40 = QtWidgets.QLabel(self.widget_3)
        self.war_40.setGeometry(QtCore.QRect(410, 353, 21, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_40.setFont(font)
        self.war_40.setStyleSheet("color:rgb(0,0,0);")
        self.war_40.setObjectName("war_40")
        self.war_41 = QtWidgets.QLabel(self.widget_3)
        self.war_41.setGeometry(QtCore.QRect(145, 353, 21, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_41.setFont(font)
        self.war_41.setStyleSheet("color:rgb(0,0,0);")
        self.war_41.setObjectName("war_41")
        self.war_42 = QtWidgets.QLabel(self.widget_3)
        self.war_42.setGeometry(QtCore.QRect(345, 353, 21, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_42.setFont(font)
        self.war_42.setStyleSheet("color:rgb(0,0,0);")
        self.war_42.setObjectName("war_42")
        self.war_input_45 = myTextEdit(self.widget_3)
        self.war_input_45.setGeometry(QtCore.QRect(370, 350, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_45.setFont(font)
        self.war_input_45.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_45.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_45.setLineWidth(2)
        self.war_input_45.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_45.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_45.setObjectName("war_input_45")
        self.war_43 = QtWidgets.QLabel(self.widget_3)
        self.war_43.setGeometry(QtCore.QRect(211, 353, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_43.setFont(font)
        self.war_43.setStyleSheet("color:rgb(0,0,0);")
        self.war_43.setObjectName("war_43")
        self.war_44 = QtWidgets.QLabel(self.widget_3)
        self.war_44.setGeometry(QtCore.QRect(476, 353, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_44.setFont(font)
        self.war_44.setStyleSheet("color:rgb(0,0,0);")
        self.war_44.setObjectName("war_44")
        self.war_45 = QtWidgets.QLabel(self.widget_3)
        self.war_45.setGeometry(QtCore.QRect(281, 353, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_45.setFont(font)
        self.war_45.setStyleSheet("color:rgb(0,0,0);")
        self.war_45.setObjectName("war_45")
        self.war_input_46 = QtWidgets.QCheckBox(self.widget_3)
        self.war_input_46.setGeometry(QtCore.QRect(365, 46, 21, 19))
        self.war_input_46.setText("")
        self.war_input_46.setChecked(False)
        self.war_input_46.setObjectName("war_input_46")
        self.war_46 = QtWidgets.QLabel(self.widget_3)
        self.war_46.setGeometry(QtCore.QRect(340, 45, 20, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.war_46.setFont(font)
        self.war_46.setStyleSheet("color:rgb(0,0,0);")
        self.war_46.setObjectName("war_46")
        self.war_input_50 = QtWidgets.QTextEdit(self.widget_3)
        self.war_input_50.setGeometry(QtCore.QRect(540, 10, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_50.setFont(font)
        self.war_input_50.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_50.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_50.setLineWidth(2)
        self.war_input_50.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_50.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_50.setObjectName("war_input_50")
        self.war_input_48 = QtWidgets.QTextEdit(self.widget_3)
        self.war_input_48.setGeometry(QtCore.QRect(440, 10, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_48.setFont(font)
        self.war_input_48.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_48.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_48.setLineWidth(2)
        self.war_input_48.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_48.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_48.setObjectName("war_input_48")
        self.war_input_49 = QtWidgets.QTextEdit(self.widget_3)
        self.war_input_49.setGeometry(QtCore.QRect(490, 10, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_49.setFont(font)
        self.war_input_49.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_49.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_49.setLineWidth(2)
        self.war_input_49.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_49.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_49.setObjectName("war_input_49")
        self.war_input_47 = QtWidgets.QTextEdit(self.widget_3)
        self.war_input_47.setGeometry(QtCore.QRect(390, 10, 41, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_47.setFont(font)
        self.war_input_47.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.war_input_47.setFrameShape(QtWidgets.QFrame.Panel)
        self.war_input_47.setLineWidth(2)
        self.war_input_47.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_47.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_47.setObjectName("war_input_47")
        self.war_input_51 = QtWidgets.QLineEdit(self.widget_3)
        self.war_input_51.setGeometry(QtCore.QRect(185, 170, 25, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_51.setFont(font)
        self.war_input_51.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        #self.war_input_51.setFrameShape(QtWidgets.QFrame.Panel)
        #self.war_input_51.setLineWidth(2)
        #self.war_input_51.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.war_input_51.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_51.setObjectName("war_input_51")
        self.war_input_52 = QtWidgets.QLineEdit(self.widget_3)
        self.war_input_52.setGeometry(QtCore.QRect(255, 170, 25, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_52.setFont(font)
        self.war_input_52.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        #self.war_input_52.setFrameShape(QtWidgets.QFrame.Panel)
        #self.war_input_52.setLineWidth(2)
        #self.war_input_52.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.war_input_52.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_52.setObjectName("war_input_52")
        self.war_input_53 = QtWidgets.QLineEdit(self.widget_3)
        self.war_input_53.setGeometry(QtCore.QRect(185, 200, 25, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_53.setFont(font)
        self.war_input_53.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        #self.war_input_53.setFrameShape(QtWidgets.QFrame.Panel)
        #self.war_input_53.setLineWidth(2)
        #self.war_input_53.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.war_input_53.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_53.setObjectName("war_input_53")
        self.war_input_54 = QtWidgets.QLineEdit(self.widget_3)
        self.war_input_54.setGeometry(QtCore.QRect(255, 200, 25, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.war_input_54.setFont(font)
        self.war_input_54.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        #self.war_input_54.setFrameShape(QtWidgets.QFrame.Panel)
        #self.war_input_54.setLineWidth(2)
        #self.war_input_54.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        #self.war_input_54.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.war_input_54.setObjectName("war_input_54")
        self.widget_0 = QtWidgets.QWidget(self.frame)
        self.widget_0.setEnabled(True)
        self.widget_0.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_0.setObjectName("widget_0")
        self.label = QtWidgets.QLabel(self.widget_0)
        self.label.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.label.setStyleSheet("background-color:rgb(253, 255, 244)")
        self.label.setText("")
        self.label.setObjectName("label")
        self.widget_4 = QtWidgets.QWidget(self.frame)
        self.widget_4.setEnabled(True)
        self.widget_4.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_4.setObjectName("widget_4")
        self.listview_item = QtWidgets.QListWidget(self.widget_4)
        self.listview_item.setGeometry(QtCore.QRect(10, 13, 145, 365))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.listview_item.setFont(font)
        self.listview_item.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.listview_item.setFrameShape(QtWidgets.QFrame.Panel)
        self.listview_item.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.listview_item.setLineWidth(2)
        self.listview_item.setAutoScroll(True)
        self.listview_item.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview_item.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listview_item.setObjectName("listview_item")
        self.item_save = QtWidgets.QPushButton(self.widget_4)
        self.item_save.setGeometry(QtCore.QRect(520, 320, 121, 51))
        self.item_save.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_save.setObjectName("item_save")
        self.item_1 = QtWidgets.QLabel(self.widget_4)
        self.item_1.setGeometry(QtCore.QRect(175, 25, 41, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.item_1.setFont(font)
        self.item_1.setStyleSheet("color:rgb(0,0,0);")
        self.item_1.setObjectName("item_1")
        self.item_input_1 = QtWidgets.QComboBox(self.widget_4)
        self.item_input_1.setGeometry(QtCore.QRect(185, 50, 136, 25))
        self.item_input_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_input_1.setObjectName("item_input_1")
        self.item_2 = QtWidgets.QLabel(self.widget_4)
        self.item_2.setGeometry(QtCore.QRect(185, 100, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.item_2.setFont(font)
        self.item_2.setStyleSheet("color:rgb(0,0,0);")
        self.item_2.setObjectName("item_2")
        self.item_input_2 = myTextEdit(self.widget_4)
        self.item_input_2.setGeometry(QtCore.QRect(185, 125, 131, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.item_input_2.setFont(font)
        self.item_input_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_input_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_input_2.setLineWidth(2)
        self.item_input_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_2.setObjectName("item_input_2")
        self.item_3 = QtWidgets.QLabel(self.widget_4)
        self.item_3.setGeometry(QtCore.QRect(185, 175, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.item_3.setFont(font)
        self.item_3.setStyleSheet("color:rgb(0,0,0);")
        self.item_3.setObjectName("item_3")
        self.item_input_3 = myTextEdit(self.widget_4)
        self.item_input_3.setGeometry(QtCore.QRect(185, 200, 131, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.item_input_3.setFont(font)
        self.item_input_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_input_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_input_3.setLineWidth(2)
        self.item_input_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_3.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_3.setObjectName("item_input_3")
        self.item_all_1 = QtWidgets.QPushButton(self.widget_4)
        self.item_all_1.setGeometry(QtCore.QRect(185, 250, 131, 25))
        self.item_all_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_all_1.setObjectName("item_all_1")
        self.item_all_2 = QtWidgets.QPushButton(self.widget_4)
        self.item_all_2.setGeometry(QtCore.QRect(185, 290, 131, 25))
        self.item_all_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_all_2.setObjectName("item_all_2")
        self.item_all_3 = QtWidgets.QPushButton(self.widget_4)
        self.item_all_3.setGeometry(QtCore.QRect(185, 330, 131, 25))
        self.item_all_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_all_3.setObjectName("item_all_3")
        self.listview_item_2 = QtWidgets.QListWidget(self.widget_4)
        self.listview_item_2.setGeometry(QtCore.QRect(350, 13, 145, 365))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.listview_item_2.setFont(font)
        self.listview_item_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.listview_item_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.listview_item_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.listview_item_2.setLineWidth(2)
        self.listview_item_2.setAutoScroll(True)
        self.listview_item_2.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview_item_2.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listview_item_2.setObjectName("listview_item_2")
        self.item_4 = QtWidgets.QLabel(self.widget_4)
        self.item_4.setGeometry(QtCore.QRect(520, 25, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.item_4.setFont(font)
        self.item_4.setStyleSheet("color:rgb(0,0,0);")
        self.item_4.setObjectName("item_4")
        self.item_input_4 = myTextEdit(self.widget_4)
        self.item_input_4.setGeometry(QtCore.QRect(520, 50, 131, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.item_input_4.setFont(font)
        self.item_input_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_input_4.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_input_4.setLineWidth(2)
        self.item_input_4.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_4.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_4.setObjectName("item_input_4")
        self.item_5 = QtWidgets.QLabel(self.widget_4)
        self.item_5.setGeometry(QtCore.QRect(520, 100, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.item_5.setFont(font)
        self.item_5.setStyleSheet("color:rgb(0,0,0);")
        self.item_5.setObjectName("item_5")
        self.item_input_5 = myTextEdit(self.widget_4)
        self.item_input_5.setGeometry(QtCore.QRect(520, 125, 131, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.item_input_5.setFont(font)
        self.item_input_5.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_input_5.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_input_5.setLineWidth(2)
        self.item_input_5.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_5.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_5.setObjectName("item_input_5")
        self.item_input_6 = myTextEdit(self.widget_4)
        self.item_input_6.setGeometry(QtCore.QRect(520, 200, 131, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.item_input_6.setFont(font)
        self.item_input_6.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_input_6.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_input_6.setLineWidth(2)
        self.item_input_6.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_6.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_6.setObjectName("item_input_6")
        self.item_6 = QtWidgets.QLabel(self.widget_4)
        self.item_6.setGeometry(QtCore.QRect(505, 175, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.item_6.setFont(font)
        self.item_6.setStyleSheet("color:rgb(0,0,0);")
        self.item_6.setObjectName("item_6")
        ''''''
        self.item_input_7 = myTextEdit(self.widget_4)
        self.item_input_7.setGeometry(QtCore.QRect(520, 275, 131, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.item_input_7.setFont(font)
        self.item_input_7.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_input_7.setFrameShape(QtWidgets.QFrame.Panel)
        self.item_input_7.setLineWidth(2)
        self.item_input_7.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_7.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.item_input_7.setObjectName("item_input_7")
        self.item_7 = QtWidgets.QLabel(self.widget_4)
        self.item_7.setGeometry(QtCore.QRect(505, 250, 61, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.item_7.setFont(font)
        self.item_7.setStyleSheet("color:rgb(0,0,0);")
        self.item_7.setObjectName("item_7")
        ''''''
        self.widget_5 = QtWidgets.QWidget(self.frame)
        self.widget_5.setEnabled(True)
        self.widget_5.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_5.setObjectName("widget_5")
        self.listview_item_3 = QtWidgets.QListWidget(self.widget_5)
        self.listview_item_3.setGeometry(QtCore.QRect(10, 13, 165, 365))
        font = QtGui.QFont()
        font.setPointSize(9)
        self.listview_item_3.setFont(font)
        self.listview_item_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.listview_item_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.listview_item_3.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.listview_item_3.setLineWidth(2)
        self.listview_item_3.setAutoScroll(True)
        self.listview_item_3.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview_item_3.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listview_item_3.setObjectName("listview_item_3")
        self.item_save_2 = QtWidgets.QPushButton(self.widget_5)
        self.item_save_2.setGeometry(QtCore.QRect(550, 320, 121, 51))
        self.item_save_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_save_2.setObjectName("item_save_2")
        self.power_1 = QtWidgets.QLabel(self.widget_5)
        self.power_1.setGeometry(QtCore.QRect(185, 15, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.power_1.setFont(font)
        self.power_1.setStyleSheet("color:rgb(0,0,0);")
        self.power_1.setObjectName("power_1")
        self.power_input_1_1 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_1_1.setGeometry(QtCore.QRect(185, 40, 136, 25))
        self.power_input_1_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_1_1.setObjectName("power_input_1_1")
        self.power_2 = QtWidgets.QLabel(self.widget_5)
        self.power_2.setGeometry(QtCore.QRect(185, 115, 41, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.power_2.setFont(font)
        self.power_2.setStyleSheet("color:rgb(0,0,0);")
        self.power_2.setObjectName("power_2")
        self.power_3 = QtWidgets.QLabel(self.widget_5)
        self.power_3.setGeometry(QtCore.QRect(185, 215, 31, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.power_3.setFont(font)
        self.power_3.setStyleSheet("color:rgb(0,0,0);")
        self.power_3.setObjectName("power_3")
        self.power_input_1_2 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_1_2.setGeometry(QtCore.QRect(355, 40, 136, 25))
        self.power_input_1_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_1_2.setObjectName("power_input_1_2")
        self.power_input_1_3 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_1_3.setGeometry(QtCore.QRect(525, 40, 136, 25))
        self.power_input_1_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_1_3.setObjectName("power_input_1_3")
        self.power_input_1_4 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_1_4.setGeometry(QtCore.QRect(185, 80, 136, 25))
        self.power_input_1_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_1_4.setObjectName("power_input_1_4")
        self.power_input_1_5 = myTextEdit(self.widget_5)
        self.power_input_1_5.setGeometry(QtCore.QRect(355, 80, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.power_input_1_5.setFont(font)
        self.power_input_1_5.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_1_5.setFrameShape(QtWidgets.QFrame.Panel)
        self.power_input_1_5.setLineWidth(2)
        self.power_input_1_5.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_1_5.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_1_5.setObjectName("power_input_1_5")
        self.power_input_2_2 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_2_2.setGeometry(QtCore.QRect(355, 140, 136, 25))
        self.power_input_2_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_2_2.setObjectName("power_input_2_2")
        self.power_input_2_1 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_2_1.setGeometry(QtCore.QRect(185, 140, 136, 25))
        self.power_input_2_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_2_1.setObjectName("power_input_2_1")
        self.power_input_2_3 = myTextEdit(self.widget_5)
        self.power_input_2_3.setGeometry(QtCore.QRect(525, 140, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.power_input_2_3.setFont(font)
        self.power_input_2_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_2_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.power_input_2_3.setLineWidth(2)
        self.power_input_2_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_2_3.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_2_3.setObjectName("power_input_2_3")
        self.power_input_2_4 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_2_4.setGeometry(QtCore.QRect(185, 180, 136, 25))
        self.power_input_2_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_2_4.setObjectName("power_input_2_4")
        self.power_input_2_6 = myTextEdit(self.widget_5)
        self.power_input_2_6.setGeometry(QtCore.QRect(525, 180, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.power_input_2_6.setFont(font)
        self.power_input_2_6.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_2_6.setFrameShape(QtWidgets.QFrame.Panel)
        self.power_input_2_6.setLineWidth(2)
        self.power_input_2_6.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_2_6.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_2_6.setObjectName("power_input_2_6")
        self.power_input_2_5 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_2_5.setGeometry(QtCore.QRect(355, 180, 136, 25))
        self.power_input_2_5.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_2_5.setObjectName("power_input_2_5")
        self.power_input_3_2 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_3_2.setGeometry(QtCore.QRect(315, 240, 120, 25))
        self.power_input_3_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_2.setObjectName("power_input_3_2")
        self.power_input_3_3 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_3_3.setGeometry(QtCore.QRect(445, 240, 120, 25))
        self.power_input_3_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_3.setObjectName("power_input_3_3")
        self.power_input_3_1 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_3_1.setGeometry(QtCore.QRect(185, 240, 120, 25))
        self.power_input_3_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_1.setObjectName("power_input_3_1")
        self.power_input_3_4 = myTextEdit(self.widget_5)
        self.power_input_3_4.setGeometry(QtCore.QRect(575, 240, 86, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.power_input_3_4.setFont(font)
        self.power_input_3_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_4.setFrameShape(QtWidgets.QFrame.Panel)
        self.power_input_3_4.setLineWidth(2)
        self.power_input_3_4.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_3_4.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_3_4.setObjectName("power_input_3_4")
        self.power_input_3_6 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_3_6.setGeometry(QtCore.QRect(315, 280, 120, 25))
        self.power_input_3_6.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_6.setObjectName("power_input_3_6")
        self.power_input_3_7 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_3_7.setGeometry(QtCore.QRect(445, 280, 120, 25))
        self.power_input_3_7.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_7.setObjectName("power_input_3_7")
        self.power_input_3_5 = QtWidgets.QComboBox(self.widget_5)
        self.power_input_3_5.setGeometry(QtCore.QRect(185, 280, 120, 25))
        self.power_input_3_5.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_5.setObjectName("power_input_3_5")
        self.power_input_3_8 = myTextEdit(self.widget_5)
        self.power_input_3_8.setGeometry(QtCore.QRect(575, 280, 86, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.power_input_3_8.setFont(font)
        self.power_input_3_8.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.power_input_3_8.setFrameShape(QtWidgets.QFrame.Panel)
        self.power_input_3_8.setLineWidth(2)
        self.power_input_3_8.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_3_8.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.power_input_3_8.setObjectName("power_input_3_8")
        self.widget_6 = QtWidgets.QWidget(self.frame)
        self.widget_6.setEnabled(True)
        self.widget_6.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_6.setObjectName("widget_6")
        self.listview_var_1 = QtWidgets.QTableWidget(self.widget_6)
        self.listview_var_1.setGeometry(QtCore.QRect(10, 50, 212, 331))
        self.listview_var_1.setObjectName("listview_var_1")
        self.listview_var_1.setColumnCount(3)
        self.listview_var_1.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_1.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_1.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_1.setHorizontalHeaderItem(2, item)
        self.listview_var_1.horizontalHeader().setDefaultSectionSize(70)
        self.listview_var_1.verticalHeader().setVisible(False)
        self.listview_var_1.verticalHeader().setDefaultSectionSize(20)
        self.listview_var_2 = QtWidgets.QTableWidget(self.widget_6)
        self.listview_var_2.setGeometry(QtCore.QRect(230, 50, 212, 331))
        self.listview_var_2.setObjectName("listview_var_2")
        self.listview_var_2.setColumnCount(3)
        self.listview_var_2.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_2.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_2.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_2.setHorizontalHeaderItem(2, item)
        self.listview_var_2.horizontalHeader().setDefaultSectionSize(70)
        self.listview_var_2.verticalHeader().setVisible(False)
        self.listview_var_2.verticalHeader().setDefaultSectionSize(20)
        self.listview_var_3 = QtWidgets.QTableWidget(self.widget_6)
        self.listview_var_3.setGeometry(QtCore.QRect(450, 50, 221, 331))
        self.listview_var_3.setObjectName("listview_var_3")
        self.listview_var_3.setColumnCount(3)
        self.listview_var_3.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_3.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_3.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_var_3.setHorizontalHeaderItem(2, item)
        self.listview_var_3.horizontalHeader().setDefaultSectionSize(70)
        self.listview_var_3.verticalHeader().setVisible(False)
        self.listview_var_3.verticalHeader().setDefaultSectionSize(20)
        self.var_input_1 = myTextEdit(self.widget_6)
        self.var_input_1.setGeometry(QtCore.QRect(10, 20, 102, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.var_input_1.setFont(font)
        self.var_input_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_input_1.setFrameShape(QtWidgets.QFrame.Panel)
        self.var_input_1.setLineWidth(2)
        self.var_input_1.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.var_input_1.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.var_input_1.setObjectName("var_input_1")
        self.var_input_2 = myTextEdit(self.widget_6)
        self.var_input_2.setGeometry(QtCore.QRect(230, 20, 102, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.var_input_2.setFont(font)
        self.var_input_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_input_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.var_input_2.setLineWidth(2)
        self.var_input_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.var_input_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.var_input_2.setObjectName("var_input_2")
        self.var_input_3 = myTextEdit(self.widget_6)
        self.var_input_3.setGeometry(QtCore.QRect(450, 20, 102, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.var_input_3.setFont(font)
        self.var_input_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_input_3.setFrameShape(QtWidgets.QFrame.Panel)
        self.var_input_3.setLineWidth(2)
        self.var_input_3.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.var_input_3.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.var_input_3.setObjectName("var_input_3")
        self.var_input_4 = QtWidgets.QPushButton(self.widget_6)
        self.var_input_4.setGeometry(QtCore.QRect(120, 20, 50, 25))
        self.var_input_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_input_4.setObjectName("var_input_4")
        self.var_input_5 = QtWidgets.QPushButton(self.widget_6)
        self.var_input_5.setGeometry(QtCore.QRect(340, 20, 50, 25))
        self.var_input_5.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_input_5.setObjectName("var_input_5")
        self.var_input_6 = QtWidgets.QPushButton(self.widget_6)
        self.var_input_6.setGeometry(QtCore.QRect(560, 20, 50, 25))
        self.var_input_6.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_input_6.setObjectName("var_input_6")
        self.var_save_1 = QtWidgets.QPushButton(self.widget_6)
        self.var_save_1.setGeometry(QtCore.QRect(170, 20, 50, 25))
        self.var_save_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_save_2 = QtWidgets.QPushButton(self.widget_6)
        self.var_save_2.setGeometry(QtCore.QRect(390, 20, 50, 25))
        self.var_save_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.var_save_3 = QtWidgets.QPushButton(self.widget_6)
        self.var_save_3.setGeometry(QtCore.QRect(610, 20, 50, 25))
        self.var_save_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.widget_7 = QtWidgets.QWidget(self.frame)
        self.widget_7.setEnabled(True)
        self.widget_7.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_7.setObjectName("widget_7")
        self.listview_diy = QtWidgets.QTableWidget(self.widget_7)
        self.listview_diy.setGeometry(QtCore.QRect(10, 50, 661, 331))
        self.listview_diy.setObjectName("listview_diy")
        self.listview_diy.setColumnCount(6)
        self.listview_diy.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.listview_diy.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_diy.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_diy.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_diy.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_diy.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.listview_diy.setHorizontalHeaderItem(5, item)
        self.listview_diy.horizontalHeader().setDefaultSectionSize(100)
        self.listview_diy.verticalHeader().setVisible(False)
        self.listview_diy.verticalHeader().setDefaultSectionSize(17)
        self.diy_input_1 = myTextEdit(self.widget_7)
        self.diy_input_1.setGeometry(QtCore.QRect(10, 20, 102, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.diy_input_2 = QtWidgets.QPushButton(self.widget_7)
        self.diy_input_2.setGeometry(QtCore.QRect(10, 20, 102, 25))
        self.diy_input_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.diy_input_2.setObjectName("diy_input_2")
        self.diy_input_4 = QtWidgets.QComboBox(self.widget_7)
        self.diy_input_4.setGeometry(QtCore.QRect(520, 20, 151, 25))
        self.diy_input_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.diy_input_4.setEditable(False)
        self.diy_input_4.setObjectName("diy_input_4")
        self.widget_8 = QtWidgets.QWidget(self.frame)
        self.widget_8.setEnabled(True)
        self.widget_8.setGeometry(QtCore.QRect(0, 0, 681, 391))
        self.widget_8.setObjectName("widget_8")
        self.listview_mk = QtWidgets.QListWidget(self.widget_8)
        self.listview_mk.setGeometry(QtCore.QRect(10, 13, 145, 365))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.listview_mk.setFont(font)
        self.listview_mk.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.listview_mk.setFrameShape(QtWidgets.QFrame.Panel)
        self.listview_mk.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.listview_mk.setLineWidth(2)
        self.listview_mk.setAutoScroll(True)
        self.listview_mk.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)
        self.listview_mk.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.listview_mk.setObjectName("listview_mk")
        self.item_save_4 = QtWidgets.QPushButton(self.widget_8)
        self.item_save_4.setGeometry(QtCore.QRect(550, 320, 121, 51))
        self.item_save_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.item_save_4.setObjectName("item_save_4")
        self.mk_1_1 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_1.setGeometry(QtCore.QRect(175, 40, 51, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_1.setFont(font)
        self.mk_1_1.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_1.setObjectName("mk_1_1")
        self.mk_input_1_1 = QtWidgets.QComboBox(self.widget_8)
        self.mk_input_1_1.setGeometry(QtCore.QRect(230, 40, 151, 25))
        self.mk_input_1_1.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_1.setObjectName("mk_input_1_1")
        self.mk_input_1_2 = myTextEdit(self.widget_8)
        self.mk_input_1_2.setGeometry(QtCore.QRect(480, 40, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.mk_input_1_2.setFont(font)
        self.mk_input_1_2.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_2.setFrameShape(QtWidgets.QFrame.Panel)
        self.mk_input_1_2.setLineWidth(2)
        self.mk_input_1_2.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_2.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_2.setObjectName("mk_input_1_2")
        self.mk_1_2 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_2.setGeometry(QtCore.QRect(405, 40, 71, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_2.setFont(font)
        self.mk_1_2.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_2.setObjectName("mk_1_2")
        self.mk_input_1_4 = myTextEdit(self.widget_8)
        self.mk_input_1_4.setGeometry(QtCore.QRect(480, 80, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.mk_input_1_4.setFont(font)
        self.mk_input_1_4.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_4.setFrameShape(QtWidgets.QFrame.Panel)
        self.mk_input_1_4.setLineWidth(2)
        self.mk_input_1_4.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_4.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_4.setObjectName("mk_input_1_4")
        self.mk_1_4 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_4.setGeometry(QtCore.QRect(405, 80, 71, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_4.setFont(font)
        self.mk_1_4.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_4.setObjectName("mk_1_4")
        self.mk_1_3 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_3.setGeometry(QtCore.QRect(175, 80, 51, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_3.setFont(font)
        self.mk_1_3.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_3.setObjectName("mk_1_3")
        self.mk_input_1_3 = QtWidgets.QComboBox(self.widget_8)
        self.mk_input_1_3.setGeometry(QtCore.QRect(230, 80, 151, 25))
        self.mk_input_1_3.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_3.setObjectName("mk_input_1_3")
        self.mk_input_1_6 = myTextEdit(self.widget_8)
        self.mk_input_1_6.setGeometry(QtCore.QRect(480, 120, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.mk_input_1_6.setFont(font)
        self.mk_input_1_6.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_6.setFrameShape(QtWidgets.QFrame.Panel)
        self.mk_input_1_6.setLineWidth(2)
        self.mk_input_1_6.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_6.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_6.setObjectName("mk_input_1_6")
        self.mk_1_5 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_5.setGeometry(QtCore.QRect(175, 120, 51, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_5.setFont(font)
        self.mk_1_5.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_5.setObjectName("mk_1_5")
        self.mk_input_1_5 = QtWidgets.QComboBox(self.widget_8)
        self.mk_input_1_5.setGeometry(QtCore.QRect(230, 120, 151, 25))
        self.mk_input_1_5.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_5.setObjectName("mk_input_1_5")
        self.mk_1_6 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_6.setGeometry(QtCore.QRect(405, 120, 71, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_6.setFont(font)
        self.mk_1_6.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_6.setObjectName("mk_1_6")
        self.mk_1_8 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_8.setGeometry(QtCore.QRect(405, 160, 71, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_8.setFont(font)
        self.mk_1_8.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_8.setObjectName("mk_1_8")
        self.mk_1_7 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_7.setGeometry(QtCore.QRect(175, 160, 51, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_7.setFont(font)
        self.mk_1_7.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_7.setObjectName("mk_1_7")
        self.mk_input_1_8 = myTextEdit(self.widget_8)
        self.mk_input_1_8.setGeometry(QtCore.QRect(480, 160, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.mk_input_1_8.setFont(font)
        self.mk_input_1_8.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_8.setFrameShape(QtWidgets.QFrame.Panel)
        self.mk_input_1_8.setLineWidth(2)
        self.mk_input_1_8.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_8.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_8.setObjectName("mk_input_1_8")
        self.mk_input_1_7 = QtWidgets.QComboBox(self.widget_8)
        self.mk_input_1_7.setGeometry(QtCore.QRect(230, 160, 151, 25))
        self.mk_input_1_7.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_7.setObjectName("mk_input_1_7")
        self.mk_1_10 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_10.setGeometry(QtCore.QRect(405, 200, 71, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_10.setFont(font)
        self.mk_1_10.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_10.setObjectName("mk_1_10")
        self.mk_1_9 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_9.setGeometry(QtCore.QRect(175, 200, 51, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_9.setFont(font)
        self.mk_1_9.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_9.setObjectName("mk_1_9")
        self.mk_input_1_9 = QtWidgets.QComboBox(self.widget_8)
        self.mk_input_1_9.setGeometry(QtCore.QRect(230, 200, 151, 25))
        self.mk_input_1_9.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_9.setObjectName("mk_input_1_9")
        self.mk_input_1_10 = myTextEdit(self.widget_8)
        self.mk_input_1_10.setGeometry(QtCore.QRect(480, 200, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.mk_input_1_10.setFont(font)
        self.mk_input_1_10.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_10.setFrameShape(QtWidgets.QFrame.Panel)
        self.mk_input_1_10.setLineWidth(2)
        self.mk_input_1_10.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_10.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_10.setObjectName("mk_input_1_10")
        self.mk_1_11 = QtWidgets.QLabel(self.widget_8)
        self.mk_1_11.setGeometry(QtCore.QRect(175, 250, 71, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.mk_1_11.setFont(font)
        self.mk_1_11.setStyleSheet("color:rgb(0,0,0);")
        self.mk_1_11.setObjectName("mk_1_11")
        self.mk_input_1_11 = QtWidgets.QTextEdit(self.widget_8)
        self.mk_input_1_11.setGeometry(QtCore.QRect(235, 250, 136, 25))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(9)
        self.mk_input_1_11.setFont(font)
        self.mk_input_1_11.setStyleSheet("background-color:rgb(255, 255, 255);\n"
"color:rgb(0,0,0);")
        self.mk_input_1_11.setFrameShape(QtWidgets.QFrame.Panel)
        self.mk_input_1_11.setLineWidth(2)
        self.mk_input_1_11.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_11.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarAlwaysOff)
        self.mk_input_1_11.setObjectName("mk_input_1_11")
        self.widget_1.raise_()
        self.widget_2.raise_()
        self.widget_3.raise_()
        self.widget_4.raise_()
        self.widget_5.raise_()
        self.widget_6.raise_()
        self.widget_0.raise_()
        self.widget_7.raise_()
        self.label_title = QtWidgets.QLabel(self.centralwidget)
        self.label_title.setGeometry(QtCore.QRect(18, 67, 36, 20))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(10)
        font.setBold(False)
        font.setWeight(50)
        self.label_title.setFont(font)
        self.label_title.setAutoFillBackground(True)
        self.label_title.setScaledContents(False)
        self.label_title.setAlignment(QtCore.Qt.AlignCenter)
        self.label_title.setObjectName("label_title")
        self.label_pivot = QtWidgets.QLabel(self.centralwidget)
        self.label_pivot.setGeometry(QtCore.QRect(10, 11, 52, 50))
        self.label_pivot.setAutoFillBackground(False)
        self.label_pivot.setStyleSheet("background-color:rgb(255, 255, 255)")
        self.label_pivot.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_pivot.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.label_pivot.setLineWidth(2)
        self.label_pivot.setMidLineWidth(1)
        self.label_pivot.setText("")
        self.label_pivot.setObjectName("label_pivot")
        self.label_window1 = QtWidgets.QLabel(self.centralwidget)
        self.label_window1.setGeometry(QtCore.QRect(70, 11, 200, 24))
        self.label_window1.setAutoFillBackground(False)
        self.label_window1.setStyleSheet("background-color:rgb(5,5,5);\n"
"color:rgb(0,255,0);")
        self.label_window1.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_window1.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.label_window1.setLineWidth(1)
        self.label_window1.setAlignment(QtCore.Qt.AlignLeading|QtCore.Qt.AlignLeft|QtCore.Qt.AlignVCenter)
        self.label_window1.setObjectName("label_window1")
        self.label_window2 = QtWidgets.QLabel(self.centralwidget)
        self.label_window2.setGeometry(QtCore.QRect(70, 36, 200, 24))
        self.label_window2.setAutoFillBackground(False)
        self.label_window2.setStyleSheet("background-color:rgb(5,5,5);\n"
"color:rgb(0,255,0);")
        self.label_window2.setFrameShape(QtWidgets.QFrame.Panel)
        self.label_window2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.label_window2.setLineWidth(1)
        self.label_window2.setObjectName("label_window2")
        self.label_help = QtWidgets.QLabel(self.centralwidget)
        self.label_help.setGeometry(QtCore.QRect(300, 30, 361, 16))
        font = QtGui.QFont()
        font.setFamily("黑体")
        font.setPointSize(9)
        font.setBold(False)
        font.setWeight(50)
        self.label_help.setFont(font)
        self.label_help.setStyleSheet("color:rgb(255, 0, 4);")
        self.label_help.setFrameShape(QtWidgets.QFrame.NoFrame)
        self.label_help.setFrameShadow(QtWidgets.QFrame.Plain)
        self.label_help.setTextFormat(QtCore.Qt.AutoText)
        self.label_help.setObjectName("label_help")
        self.version_0 = QtWidgets.QRadioButton(self.centralwidget)
        self.version_0.setGeometry(QtCore.QRect(100, 475, 50, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.version_0.setFont(font)
        self.version_0.setObjectName("version_0")
        self.version_1 = QtWidgets.QRadioButton(self.centralwidget)
        self.version_1.setGeometry(QtCore.QRect(20, 475, 91, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.version_1.setFont(font)
        self.version_1.setObjectName("version_1")
        self.version_2 = QtWidgets.QRadioButton(self.centralwidget)
        self.version_2.setGeometry(QtCore.QRect(160, 475, 50, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.version_2.setFont(font)
        self.version_2.setObjectName("version_2")
        self.version_3 = QtWidgets.QRadioButton(self.centralwidget)
        self.version_3.setGeometry(QtCore.QRect(220, 475, 50, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.version_3.setFont(font)
        self.version_3.setObjectName("version_3")
        self.version_4 = QtWidgets.QRadioButton(self.centralwidget)
        self.version_4.setGeometry(QtCore.QRect(280, 475, 50, 19))
        font = QtGui.QFont()
        font.setFamily("微软雅黑")
        self.version_4.setFont(font)
        self.version_4.setObjectName("version_4")
        self.buttonGroup=QtWidgets.QButtonGroup(self.centralwidget)
        self.buttonGroup.addButton(self.version_0)
        self.buttonGroup.addButton(self.version_1)
        self.buttonGroup.addButton(self.version_2)
        self.buttonGroup.addButton(self.version_3)
        self.buttonGroup.addButton(self.version_4)
        MainWindow.setCentralWidget(self.centralwidget)
        self.toolBar = QtWidgets.QToolBar(MainWindow)
        self.toolBar.setEnabled(False)
        self.toolBar.setMovable(False)
        self.toolBar.setObjectName("toolBar")
        MainWindow.addToolBar(QtCore.Qt.TopToolBarArea, self.toolBar)
        self.action_C = QtWidgets.QAction(MainWindow)
        self.action_C.setObjectName("action_C")
        self.action_M = QtWidgets.QAction(MainWindow)
        self.action_M.setObjectName("action_M")
        self.action_B = QtWidgets.QAction(MainWindow)
        self.action_B.setObjectName("action_B")
        self.action_W = QtWidgets.QAction(MainWindow)
        self.action_W.setObjectName("action_W")
        self.action_T = QtWidgets.QAction(MainWindow)
        self.action_T.setObjectName("action_T")
        self.action_V = QtWidgets.QAction(MainWindow)
        self.action_V.setObjectName("action_V")
        self.action_D = QtWidgets.QAction(MainWindow)
        self.action_D.setObjectName("action_D")
        self.action_K = QtWidgets.QAction(MainWindow)
        self.action_K.setObjectName("action_K")
        self.toolBar.addAction(self.action_C)
        self.toolBar.addAction(self.action_M)
        self.toolBar.addAction(self.action_B)
        self.toolBar.addAction(self.action_W)
        self.toolBar.addAction(self.action_T)
        self.toolBar.addAction(self.action_K)
        self.toolBar.addAction(self.action_V)
        self.toolBar.addAction(self.action_D)

        self.retranslateUi(MainWindow)
        self.otherSettings(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "by Puluo"))
        self.checkBox_1.setText(_translate("MainWindow", "可控制敌军和友军"))
        self.checkBox_2.setText(_translate("MainWindow", "不分敌我"))
        self.checkBox_3.setText(_translate("MainWindow", "禁止AI行动"))
        self.checkBox_4.setText(_translate("MainWindow", "待命后可移动"))
        self.checkBox_5.setText(_translate("MainWindow", "移动力 = 255"))
        self.checkBox_6.setText(_translate("MainWindow", "穿越移动"))
        self.checkBox_7.setText(_translate("MainWindow", "自动回归"))
        self.checkBox_8.setText(_translate("MainWindow", "托管我军主动出击"))
        self.checkBox_9.setText(_translate("MainWindow", "我军自动复活"))
        self.data_1.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">R形象</p></body></html>"))
        self.data_2.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">S形象</p></body></html>"))
        self.data_3.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">头像</p></body></html>"))
        self.data_4.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">攻击力</p></body></html>"))
        self.data_5.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">防御力</p></body></html>"))
        self.data_6.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">精神力</p></body></html>"))
        self.data_7.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">爆发力</p></body></html>"))
        self.data_8.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">士气</p></body></html>"))
        self.data_9.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">HP上限</p></body></html>"))
        self.data_10.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">MP上限</p></body></html>"))
        self.data_11.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">我军</p></body></html>"))
        self.data_12.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">等级</p></body></html>"))
        self.data_13.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">经验</p></body></html>"))
        self.data_14.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">武力</p></body></html>"))
        self.data_15.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">统率</p></body></html>"))
        self.data_16.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">智力</p></body></html>"))
        self.data_17.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">敏捷</p></body></html>"))
        self.data_18.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">运气</p></body></html>"))
        self.data_19.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">出阵</p></body></html>"))
        self.data_20.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">撤退</p></body></html>"))
        self.data_21.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">武功勋</p></body></html>"))
        self.data_22.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">统功勋</p></body></html>"))
        self.data_23.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">智功勋</p></body></html>"))
        self.data_24.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">敏功勋</p></body></html>"))
        self.data_25.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">运功勋</p></body></html>"))
        self.data_26.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">幸存</p></body></html>"))
        self.data_27.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">6号(2</p></body></html>"))
        self.data_28.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">44号(2</p></body></html>"))
        self.data_29.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">46号(2</p></body></html>"))
        self.data_30.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">杀敌数</p></body></html>"))
        self.data_31.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">兵种</p></body></html>"))
        self.data_32.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">武器</p></body></html>"))
        self.data_33.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">等级</p></body></html>"))
        self.data_34.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">经验</p></body></html>"))
        self.data_35.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">防具</p></body></html>"))
        self.data_36.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">等级</p></body></html>"))
        self.data_37.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">经验</p></body></html>"))
        self.data_38.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">辅助</p></body></html>"))
        self.data_save.setText(_translate("MainWindow", "保存"))
        self.data_recal.setText(_translate("MainWindow", "能力重新计算"))
        self.war_2.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">HP</p></body></html>"))
        self.war_save.setText(_translate("MainWindow", "保存"))
        self.war_kind_1.setText(_translate("MainWindow", "我"))
        self.war_kind_2.setText(_translate("MainWindow", "友"))
        self.war_kind_3.setText(_translate("MainWindow", "敌"))
        self.war_connect.setText(_translate("MainWindow", "连接至人物"))
        self.war_3.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">MP</p></body></html>"))
        self.war_4.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">SP</p></body></html>"))
        self.war_5.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">麻痹</p></body></html>"))
        self.war_6.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">禁咒</p></body></html>"))
        self.war_7.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">混乱</p></body></html>"))
        self.war_8.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">中毒</p></body></html>"))
        self.war_9.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">X</p></body></html>"))
        self.war_10.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">Y</p></body></html>"))
        self.war_11.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">AI</p></body></html>"))
        self.war_input_11.setItemText(0, _translate("MainWindow", "被动出击"))
        self.war_input_11.setItemText(1, _translate("MainWindow", "主动出击"))
        self.war_input_11.setItemText(2, _translate("MainWindow", "坚守原地"))
        self.war_input_11.setItemText(3, _translate("MainWindow", "攻击武将"))
        self.war_input_11.setItemText(4, _translate("MainWindow", "到指定点"))
        self.war_input_11.setItemText(5, _translate("MainWindow", "跟随武将"))
        self.war_input_11.setItemText(6, _translate("MainWindow", "逃到指定点"))
        self.war_12.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">武将</p></body></html>"))
        self.war_13.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">X1</p></body></html>"))
        self.war_14.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">Y1</p></body></html>"))
        self.war_15.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">行动</p></body></html>"))
        self.war_16.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">方向</p></body></html>"))
        self.war_input_16.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_16.setItemText(1, _translate("MainWindow", "上"))
        self.war_input_16.setItemText(2, _translate("MainWindow", "右"))
        self.war_input_16.setItemText(3, _translate("MainWindow", "下"))
        self.war_input_16.setItemText(4, _translate("MainWindow", "左"))
        self.war_input_17.setItemText(0, _translate("MainWindow", "减少"))
        self.war_input_17.setItemText(1, _translate("MainWindow", "正常"))
        self.war_input_17.setItemText(2, _translate("MainWindow", "增加"))
        self.war_17.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">攻击</p></body></html>"))
        self.war_18.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">防御</p></body></html>"))
        self.war_input_18.setItemText(0, _translate("MainWindow", "减少"))
        self.war_input_18.setItemText(1, _translate("MainWindow", "正常"))
        self.war_input_18.setItemText(2, _translate("MainWindow", "增加"))
        self.war_input_19.setItemText(0, _translate("MainWindow", "减少"))
        self.war_input_19.setItemText(1, _translate("MainWindow", "正常"))
        self.war_input_19.setItemText(2, _translate("MainWindow", "增加"))
        self.war_19.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">精神</p></body></html>"))
        self.war_20.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">爆发</p></body></html>"))
        self.war_input_20.setItemText(0, _translate("MainWindow", "减少"))
        self.war_input_20.setItemText(1, _translate("MainWindow", "正常"))
        self.war_input_20.setItemText(2, _translate("MainWindow", "增加"))
        self.war_input_21.setItemText(0, _translate("MainWindow", "减少"))
        self.war_input_21.setItemText(1, _translate("MainWindow", "正常"))
        self.war_input_21.setItemText(2, _translate("MainWindow", "增加"))
        self.war_21.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">士气</p></body></html>"))
        self.war_input_22.setItemText(0, _translate("MainWindow", "减少"))
        self.war_input_22.setItemText(1, _translate("MainWindow", "正常"))
        self.war_input_22.setItemText(2, _translate("MainWindow", "增加"))
        self.war_22.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">移动</p></body></html>"))
        self.war_input_23.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_23.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_23.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_23.setItemText(3, _translate("MainWindow", "增加"))
        self.war_23.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">全部</p></body></html>"))
        self.war_lockadd.setText(_translate("MainWindow", "增加锁定"))
        self.war_locksub.setText(_translate("MainWindow", "移除锁定"))
        self.war_life.setText(_translate("MainWindow", "战场复活"))
        self.war_kill.setText(_translate("MainWindow", "区域灭敌"))
        self.war_24.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">回合上限</p></body></html>"))
        self.war_25.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">当前回合</p></body></html>"))
        self.war_26.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">下一关</p></body></html>"))
        self.war_input_27.setItemText(0, _translate("MainWindow", "晴"))
        self.war_input_27.setItemText(1, _translate("MainWindow", "阴"))
        self.war_input_27.setItemText(2, _translate("MainWindow", "小雨"))
        self.war_input_27.setItemText(3, _translate("MainWindow", "大雨"))
        self.war_input_27.setItemText(4, _translate("MainWindow", "雪"))
        self.war_27.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">天气</p></body></html>"))
        self.war_input_28.setItemText(0, _translate("MainWindow", "我"))
        self.war_input_28.setItemText(1, _translate("MainWindow", "友"))
        self.war_input_28.setItemText(2, _translate("MainWindow", "敌"))
        self.war_28.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">军</p></body></html>"))
        self.war_29.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">攻</p></body></html>"))
        self.war_input_29.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_29.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_29.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_29.setItemText(3, _translate("MainWindow", "增加"))
        self.war_input_30.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_30.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_30.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_30.setItemText(3, _translate("MainWindow", "增加"))
        self.war_30.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">防</p></body></html>"))
        self.war_31.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">精</p></body></html>"))
        self.war_input_31.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_31.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_31.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_31.setItemText(3, _translate("MainWindow", "增加"))
        self.war_input_32.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_32.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_32.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_32.setItemText(3, _translate("MainWindow", "增加"))
        self.war_32.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">爆</p></body></html>"))
        self.war_input_33.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_33.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_33.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_33.setItemText(3, _translate("MainWindow", "增加"))
        self.war_33.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">士</p></body></html>"))
        self.war_input_34.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_34.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_34.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_34.setItemText(3, _translate("MainWindow", "增加"))
        self.war_34.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">移</p></body></html>"))
        self.war_input_35.setItemText(0, _translate("MainWindow", "——"))
        self.war_input_35.setItemText(1, _translate("MainWindow", "减少"))
        self.war_input_35.setItemText(2, _translate("MainWindow", "正常"))
        self.war_input_35.setItemText(3, _translate("MainWindow", "增加"))
        self.war_35.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">全</p></body></html>"))
        self.war_36.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">X2</p></body></html>"))
        self.war_37.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">Y2</p></body></html>"))
        self.war_39.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">戮</p></body></html>"))
        self.war_38.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">22</p></body></html>"))
        self.war_40.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">2C</p></body></html>"))
        self.war_41.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">24</p></body></html>"))
        self.war_42.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">2A</p></body></html>"))
        self.war_43.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">26</p></body></html>"))
        self.war_44.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">2E</p></body></html>"))
        self.war_45.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">28</p></body></html>"))
        self.war_46.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">控</p></body></html>"))
        self.item_save.setText(_translate("MainWindow", "保存"))
        self.item_1.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\"><span style=\" font-size:9pt;\">装备</span></p></body></html>"))
        self.item_2.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">装备等级</p></body></html>"))
        self.item_3.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">装备经验</p></body></html>"))
        self.item_all_1.setText(_translate("MainWindow", "全宝物"))
        self.item_all_2.setText(_translate("MainWindow", "全道具"))
        self.item_all_3.setText(_translate("MainWindow", "清空仓库"))
        self.item_4.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">道具数量</p></body></html>"))
        self.item_5.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">金钱</p></body></html>"))
        self.item_6.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">忠奸度</p></body></html>"))
        self.item_7.setText(_translate("MainWindow", "<html><head/><body><p align=\"right\">功勋池</p></body></html>"))
        self.item_save_2.setText(_translate("MainWindow", "保存"))
        self.power_1.setText(_translate("MainWindow", "<html><head/><body><p>天赋</p></body></html>"))
        self.power_2.setText(_translate("MainWindow", "<html><head/><body><p>专属</p></body></html>"))
        self.power_3.setText(_translate("MainWindow", "<html><head/><body><p>套装</p></body></html>"))
        item = self.listview_var_1.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "布尔"))
        item = self.listview_var_1.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "值"))
        item = self.listview_var_1.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "地址"))
        item = self.listview_var_2.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "整型"))
        item = self.listview_var_2.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "值"))
        item = self.listview_var_2.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "地址"))
        item = self.listview_var_3.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "指针"))
        item = self.listview_var_3.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "值"))
        item = self.listview_var_3.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "地址"))
        self.var_input_4.setText(_translate("MainWindow", "跳转"))
        self.var_input_5.setText(_translate("MainWindow", "跳转"))
        self.var_input_6.setText(_translate("MainWindow", "跳转"))
        self.var_save_1.setText(_translate("MainWindow", "保存"))
        self.var_save_2.setText(_translate("MainWindow", "保存"))
        self.var_save_3.setText(_translate("MainWindow", "保存"))
        item = self.listview_diy.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "变量名"))
        item = self.listview_diy.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "值"))
        item = self.listview_diy.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "值解释"))
        item = self.listview_diy.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "地址"))
        item = self.listview_diy.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "字节数"))
        item = self.listview_diy.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "注释"))
        self.diy_input_2.setText(_translate("MainWindow", "保存值"))
        self.item_save_4.setText(_translate("MainWindow", "保存"))
        self.mk_1_1.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">武将1</span></p></body></html>"))
        self.mk_1_2.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">领悟等级</span></p></body></html>"))
        self.mk_1_4.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">领悟等级</span></p></body></html>"))
        self.mk_1_3.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">武将2</span></p></body></html>"))
        self.mk_1_5.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">武将3</span></p></body></html>"))
        self.mk_1_6.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">领悟等级</span></p></body></html>"))
        self.mk_1_8.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">领悟等级</span></p></body></html>"))
        self.mk_1_7.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">武将4</span></p></body></html>"))
        self.mk_1_10.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">领悟等级</span></p></body></html>"))
        self.mk_1_9.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">武将5</span></p></body></html>"))
        self.mk_1_11.setText(_translate("MainWindow", "<html><head/><body><p><span style=\" font-size:10pt;\">效果值</span></p></body></html>"))
        self.label_title.setText(_translate("MainWindow", "控制"))
        self.label_window1.setText(_translate("MainWindow", "窗体名称"))
        self.label_window2.setText(_translate("MainWindow", "进程说明"))
        self.label_help.setText(_translate("MainWindow", "将左方的\"准心图案\"拖拽至游戏中即可开始调试。"))
        self.version_0.setText(_translate("MainWindow", "6.4"))
        self.version_1.setText(_translate("MainWindow", "自动"))
        self.version_2.setText(_translate("MainWindow", "6.3"))
        self.version_3.setText(_translate("MainWindow", "6.2"))
        self.version_4.setText(_translate("MainWindow", "6.1"))
        self.action_C.setText(_translate("MainWindow", "控制(C)"))
        self.action_M.setText(_translate("MainWindow", "人物(M)"))
        self.action_B.setText(_translate("MainWindow", "战场(B)"))
        self.action_W.setText(_translate("MainWindow", "仓库(W)"))
        self.action_T.setText(_translate("MainWindow", "天赋(T)"))
        self.action_V.setText(_translate("MainWindow", "变量(V)"))
        self.action_D.setText(_translate("MainWindow", "自定义(D)"))
        self.action_K.setText(_translate("MainWindow", "必杀(K)"))
        self.war_input_47.setText("0")
        self.war_input_48.setText("0")
        self.war_input_49.setText("255")
        self.war_input_50.setText("255")
        self.war_input_51.setText("0")
        self.war_input_52.setText("0")
        self.war_input_53.setText("0")
        self.war_input_54.setText("0")

    #这里记录一些乱七八糟的变量和信号槽链接
    def otherSettings(self, MainWindow):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("myappid")
        self.setWindowIcon(QIcon('logo.ico'))
        self.mouse_capture = False
        self.process = NULL
        self.p = NULL
        self.md = NULL
        self.ok = False
        #窗口初始化
        self.widget_0.hide()
        self.widget_1.show()
        self.widget_1.setEnabled(False)
        self.widget_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()
        self.widget_5.hide()
        self.widget_6.hide()
        self.widget_7.hide()
        self.widget_8.hide()
        pix = QtGui.QPixmap('准星.png')
        self.label_pivot.setPixmap(pix)
        self.setFocusPolicy(QtCore.Qt.ClickFocus)
        self.setContextMenuPolicy(QtCore.Qt.NoContextMenu)

        #页面控件链接
        self.checkBox_1.clicked.connect(lambda: self.onButtonClick(1))
        self.checkBox_2.clicked.connect(lambda: self.onButtonClick(2))
        self.checkBox_3.clicked.connect(lambda: self.onButtonClick(3))
        self.checkBox_4.clicked.connect(lambda: self.onButtonClick(4))
        self.checkBox_5.clicked.connect(lambda: self.onButtonClick(5))
        self.checkBox_6.clicked.connect(lambda: self.onButtonClick(6))
        self.checkBox_7.clicked.connect(lambda: self.onButtonClick(7))
        self.checkBox_8.clicked.connect(lambda: self.onButtonClick(8))
        self.checkBox_8.clicked.connect(lambda: self.onButtonClick(8))
        self.checkBox_9.clicked.connect(lambda: self.onButtonClick(9))

        self.listview_data.itemSelectionChanged.connect(lambda: self.onData())
        self.data_save.clicked.connect(lambda: self.saveData())
        self.data_recal.clicked.connect(lambda: self.recal())

        self.war_kind_1.clicked.connect(lambda: self.onWar(0))
        self.war_kind_2.clicked.connect(lambda: self.onWar(0))
        self.war_kind_3.clicked.connect(lambda: self.onWar(0))
        self.listview_war.itemSelectionChanged.connect(lambda: self.onWar(1))
        self.war_input_11.currentIndexChanged.connect(lambda: self.refreshFangzhen())
        self.war_connect.clicked.connect(lambda: self.onConnect())
        self.war_kill.clicked.connect(lambda: self.onKill())
        self.war_life.clicked.connect(lambda: self.onLife())
        self.war_save.clicked.connect(lambda: self.saveWar())
        self.war_lockadd.clicked.connect(lambda: self.onLock())
        self.war_locksub.clicked.connect(lambda: self.offLock())

        self.listview_item.itemSelectionChanged.connect(lambda: self.onItem())
        self.listview_item_2.itemSelectionChanged.connect(lambda: self.onItem())
        self.item_save.clicked.connect(lambda: self.saveItem())
        self.item_all_1.clicked.connect(lambda: self.allItem(1))
        self.item_all_2.clicked.connect(lambda: self.allItem(2))
        self.item_all_3.clicked.connect(lambda: self.allItem(3))

        self.listview_item_3.itemSelectionChanged.connect(lambda: self.onPower())
        self.item_save_2.clicked.connect(lambda: self.savePower())

        self.var_input_1.setText("0")
        self.var_input_2.setText("0")
        self.var_input_3.setText("0")
        self.listview_var_1.setColumnWidth(0,60)
        self.listview_var_1.setColumnWidth(1,55)
        self.listview_var_2.setColumnWidth(0,45)
        self.listview_var_2.setColumnWidth(1,75)
        self.listview_var_2.setColumnWidth(2,65)
        self.listview_var_3.setColumnWidth(0,45)
        self.listview_var_3.setColumnWidth(1,75)
        self.var_input_4.clicked.connect(lambda: self.onVar())
        self.var_input_5.clicked.connect(lambda: self.onVar())
        self.var_input_6.clicked.connect(lambda: self.onVar())
        self.var_save_1.clicked.connect(lambda: self.saveVar(1))
        self.var_save_2.clicked.connect(lambda: self.saveVar(2))
        self.var_save_3.clicked.connect(lambda: self.saveVar(3))

        self.listview_diy.setColumnWidth(0,100)
        self.listview_diy.setColumnWidth(1,80)
        self.listview_diy.setColumnWidth(2,90)
        self.listview_diy.setColumnWidth(3,70)
        self.listview_diy.setColumnWidth(4,45)
        self.listview_diy.setColumnWidth(5,230)
        self.diy_input_2.clicked.connect(lambda: self.saveDIY())
        self.diy_input_4.currentIndexChanged.connect(lambda: self.DIY_Page(1))

        self.listview_mk.itemSelectionChanged.connect(lambda: self.onMk())
        self.item_save_4.clicked.connect(lambda: self.saveMk())

        #控件属性设置
        self.my_thread = NULL
        self.item_input_1.setMaxVisibleItems(32)
        self.version_1.setChecked(True)
    
    #打开第一页
    def on_action_C_triggered(self):
        self.widget_1.show()
        self.widget_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()
        self.widget_5.hide()
        self.widget_6.hide()
        self.widget_7.hide()
        self.widget_8.hide()
        self.label_title.setText("控制")

    #打开第二页
    def on_action_M_triggered(self):
        self.widget_1.hide()
        self.widget_2.show()
        self.widget_3.hide()
        self.widget_4.hide()
        self.widget_5.hide()
        self.widget_6.hide()
        self.widget_7.hide()
        self.widget_8.hide()
        self.label_title.setText("人物")

    #打开第三页
    def on_action_B_triggered(self):
        self.widget_1.hide()
        self.widget_2.hide()
        self.widget_3.show()
        self.widget_4.hide()
        self.widget_5.hide()
        self.widget_6.hide()
        self.widget_7.hide()
        self.widget_8.hide()
        self.label_title.setText("战场")

    #打开第四页
    def on_action_W_triggered(self):
        self.widget_1.hide()
        self.widget_2.hide()
        self.widget_3.hide()
        self.widget_4.show()
        self.widget_5.hide()
        self.widget_6.hide()
        self.widget_7.hide()
        self.widget_8.hide()
        self.label_title.setText("仓库")

    #打开第五页
    def on_action_T_triggered(self):
        global version
        if version == -1:
            return
        self.widget_1.hide()
        self.widget_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()
        self.widget_5.show()
        self.widget_6.hide()
        self.widget_7.hide()
        self.widget_8.hide()
        self.label_title.setText("天赋")

    #打开第六页
    def on_action_V_triggered(self):
        global version
        if version == -1:
            return
        self.widget_1.hide()
        self.widget_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()
        self.widget_5.hide()
        self.widget_6.show()
        self.widget_7.hide()
        self.widget_8.hide()
        self.label_title.setText("变量")

    #打开第七页
    def on_action_D_triggered(self):
        global version
        if version == -1:
            return
        self.widget_1.hide()
        self.widget_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()
        self.widget_5.hide()
        self.widget_6.hide()
        self.widget_7.show()
        self.widget_8.hide()
        self.label_title.setText("自定")

    #打开第八页
    def on_action_K_triggered(self):
        global version
        if version == -1:
            return
        self.widget_1.hide()
        self.widget_2.hide()
        self.widget_3.hide()
        self.widget_4.hide()
        self.widget_5.hide()
        self.widget_6.hide()
        self.widget_7.hide()
        self.widget_8.show()
        self.label_title.setText("必杀")

    #扳手第一页功能实现
    def onButtonClick(self, n):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        global auto_life
        if n == 1:
            if self.checkBox_1.isChecked() == True:
                self.md.WriteProcessMemory(int(self.p), 0x43D574, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43D5A5, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43E359, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E748, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E749, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E754, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E755, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x455379, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
            else:
                self.md.WriteProcessMemory(int(self.p), 0x43D574, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43D5A5, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43E359, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E748, ctypes.byref(ctypes.c_int(0x75)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E749, ctypes.byref(ctypes.c_int(0xC8)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E754, ctypes.byref(ctypes.c_int(0x75)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44E755, ctypes.byref(ctypes.c_int(0xBC)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x455379, ctypes.byref(ctypes.c_int(0x74)), 1, None)
        if n == 2:
            if self.checkBox_2.isChecked() == True:
                #self.md.WriteProcessMemory(int(self.p), 0x4242AF, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x4242B0, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                if version == 0:
                    self.md.WriteProcessMemory(int(self.p), 0x4242AF, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437BC0, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437BC1, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x454405, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x454406, ctypes.byref(ctypes.c_int(0x90)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x455646, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
            else:
                #self.md.WriteProcessMemory(int(self.p), 0x4242AF, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x4242B0, ctypes.byref(ctypes.c_int(0x32)), 1, None)
                if version == 0:
                    self.md.WriteProcessMemory(int(self.p), 0x4242AF, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x4242B0, ctypes.byref(ctypes.c_int(0xDD)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437BC0, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437BC1, ctypes.byref(ctypes.c_int(0x34)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x454405, ctypes.byref(ctypes.c_int(0x75)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x454406, ctypes.byref(ctypes.c_int(0x27)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x455646, ctypes.byref(ctypes.c_int(0x75)), 1, None)
        if n == 3:
            if self.checkBox_3.isChecked() == True:
                self.md.WriteProcessMemory(int(self.p), 0x44E9D3, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
            else:
                self.md.WriteProcessMemory(int(self.p), 0x44E9D3, ctypes.byref(ctypes.c_int(0x74)), 1, None)
        if n == 4:
            if self.checkBox_4.isChecked() == True:
                self.md.WriteProcessMemory(int(self.p), 0x43D5DC, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
                #self.md.WriteProcessMemory(int(self.p), 0x470B8C, ctypes.byref(ctypes.c_int(0x42)), 1, None)
            else:
                self.md.WriteProcessMemory(int(self.p), 0x43D5DC, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                #self.md.WriteProcessMemory(int(self.p), 0x470B8C, ctypes.byref(ctypes.c_int(0x47)), 1, None)
        if n == 5:
            if self.checkBox_5.isChecked() == True:
                self.md.WriteProcessMemory(int(self.p), 0x43F74F, ctypes.byref(ctypes.c_int(0x33)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43F750, ctypes.byref(ctypes.c_int(0xC0)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43F751, ctypes.byref(ctypes.c_int(0x48)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43F752, ctypes.byref(ctypes.c_int(0xC3)), 1, None)
            else:
                self.md.WriteProcessMemory(int(self.p), 0x43F74F, ctypes.byref(ctypes.c_int(0x55)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43F750, ctypes.byref(ctypes.c_int(0x8B)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43F751, ctypes.byref(ctypes.c_int(0xEC)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x43F752, ctypes.byref(ctypes.c_int(0x83)), 1, None)
        if n == 6:
            if self.checkBox_6.isChecked() == True:
                self.md.WriteProcessMemory(int(self.p), 0x4387B7, ctypes.byref(ctypes.c_int(0xEB)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437D59, ctypes.byref(ctypes.c_int(0x33)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437D5A, ctypes.byref(ctypes.c_int(0xC0)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437D5B, ctypes.byref(ctypes.c_int(0xC3)), 1, None)
            else:
                self.md.WriteProcessMemory(int(self.p), 0x4387B7, ctypes.byref(ctypes.c_int(0x74)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437D59, ctypes.byref(ctypes.c_int(0x55)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437D5A, ctypes.byref(ctypes.c_int(0x8B)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x437D5B, ctypes.byref(ctypes.c_int(0xEC)), 1, None)
        if n == 7:
            if self.checkBox_7.isChecked() == True:
                data = ctypes.c_int()
                self.md.ReadProcessMemory(int(self.p), 0x44E570, ctypes.byref(data), 1, None)
                if data.value == 0xE8:
                    self.md.WriteProcessMemory(int(self.p), 0x44E571, ctypes.byref(ctypes.c_int(0x8B)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E572, ctypes.byref(ctypes.c_int(0x78)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E573, ctypes.byref(ctypes.c_int(0x03)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E574, ctypes.byref(ctypes.c_int(0x00)), 1, None)
                else:
                    self.md.WriteProcessMemory(int(self.p), 0x44E576, ctypes.byref(ctypes.c_int(0x86)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E577, ctypes.byref(ctypes.c_int(0x78)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E578, ctypes.byref(ctypes.c_int(0x03)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E579, ctypes.byref(ctypes.c_int(0x00)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44EA74, ctypes.byref(ctypes.c_int(0x88)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44EA75, ctypes.byref(ctypes.c_int(0x73)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44EA76, ctypes.byref(ctypes.c_int(0x03)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x44EA77, ctypes.byref(ctypes.c_int(0x00)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E00, ctypes.byref(ctypes.c_long(0x83EC8B55)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E04, ctypes.byref(ctypes.c_long(0x75FF04EC)), 4, None)
                if version >= 3:
                    self.md.WriteProcessMemory(int(self.p), 0x485E08, ctypes.byref(ctypes.c_long(0x9E8DE808)), 4, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E0C, ctypes.byref(ctypes.c_long(0x4D8B0004)), 4, None)
                else:
                    self.md.WriteProcessMemory(int(self.p), 0x485E08, ctypes.byref(ctypes.c_long(0xCF44E808)), 4, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E0C, ctypes.byref(ctypes.c_long(0x4D8BFFF8)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E10, ctypes.byref(ctypes.c_long(0xFFE18108)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E17, ctypes.byref(ctypes.c_long(0xC96B)), 2, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E19, ctypes.byref(ctypes.c_long(len_war)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E1A, ctypes.byref(ctypes.c_long(0x81)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E1B, ctypes.byref(ctypes.c_long(0xC1)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E1C, ctypes.byref(ctypes.c_long(addr_war)), 3, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E20, ctypes.byref(ctypes.c_long(0xB8FC4D89)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E24, ctypes.byref(ctypes.c_int(0x06)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E28, ctypes.byref(ctypes.c_long(0x4120D0F7)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E2C, ctypes.byref(ctypes.c_long(0x0D)), 1, None)
                if version >= 1:
                    self.md.WriteProcessMemory(int(self.p), 0x485E2D, ctypes.byref(ctypes.c_long(0xE831FF)), 3, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E30, ctypes.byref(ctypes.c_long(0xFFFB86A2)), 4, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E34, ctypes.byref(ctypes.c_long(0x00008868)), 4, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E38, ctypes.byref(ctypes.c_long(0x50066A00)), 4, None)
                else:
                    self.md.WriteProcessMemory(int(self.p), 0x485E2D, ctypes.byref(ctypes.c_long(0x00008868)), 4, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E31, ctypes.byref(ctypes.c_long(0x8B066A00)), 4, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E35, ctypes.byref(ctypes.c_long(0x71FFFC4D)), 4, None)
                    self.md.WriteProcessMemory(int(self.p), 0x485E39, ctypes.byref(ctypes.c_long(0x909004)), 3, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E3C, ctypes.byref(ctypes.c_long(0xE8)), 1, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E3D, ctypes.byref(ctypes.c_long(0xFFFB8869)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E41, ctypes.byref(ctypes.c_long(0xFE5DE58B)), 4, None)
                self.md.WriteProcessMemory(int(self.p), 0x485E45, ctypes.byref(ctypes.c_long(0x00C3FC4D)), 4, None)
            else:
                if version <= 2:
                    self.md.WriteProcessMemory(int(self.p), 0x44E571, ctypes.byref(ctypes.c_int(0xDD)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E572, ctypes.byref(ctypes.c_int(0x47)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E573, ctypes.byref(ctypes.c_int(0xFC)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44E574, ctypes.byref(ctypes.c_int(0xFF)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA74, ctypes.byref(ctypes.c_int(0xDA)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA75, ctypes.byref(ctypes.c_int(0x42)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA76, ctypes.byref(ctypes.c_int(0xFC)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA77, ctypes.byref(ctypes.c_int(0xFF)), 1, None)
                else:
                    data = ctypes.c_int()
                    self.md.ReadProcessMemory(int(self.p), 0x44E570, ctypes.byref(data), 1, None)
                    if data.value == 0xE8:
                        self.md.WriteProcessMemory(int(self.p), 0x44E571, ctypes.byref(ctypes.c_int(0x26)), 1, None)
                        self.md.WriteProcessMemory(int(self.p), 0x44E572, ctypes.byref(ctypes.c_int(0x17)), 1, None)
                        self.md.WriteProcessMemory(int(self.p), 0x44E573, ctypes.byref(ctypes.c_int(0x08)), 1, None)
                        self.md.WriteProcessMemory(int(self.p), 0x44E574, ctypes.byref(ctypes.c_int(0x00)), 1, None)
                    else:
                        self.md.WriteProcessMemory(int(self.p), 0x44E576, ctypes.byref(ctypes.c_int(0x21)), 1, None)
                        self.md.WriteProcessMemory(int(self.p), 0x44E577, ctypes.byref(ctypes.c_int(0x17)), 1, None)
                        self.md.WriteProcessMemory(int(self.p), 0x44E578, ctypes.byref(ctypes.c_int(0x08)), 1, None)
                        self.md.WriteProcessMemory(int(self.p), 0x44E579, ctypes.byref(ctypes.c_int(0x00)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA74, ctypes.byref(ctypes.c_int(0x23)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA75, ctypes.byref(ctypes.c_int(0x12)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA76, ctypes.byref(ctypes.c_int(0x08)), 1, None)
                    self.md.WriteProcessMemory(int(self.p), 0x44EA77, ctypes.byref(ctypes.c_int(0x00)), 1, None)
        if n == 8:
            if self.checkBox_8.isChecked() == True:
                for i in range(0,cnt_wo + cnt_you):
                    data = ctypes.c_int()
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war, ctypes.byref(data), 2, None)
                    if data.value == 65535:
                        continue
                    self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0xE, ctypes.byref(ctypes.c_int(1)), 1, None)
            else:
                for i in range(0,cnt_wo + cnt_you):
                    data = ctypes.c_int()
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war, ctypes.byref(data), 2, None)
                    if data.value == 65535:
                        continue
                    self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0xE, ctypes.byref(ctypes.c_int(7)), 1, None)
        '''if n == 9:
            if self.checkBox_9.isChecked() == True:
                self.md.WriteProcessMemory(int(self.p), 0x404388, ctypes.byref(ctypes.c_int(0xC3)), 1, None)
                if version == 0:
                    self.md.WriteProcessMemory(int(self.p), 0x4214A1, ctypes.byref(ctypes.c_int(0xC3)), 1, None)
                else:
                    self.md.WriteProcessMemory(int(self.p), 0x4214C9, ctypes.byref(ctypes.c_int(0xC3)), 1, None)
            else:
                self.md.WriteProcessMemory(int(self.p), 0x404388, ctypes.byref(ctypes.c_int(0x55)), 1, None)
                if version == 0:
                    self.md.WriteProcessMemory(int(self.p), 0x4214A1, ctypes.byref(ctypes.c_int(0x55)), 1, None)
                else:
                    self.md.WriteProcessMemory(int(self.p), 0x4214C9, ctypes.byref(ctypes.c_int(0xC3)), 1, None)'''
        if n == 9:
            auto_life = self.checkBox_9.isChecked()

    #扳手第二页人物data数据读入
    def onData(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        global cnt_item
        global version
        if len(self.listview_data.selectedIndexes())<=0:
            n = 0
        else:
            n = self.listview_data.selectedIndexes()[0].row()
        data = ctypes.c_int()
        #R形象
        self.md.ReadProcessMemory(int(self.p), 0x50F800+n*2, ctypes.byref(data), 2, None)
        self.data_input_1.setText(str(data.value))
        #S形象
        self.md.ReadProcessMemory(int(self.p), 0x501000+n*2, ctypes.byref(data), 2, None)
        self.data_input_2.setText(str(data.value))
        #头像
        self.md.ReadProcessMemory(int(self.p), 0x50F000+n*2, ctypes.byref(data), 2, None)
        self.data_input_3.setText(str(data.value))
        mem = ctypes.c_long()
        self.md.ReadProcessMemory(int(self.p), 0x4CEA00, ctypes.byref(mem), 4, None)
        #攻击力
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x11, ctypes.byref(data), 2, None)
        self.data_input_4.setText(str(data.value))
        #防御力
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x13, ctypes.byref(data), 2, None)
        self.data_input_5.setText(str(data.value))
        #精神力
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x15, ctypes.byref(data), 2, None)
        self.data_input_6.setText(str(data.value))
        #爆发力
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x17, ctypes.byref(data), 2, None)
        self.data_input_7.setText(str(data.value))
        #士气
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x19, ctypes.byref(data), 2, None)
        self.data_input_8.setText(str(data.value))
        #HP上限
        if version <= 1:
            self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x1B, ctypes.byref(data), 4, None)
        else:
            self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x1C, ctypes.byref(data), 4, None)
        self.data_input_9.setText(str(data.value))
        data = ctypes.c_int(0)
        #MP上限
        if version <= 1:
            self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x1F, ctypes.byref(data), 2, None)
        else:
            self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x20, ctypes.byref(data), 1, None)
        self.data_input_10.setText(str(data.value))
        data = ctypes.c_int(0)
        #我军
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x2A, ctypes.byref(data), 1, None)
        if data.value==0:
            self.data_input_11.setChecked(True)
        else:
            self.data_input_11.setChecked(False)
        #等级
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x2C, ctypes.byref(data), 1, None)
        self.data_input_12.setText(str(data.value))
        #经验
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x2D, ctypes.byref(data), 1, None)
        self.data_input_13.setText(str(data.value))
        #武力
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x21, ctypes.byref(data), 1, None)
        self.data_input_14.setText(str(data.value))
        #统率
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x22, ctypes.byref(data), 1, None)
        self.data_input_15.setText(str(data.value))
        #智力
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x23, ctypes.byref(data), 1, None)
        self.data_input_16.setText(str(data.value))
        #敏捷
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x24, ctypes.byref(data), 1, None)
        self.data_input_17.setText(str(data.value))
        #运气
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x25, ctypes.byref(data), 1, None)
        self.data_input_18.setText(str(data.value))
        #出场
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x27, ctypes.byref(data), 1, None)
        self.data_input_19.setText(str(data.value))
        #撤退
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x29, ctypes.byref(data), 1, None)
        self.data_input_20.setText(str(data.value))
        if version == 0:
            gongxun = 0x508000
        else:
            gongxun = 0x508400
        #武力功勋
        self.md.ReadProcessMemory(int(self.p), gongxun+10*n+0, ctypes.byref(data), 2, None)
        self.data_input_21.setText(str(data.value))
        #统率功勋
        self.md.ReadProcessMemory(int(self.p), gongxun+10*n+2, ctypes.byref(data), 2, None)
        self.data_input_22.setText(str(data.value))
        #智力功勋
        self.md.ReadProcessMemory(int(self.p), gongxun+10*n+4, ctypes.byref(data), 2, None)
        self.data_input_23.setText(str(data.value))
        #敏捷功勋
        self.md.ReadProcessMemory(int(self.p), gongxun+10*n+6, ctypes.byref(data), 2, None)
        self.data_input_24.setText(str(data.value))
        #运气功勋
        self.md.ReadProcessMemory(int(self.p), gongxun+10*n+8, ctypes.byref(data), 2, None)
        self.data_input_25.setText(str(data.value))
        #3
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x28, ctypes.byref(data), 1, None)
        self.data_input_26.setText(str(data.value))
        #6
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x6, ctypes.byref(data), 2, None)
        self.data_input_27.setText(str(data.value))
        #6
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x44, ctypes.byref(data), 2, None)
        self.data_input_28.setText(str(data.value))
        #6
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x46, ctypes.byref(data), 2, None)
        self.data_input_29.setText(str(data.value))
        #杀敌数
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x35, ctypes.byref(data), 2, None)
        self.data_input_30.setText(str(data.value))
        data = ctypes.c_int(0)
        #兵种
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x2B, ctypes.byref(data), 1, None)
        self.data_input_31.setCurrentIndex(data.value)
        #武器
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x2E, ctypes.byref(data), 1, None)
        self.data_input_32.setCurrentIndex(data.value)
        if data.value==255:
            self.data_input_32.setCurrentIndex(cnt_item)
        #等级
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x2F, ctypes.byref(data), 1, None)
        self.data_input_33.setText(str(data.value))
        #经验
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x30, ctypes.byref(data), 1, None)
        self.data_input_34.setText(str(data.value))
        #防具
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x31, ctypes.byref(data), 1, None)
        self.data_input_35.setCurrentIndex(data.value)
        if data.value==255:
            self.data_input_35.setCurrentIndex(cnt_item)
        #等级
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x32, ctypes.byref(data), 1, None)
        self.data_input_36.setText(str(data.value))
        #经验
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x33, ctypes.byref(data), 1, None)
        self.data_input_37.setText(str(data.value))
        #辅助
        self.md.ReadProcessMemory(int(self.p), mem.value+0x48*n+0x34, ctypes.byref(data), 1, None)
        self.data_input_38.setCurrentIndex(data.value)
        if data.value==255:
            self.data_input_38.setCurrentIndex(cnt_item)

        #无功勋人
        if n > 101:
            self.data_input_21.setText("")
            self.data_input_22.setText("")
            self.data_input_23.setText("")
            self.data_input_24.setText("")
            self.data_input_25.setText("")
            self.data_input_21.setEnabled(False)
            self.data_input_22.setEnabled(False)
            self.data_input_23.setEnabled(False)
            self.data_input_24.setEnabled(False)
            self.data_input_25.setEnabled(False)
        else:
            self.data_input_21.setEnabled(True)
            self.data_input_22.setEnabled(True)
            self.data_input_23.setEnabled(True)
            self.data_input_24.setEnabled(True)
            self.data_input_25.setEnabled(True)

    #扳手第二页保存按键
    def saveData(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        global cnt_item
        if len(self.listview_data.selectedIndexes())<=0:
            return
        n = self.listview_data.selectedIndexes()[0].row()
        #R形象
        data = ctypes.c_int(int(self.data_input_1.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x50F800+n*2, ctypes.byref(data), 2, None)
        
        #S形象
        data = ctypes.c_int(int(self.data_input_2.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x501000+n*2, ctypes.byref(data), 2, None)
        #头像
        data = ctypes.c_int(int(self.data_input_3.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x50F000+n*2, ctypes.byref(data), 2, None)
        mem = ctypes.c_long()
        self.md.ReadProcessMemory(int(self.p), 0x4CEA00, ctypes.byref(mem), 4, None)
        #攻击力
        data = ctypes.c_int(int(self.data_input_4.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x11, ctypes.byref(data), 2, None)
        #防御力
        data = ctypes.c_int(int(self.data_input_5.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x13, ctypes.byref(data), 2, None)
        #精神力
        data = ctypes.c_int(int(self.data_input_6.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x15, ctypes.byref(data), 2, None)
        #爆发力
        data = ctypes.c_int(int(self.data_input_7.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x17, ctypes.byref(data), 2, None)
        #士气
        data = ctypes.c_int(int(self.data_input_8.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x19, ctypes.byref(data), 2, None)
        #HP上限
        data = ctypes.c_int(int(self.data_input_9.toPlainText()))
        if version <= 1:
            self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x1B, ctypes.byref(data), 4, None)
        else:
            self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x1C, ctypes.byref(data), 4, None)
        #MP上限
        data = ctypes.c_int(int(self.data_input_10.toPlainText()))
        if version <= 1:
            self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x1F, ctypes.byref(data), 2, None)
        else:
            self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x20, ctypes.byref(data), 1, None)
        #我军
        if self.data_input_11.isChecked() == True:
            data=ctypes.c_int(0)
        else:
            data=ctypes.c_int(255)
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x2A, ctypes.byref(data), 1, None)
        #等级
        data = ctypes.c_int(int(self.data_input_12.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x2C, ctypes.byref(data), 1, None)
        #经验
        data = ctypes.c_int(int(self.data_input_13.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x2D, ctypes.byref(data), 1, None)
        #武力
        data = ctypes.c_int(int(self.data_input_14.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x21, ctypes.byref(data), 1, None)
        #统率
        data = ctypes.c_int(int(self.data_input_15.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x22, ctypes.byref(data), 1, None)
        #智力
        data = ctypes.c_int(int(self.data_input_16.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x23, ctypes.byref(data), 1, None)
        #敏捷
        data = ctypes.c_int(int(self.data_input_17.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x24, ctypes.byref(data), 1, None)
        #运气
        data = ctypes.c_int(int(self.data_input_18.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x25, ctypes.byref(data), 1, None)
        #出场
        data = ctypes.c_int(int(self.data_input_19.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x27, ctypes.byref(data), 1, None)
        #撤退
        data = ctypes.c_int(int(self.data_input_20.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x29, ctypes.byref(data), 1, None)
        if n <= 101:
            if version == 0:
                gongxun = 0x508000
            else:
                gongxun = 0x508400
            #武力功勋
            data = ctypes.c_int(int(self.data_input_21.toPlainText()))
            if n <= 101:
                self.md.WriteProcessMemory(int(self.p), gongxun+10*n+0, ctypes.byref(data), 2, None)
            #统率功勋
            data = ctypes.c_int(int(self.data_input_22.toPlainText()))
            if n <= 101:
                self.md.WriteProcessMemory(int(self.p), gongxun+10*n+2, ctypes.byref(data), 2, None)
            #智力功勋
            data = ctypes.c_int(int(self.data_input_23.toPlainText()))
            if n <= 101:
                self.md.WriteProcessMemory(int(self.p), gongxun+10*n+4, ctypes.byref(data), 2, None)
            #敏捷功勋
            data = ctypes.c_int(int(self.data_input_24.toPlainText()))
            if n <= 101:
                self.md.WriteProcessMemory(int(self.p), gongxun+10*n+6, ctypes.byref(data), 2, None)
            #运气功勋
            data = ctypes.c_int(int(self.data_input_25.toPlainText()))
            if n <= 101:
                self.md.WriteProcessMemory(int(self.p), gongxun+10*n+8, ctypes.byref(data), 2, None)
        #3
        data = ctypes.c_int(int(self.data_input_26.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x28, ctypes.byref(data), 1, None)
        #6
        data = ctypes.c_int(int(self.data_input_27.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x6, ctypes.byref(data), 2, None)
        #6
        data = ctypes.c_int(int(self.data_input_28.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x44, ctypes.byref(data), 2, None)
        #6
        data = ctypes.c_int(int(self.data_input_29.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x46, ctypes.byref(data), 2, None)
        #杀敌数
        data = ctypes.c_int(int(self.data_input_30.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x35, ctypes.byref(data), 2, None)
        #兵种
        data = ctypes.c_int(self.data_input_31.currentIndex())
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x2B, ctypes.byref(data), 1, None)
        #武器
        data = ctypes.c_int(self.data_input_32.currentIndex())
        if self.data_input_32.currentIndex() == cnt_item:
            data=ctypes.c_int(255)
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x2E, ctypes.byref(data), 1, None)
        #等级
        data = ctypes.c_int(int(self.data_input_33.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x2F, ctypes.byref(data), 1, None)
        #经验
        data = ctypes.c_int(int(self.data_input_34.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x30, ctypes.byref(data), 1, None)
        #防具
        data = ctypes.c_int(self.data_input_35.currentIndex())
        if self.data_input_35.currentIndex() == cnt_item:
            data=ctypes.c_int(255)
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x31, ctypes.byref(data), 1, None)
        #等级
        data = ctypes.c_int(int(self.data_input_36.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x32, ctypes.byref(data), 1, None)
        #经验
        data = ctypes.c_int(int(self.data_input_37.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x33, ctypes.byref(data), 1, None)
        #辅助
        data = ctypes.c_int(self.data_input_38.currentIndex())
        if self.data_input_38.currentIndex() == cnt_item:
            data=ctypes.c_int(255)
        self.md.WriteProcessMemory(int(self.p), mem.value+0x48*n+0x34, ctypes.byref(data), 1, None)

    #扳手第三页人物战场数据读入
    def onWar(self, kind):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        data = ctypes.c_int()
        data2 = ctypes.c_int()
        name = ctypes.c_byte()
        mem = ctypes.c_int()
        if kind == 0:
            n = 0
            if len(self.listview_war.selectedIndexes())>0:
                n = self.listview_war.selectedIndexes()[0].row()
            self.listview_war.clear()
            self.md.ReadProcessMemory(int(self.p), 0x4CEA00, ctypes.byref(mem), 4, None)
            for i in range(0,cnt_wo + cnt_you + cnt_di):
                self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war, ctypes.byref(data), 2, None)
                if data.value!=65535:
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war + 5, ctypes.byref(data2), 1, None)
                    if (data2.value==0 and self.war_kind_1.isChecked() == True)\
                        or (data2.value==1 and self.war_kind_2.isChecked() == True)\
                        or (data2.value>=2 and self.war_kind_3.isChecked() == True):
                        names=b""
                        for j in range(0,8):
                            self.md.ReadProcessMemory(int(self.p), mem.value+data.value*0x48+j+8, ctypes.byref(name), 1, None)
                            names+=name
                        try:
                            names=names.decode("gbk")
                        except:
                            names="非法字符"
                        self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war+4, ctypes.byref(data2), 1, None)
                        self.listview_war.addItem(str(data2.value)+"/"+str(data.value)+":"+names)
            if n >= self.listview_war.count():
                n = 0
            if self.listview_war.count()!=0:
                self.listview_war.setCurrentRow(n)

        if self.war_kind_1.isChecked() == True:
            war_code = self.listview_war.currentRow()
        if self.war_kind_2.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo
        if self.war_kind_3.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo + cnt_you
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war, ctypes.byref(data), 2, None)
        data_code = data.value

        #角色
        self.war_input_1.setCurrentIndex(data_code)
        #HPCur
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x10, ctypes.byref(data), 4, None)
        self.war_input_2.setText(str(data.value))
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xC, ctypes.byref(data2), 1, None)
        if data.value == 0 and data2.value == 3:
            self.war_life.setEnabled(True)
            self.war_life.setStyleSheet("background-color:rgb(255, 255, 255);\ncolor:rgb(0,0,0)")
        else:
            self.war_life.setEnabled(False)
            self.war_life.setStyleSheet("background-color:rgb(255, 255, 255);\ncolor:rgb(190,190,190)")
        #MPCur
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x14, ctypes.byref(data), 4, None)
        self.war_input_3.setText(str(data.value))
        #SPCur
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), 0x501C00+data_code, ctypes.byref(data), 1, None)
        self.war_input_4.setText(str(data.value))
        #健康
        global condition_change
        data = ctypes.c_int()
        if condition_change == False:
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x1E, ctypes.byref(data), 1, None)
            self.war_input_5.setChecked(data.value & (1 << 1))
            self.war_input_6.setChecked(data.value & (1 << 2))
            self.war_input_7.setChecked(data.value & (1 << 3))
            self.war_input_8.setChecked(data.value & (1 << 4))
        else:
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x1E, ctypes.byref(data), 1, None)
            self.war_input_51.setText(str(data.value % 4))
            self.war_input_52.setText(str(int(data.value / 4) % 4))
            self.war_input_53.setText(str(int(data.value / 16) % 4))
            self.war_input_54.setText(str(int(data.value / 64) % 4))
        #X
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x6, ctypes.byref(data), 1, None)
        self.war_input_9.setText(str(data.value))
        #Y
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x7, ctypes.byref(data), 1, None)
        self.war_input_10.setText(str(data.value))
        self.war_input_9.setEnabled(self.war_life.isEnabled())
        self.war_input_10.setEnabled(self.war_life.isEnabled())
        #方针
        if self.war_kind_1.isChecked() == False:
            self.war_11.show()
            self.war_input_11.show()
            self.war_13.show()
            self.war_input_13.show()
            self.war_14.show()
            self.war_input_14.show()
            self.war_36.show()
            self.war_input_36.show()
            self.war_37.show()
            self.war_input_37.show()
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(data), 1, None)
            if data.value == 3:
                self.war_input_11.setCurrentIndex(0)
            if data.value == 1:
                self.war_input_11.setCurrentIndex(1)
            if data.value == 2:
                self.war_input_11.setCurrentIndex(2)
            if data.value == 0:
                self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x8, ctypes.byref(data2), 1, None)
                if data2.value != 255:
                    self.war_input_11.setCurrentIndex(3)
                else:
                    self.war_input_11.setCurrentIndex(4)
            if data.value == 4:
                self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x8, ctypes.byref(data2), 1, None)
                if data2.value != 255:
                    self.war_input_11.setCurrentIndex(5)
                else:
                    self.war_input_11.setCurrentIndex(6)
            if (data.value == 0 or data.value == 4) and data2.value != 255:
                self.war_12.show()
                self.war_input_12.show()
                self.war_input_12.clear()
                data2 = ctypes.c_int()
                data3 = ctypes.c_int()
                name = ctypes.c_byte()
                mem = ctypes.c_int()
                self.md.ReadProcessMemory(int(self.p), 0x4CEA00, ctypes.byref(mem), 4, None)
                self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x8, ctypes.byref(data3), 1, None)
                for i in range(0,cnt_wo + cnt_you + cnt_di):
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war, ctypes.byref(data), 2, None)
                    if data.value!=65535:
                        self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war + 5, ctypes.byref(data2), 1, None)
                        names=b""
                        for j in range(0,8):
                            self.md.ReadProcessMemory(int(self.p), mem.value+data.value*0x48+j+8, ctypes.byref(name), 1, None)
                            names+=name
                        try:
                            names=names.decode("gbk")
                        except:
                            names="非法字符"
                        self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war+4, ctypes.byref(data2), 1, None)
                        self.war_input_12.addItem(str(data2.value)+":"+names)
                    if i == data3.value:
                        self.war_input_12.setCurrentIndex(self.war_input_12.count()-1)
                        global_1 = data3.value
            else:
                self.war_12.hide()
                self.war_input_12.hide()
            data = ctypes.c_int()
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x9, ctypes.byref(data), 1, None)
            self.war_input_13.setText(str(data.value))
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xA, ctypes.byref(data), 1, None)
            self.war_input_14.setText(str(data.value))
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x20, ctypes.byref(data), 1, None)
            self.war_input_36.setText(str(data.value))
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x21, ctypes.byref(data), 1, None)
            self.war_input_37.setText(str(data.value))
        else:
            self.war_11.hide()
            self.war_input_11.hide()
            self.war_12.hide()
            self.war_input_12.hide()
            self.war_13.hide()
            self.war_input_13.hide()
            self.war_14.hide()
            self.war_input_14.hide()
            self.war_36.hide()
            self.war_input_36.hide()
            self.war_37.hide()
            self.war_input_37.hide()
        #行动
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xD, ctypes.byref(data), 1, None)
        if data.value & (1 << 1) or data.value & (1 << 2):
            self.war_input_15.setChecked(True)
        else:
            self.war_input_15.setChecked(False)
        #可控
        if self.war_kind_1.isChecked() == True or self.war_kind_3.isChecked() == True:
            self.war_46.hide()
            self.war_input_46.hide()
        if self.war_kind_2.isChecked() == True:
            self.war_46.show()
            self.war_input_46.show()
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(data), 1, None)
            if data.value == 7:
                self.war_input_46.setChecked(True)
                self.war_input_11.setCurrentIndex(0)
            else:
                self.war_input_46.setChecked(False)
        #方向
        '''data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xF, ctypes.byref(data), 1, None)
        self.war_input_16.setCurrentIndex(data.value)'''
        self.war_input_16.setCurrentIndex(0)
        #攻击
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x18, ctypes.byref(data), 1, None)
        if data.value < 3:
            self.war_input_17.setCurrentIndex(0)
        if data.value == 3:
            self.war_input_17.setCurrentIndex(1)
        if data.value > 3:
            self.war_input_17.setCurrentIndex(2)
        #攻击
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x19, ctypes.byref(data), 1, None)
        if data.value < 3:
            self.war_input_18.setCurrentIndex(0)
        if data.value == 3:
            self.war_input_18.setCurrentIndex(1)
        if data.value > 3:
            self.war_input_18.setCurrentIndex(2)
        #攻击
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x1A, ctypes.byref(data), 1, None)
        if data.value < 3:
            self.war_input_19.setCurrentIndex(0)
        if data.value == 3:
            self.war_input_19.setCurrentIndex(1)
        if data.value > 3:
            self.war_input_19.setCurrentIndex(2)
        #攻击
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x1B, ctypes.byref(data), 1, None)
        if data.value < 3:
            self.war_input_20.setCurrentIndex(0)
        if data.value == 3:
            self.war_input_20.setCurrentIndex(1)
        if data.value > 3:
            self.war_input_20.setCurrentIndex(2)
        #攻击
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x1C, ctypes.byref(data), 1, None)
        if data.value < 3:
            self.war_input_21.setCurrentIndex(0)
        if data.value == 3:
            self.war_input_21.setCurrentIndex(1)
        if data.value > 3:
            self.war_input_21.setCurrentIndex(2)
        #攻击
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x1D, ctypes.byref(data), 1, None)
        if data.value < 3:
            self.war_input_22.setCurrentIndex(0)
        if data.value == 3:
            self.war_input_22.setCurrentIndex(1)
        if data.value > 3:
            self.war_input_22.setCurrentIndex(2)
        #回合上限
        self.md.ReadProcessMemory(int(self.p), 0x4B3D0B, ctypes.byref(data), 1, None)
        self.war_input_24.setText(str(data.value))
        #当前回合
        self.md.ReadProcessMemory(int(self.p), 0x4B3D0A, ctypes.byref(data), 1, None)
        self.war_input_25.setText(str(data.value+1))
        #下一关
        self.md.ReadProcessMemory(int(self.p), 0x4B0776, ctypes.byref(data), 1, None)
        self.war_input_26.setText(str((int)(data.value/2)+1))
        #天气
        data = ctypes.c_int()
        data2 = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), 0x4B3D0C, ctypes.byref(data), 1, None)
        self.md.ReadProcessMemory(int(self.p), 0x4B3D19, ctypes.byref(data2), 1, None)
        weather_list = [0,0,0,1,2,3,0,0,0,0,1,2,0,1,2,2,3,3,0,0,1,1,4,4,0,1,4,4,4,4]
        self.war_input_27.setCurrentIndex(weather_list[(data2.value*6+data.value)%30])
        #22
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x22, ctypes.byref(data), 1, None)
        self.war_input_38.setText(str(data.value))
        #戮
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x23, ctypes.byref(data), 1, None)
        self.war_input_39.setText(str(data.value))

        if version == 0:
            self.war_input_40.setEnabled(True)
            self.war_input_41.setEnabled(True)
            self.war_input_42.setEnabled(True)
            self.war_input_43.setEnabled(True)
            self.war_input_44.setEnabled(True)
            self.war_input_45.setEnabled(True)
            #24
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*0x36+0x24, ctypes.byref(data), 1, None)
            self.war_input_40.setText(str(data.value))
            #26
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*0x36+0x26, ctypes.byref(data), 1, None)
            self.war_input_44.setText(str(data.value))
            #28
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*0x36+0x28, ctypes.byref(data), 1, None)
            self.war_input_41.setText(str(data.value))
            #2A
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*0x36+0x2A, ctypes.byref(data), 1, None)
            self.war_input_45.setText(str(data.value))
            #2C
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*0x36+0x2C, ctypes.byref(data), 1, None)
            self.war_input_42.setText(str(data.value))
            #2E
            self.md.ReadProcessMemory(int(self.p), addr_war+war_code*0x36+0x2E, ctypes.byref(data), 1, None)
            self.war_input_43.setText(str(data.value))
        else:
            self.war_input_40.setEnabled(False)
            self.war_input_41.setEnabled(False)
            self.war_input_42.setEnabled(False)
            self.war_input_43.setEnabled(False)
            self.war_input_44.setEnabled(False)
            self.war_input_45.setEnabled(False)

    #扳手第三页人物战场数据保存
    def saveWar(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        if self.listview_war.currentRow()<0:
            return
        data = ctypes.c_int()
        #检查RS
        self.md.ReadProcessMemory(int(self.p), 0x4B0776, ctypes.byref(data), 1, None)
        if data.value % 2 == 0:
            #HPCur
            data = ctypes.c_int(int(self.war_input_2.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x10, ctypes.byref(data), 4, None)
            #MPCur
            data = ctypes.c_int(int(self.war_input_3.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x14, ctypes.byref(data), 4, None)
            return
        
        data = ctypes.c_int()
        if self.war_kind_1.isChecked() == True:
            war_code = self.listview_war.currentRow()
        if self.war_kind_2.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo
        if self.war_kind_3.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo + cnt_you

        #角色
        data_code = self.war_input_1.currentIndex()
        data = ctypes.c_int(data_code)
        self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war, ctypes.byref(data), 2, None)
        #HPCur
        data = ctypes.c_int(int(self.war_input_2.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x10, ctypes.byref(data), 4, None)
        #MPCur
        data = ctypes.c_int(int(self.war_input_3.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x14, ctypes.byref(data), 4, None)
        #SPCur
        data = ctypes.c_int(int(self.war_input_4.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x501C00+data_code, ctypes.byref(data), 1, None)
        #健康
        global condition_change
        if condition_change == False:
            data = ctypes.c_int(0)
            if self.war_input_5.isChecked() == True:
                data.value += 2
            if self.war_input_6.isChecked() == True:
                data.value += 4
            if self.war_input_7.isChecked() == True:
                data.value += 8
            if self.war_input_8.isChecked() == True:
                data.value += 16
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1E, ctypes.byref(data), 1, None)
        else:
            data = ctypes.c_int(0)
            data.value += 1 * (int(self.war_input_51.text()) % 4)
            data.value += 4 * (int(self.war_input_52.text()) % 4)
            data.value += 16 * (int(self.war_input_53.text()) % 4)
            data.value += 64 * (int(self.war_input_54.text()) % 4)
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1E, ctypes.byref(data), 1, None)
        #方针
        if self.war_kind_1.isChecked() == False:
            sel = self.war_input_11.currentIndex()
            if sel == 0:
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(ctypes.c_int(3)), 1, None)
            if sel == 1:
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(ctypes.c_int(1)), 1, None)
            if sel == 2:
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(ctypes.c_int(2)), 1, None)
            if sel == 3 or sel == 4:
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(ctypes.c_int(0)), 1, None)
            if sel == 5 or sel == 6:
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(ctypes.c_int(4)), 1, None)
            if sel == 3 or sel == 5:
                a = 0
                b = 0
                for i in range(0,cnt_wo + cnt_you + cnt_di):
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war, ctypes.byref(data), 2, None)
                    if data.value!=65535:
                        if i < cnt_wo:
                            a += 1
                        elif i < cnt_wo + cnt_you:
                            b += 1
                c = self.war_input_12.currentIndex()
                if c < a:
                    data = ctypes.c_int(c)
                elif c < b:
                    data = ctypes.c_int(c-a+cnt_wo)
                else :
                    data = ctypes.c_int(c-a-b+cnt_wo+cnt_you)
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x8, ctypes.byref(data), 1, None)
            if sel == 4 or sel == 6:
                data = ctypes.c_int(int(self.war_input_13.toPlainText()))
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x9, ctypes.byref(data), 1, None)
                data = ctypes.c_int(int(self.war_input_14.toPlainText()))
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xA, ctypes.byref(data), 1, None)
                data = ctypes.c_int(255)
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x8, ctypes.byref(data), 1, None)
        #两个坐标
        if self.war_kind_1.isChecked() == False:
            data = ctypes.c_int(int(self.war_input_13.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x9, ctypes.byref(data), 1, None)
            data = ctypes.c_int(int(self.war_input_14.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xA, ctypes.byref(data), 1, None)
            data = ctypes.c_int(int(self.war_input_36.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x20, ctypes.byref(data), 1, None)
            data = ctypes.c_int(int(self.war_input_37.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x21, ctypes.byref(data), 1, None)
        #行动
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xD, ctypes.byref(data), 1, None)
        if self.war_input_15.isChecked() == True:
            data = ctypes.c_int(data.value | 6)
        else:
            data = ctypes.c_int(data.value & 248)
        self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xD, ctypes.byref(data), 1, None)
        #可控
        if self.war_kind_2.isChecked() == True:
            if self.war_input_46.isChecked() == True:
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0xE, ctypes.byref(ctypes.c_int(7)), 1, None)
        #转向
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0xF, ctypes.byref(data), 1, None)
        if self.war_input_16.currentIndex() != data.value + 1:
            self.onTurn()
        #攻击
        if self.war_input_17.currentIndex() == 0:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x18, ctypes.byref(ctypes.c_int(1)), 1, None)
        if self.war_input_17.currentIndex() == 1:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x18, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_17.currentIndex() == 2:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x18, ctypes.byref(ctypes.c_int(6)), 1, None)
        #攻击
        if self.war_input_18.currentIndex() == 0:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x19, ctypes.byref(ctypes.c_int(1)), 1, None)
        if self.war_input_18.currentIndex() == 1:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x19, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_18.currentIndex() == 2:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x19, ctypes.byref(ctypes.c_int(6)), 1, None)
        #攻击
        if self.war_input_19.currentIndex() == 0:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1A, ctypes.byref(ctypes.c_int(1)), 1, None)
        if self.war_input_19.currentIndex() == 1:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1A, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_19.currentIndex() == 2:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1A, ctypes.byref(ctypes.c_int(6)), 1, None)
        #攻击
        if self.war_input_20.currentIndex() == 0:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1B, ctypes.byref(ctypes.c_int(1)), 1, None)
        if self.war_input_20.currentIndex() == 1:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1B, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_20.currentIndex() == 2:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1B, ctypes.byref(ctypes.c_int(6)), 1, None)
        #攻击
        if self.war_input_21.currentIndex() == 0:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1C, ctypes.byref(ctypes.c_int(1)), 1, None)
        if self.war_input_21.currentIndex() == 1:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1C, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_21.currentIndex() == 2:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1C, ctypes.byref(ctypes.c_int(6)), 1, None)
        #攻击
        if self.war_input_22.currentIndex() == 0:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1D, ctypes.byref(ctypes.c_int(1)), 1, None)
        if self.war_input_22.currentIndex() == 1:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1D, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_22.currentIndex() == 2:
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x1D, ctypes.byref(ctypes.c_int(6)), 1, None)
        #全部
        if self.war_input_23.currentIndex() == 1:
            for i in range(0x18,0x1E):
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+i, ctypes.byref(ctypes.c_int(1)), 1, None)
        if self.war_input_23.currentIndex() == 2:
            for i in range(0x18,0x1E):
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+i, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_23.currentIndex() == 3:
            for i in range(0x18,0x1E):
                self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+i, ctypes.byref(ctypes.c_int(6)), 1, None)
        self.war_input_23.setCurrentIndex(0)
        #回合上限
        data = ctypes.c_int(int(self.war_input_24.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x4B3D0B, ctypes.byref(data), 1, None)
        #当前回合
        data = ctypes.c_int(int(self.war_input_25.toPlainText())-1)
        self.md.WriteProcessMemory(int(self.p), 0x4B3D0A, ctypes.byref(data), 1, None)
        #下一关
        self.md.ReadProcessMemory(int(self.p), 0x4B0776, ctypes.byref(data), 1, None)
        if data.value % 2 == 1:
            data = ctypes.c_int(int(self.war_input_26.toPlainText()) * 2 - 1)
            if data.value >= 0:
                self.md.WriteProcessMemory(int(self.p), 0x4B0776, ctypes.byref(data), 1, None)
        #天气
        if self.war_input_27.currentIndex() == 0:
            self.md.WriteProcessMemory(int(self.p), 0x4B3D0C, ctypes.byref(ctypes.c_int(0)), 1, None)
        if self.war_input_27.currentIndex() == 1:
            self.md.WriteProcessMemory(int(self.p), 0x4B3D0C, ctypes.byref(ctypes.c_int(3)), 1, None)
        if self.war_input_27.currentIndex() == 2:
            self.md.WriteProcessMemory(int(self.p), 0x4B3D0C, ctypes.byref(ctypes.c_int(4)), 1, None)
        if self.war_input_27.currentIndex() == 3:
            self.md.WriteProcessMemory(int(self.p), 0x4B3D0C, ctypes.byref(ctypes.c_int(5)), 1, None)
        if self.war_input_27.currentIndex() == 4:
            self.md.WriteProcessMemory(int(self.p), 0x4B3D0C, ctypes.byref(ctypes.c_int(0x16)), 1, None)
        self.md.WriteProcessMemory(int(self.p), 0x4B3D19, ctypes.byref(ctypes.c_int(0)), 1, None)
        #22
        data = ctypes.c_int(int(self.war_input_38.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x22, ctypes.byref(data), 1, None)
        #戮
        data = ctypes.c_int(int(self.war_input_39.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_war+war_code*len_war+0x23, ctypes.byref(data), 1, None)

        #群体buff/debuff
        if self.war_input_28.currentIndex() == 0:
            a = 0
            b = cnt_wo
        if self.war_input_28.currentIndex() == 1:
            a = cnt_wo
            b = cnt_wo + cnt_you
        if self.war_input_28.currentIndex() == 2:
            a = cnt_wo + cnt_you
            b = cnt_wo + cnt_you + cnt_di
        if self.war_input_29.currentIndex() != 0:
            for i in range(a,b):
                self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0x18, ctypes.byref(ctypes.c_int(2*self.war_input_29.currentIndex()-1)), 1, None)
        if self.war_input_30.currentIndex() != 0:
            for i in range(a,b):
                self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0x19, ctypes.byref(ctypes.c_int(2*self.war_input_29.currentIndex()-1)), 1, None)
        if self.war_input_31.currentIndex() != 0:
            for i in range(a,b):
                self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0x1A, ctypes.byref(ctypes.c_int(2*self.war_input_29.currentIndex()-1)), 1, None)
        if self.war_input_32.currentIndex() != 0:
            for i in range(a,b):
                self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0x1B, ctypes.byref(ctypes.c_int(2*self.war_input_29.currentIndex()-1)), 1, None)
        if self.war_input_33.currentIndex() != 0:
            for i in range(a,b):
                self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0x1C, ctypes.byref(ctypes.c_int(2*self.war_input_29.currentIndex()-1)), 1, None)
        if self.war_input_34.currentIndex() != 0:
            for i in range(a,b):
                self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+0x1D, ctypes.byref(ctypes.c_int(2*self.war_input_29.currentIndex()-1)), 1, None)
        if self.war_input_35.currentIndex() != 0:
            for i in range(a,b):
                for j in range(0x18,0x1E):
                    self.md.WriteProcessMemory(int(self.p), addr_war+i*len_war+j, ctypes.byref(ctypes.c_int(2*self.war_input_29.currentIndex()-1)), 1, None)
        self.war_input_29.setCurrentIndex(0)
        self.war_input_30.setCurrentIndex(0)
        self.war_input_31.setCurrentIndex(0)
        self.war_input_32.setCurrentIndex(0)
        self.war_input_33.setCurrentIndex(0)
        self.war_input_34.setCurrentIndex(0)
        self.war_input_35.setCurrentIndex(0)


        if version == 0:
            #24
            data = ctypes.c_int(int(self.war_input_40.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*0x36+0x24, ctypes.byref(data), 1, None)
            #26
            data = ctypes.c_int(int(self.war_input_44.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*0x36+0x26, ctypes.byref(data), 1, None)
            #28
            data = ctypes.c_int(int(self.war_input_41.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*0x36+0x28, ctypes.byref(data), 1, None)
            #2A
            data = ctypes.c_int(int(self.war_input_45.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*0x36+0x2A, ctypes.byref(data), 1, None)
            #2C
            data = ctypes.c_int(int(self.war_input_42.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*0x36+0x2C, ctypes.byref(data), 1, None)
            #2E
            data = ctypes.c_int(int(self.war_input_43.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), addr_war+war_code*0x36+0x2E, ctypes.byref(data), 1, None)

        self.onWar(1)

    def onItem(self):
        global cnt_item
        self.item_input_2.setText("0")
        self.item_input_3.setText("0")
        data = ctypes.c_int()
        for i in range(0,200):
            self.md.ReadProcessMemory(int(self.p), 0x4B0783 + i * 3, ctypes.byref(data), 1, None)
            if data.value!=255:
                self.listview_item.item(i).setText(self.item_input_1.itemText(data.value))
            else:
                self.listview_item.item(i).setText("空")
            if i == self.listview_item.currentRow():
                self.item_input_1.setCurrentIndex(data.value)
                if data.value == 255:
                    self.item_input_1.setCurrentIndex(cnt_item)
                self.md.ReadProcessMemory(int(self.p), 0x4B0783 + i * 3 + 1, ctypes.byref(data), 1, None)
                self.item_input_2.setText(str(data.value))
                self.md.ReadProcessMemory(int(self.p), 0x4B0783 + i * 3 + 2, ctypes.byref(data), 1, None)
                self.item_input_3.setText(str(data.value))

        a = self.listview_item_2.currentRow()
        if version >= 1:
            if a <= 16:
                self.md.ReadProcessMemory(int(self.p), 0x4B09DB + a, ctypes.byref(data), 1, None)
            else:
                self.md.ReadProcessMemory(int(self.p), 0x510c80 + a - 17, ctypes.byref(data), 1, None)
        else:
            self.md.ReadProcessMemory(int(self.p), 0x510c80 + a, ctypes.byref(data), 1, None)
        self.item_input_4.setText(str(data.value))

        self.md.ReadProcessMemory(int(self.p), 0x4B077C, ctypes.byref(data), 4, None)
        self.item_input_5.setText(str(data.value))

        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), 0x4B0782, ctypes.byref(data), 1, None)
        self.item_input_6.setText(str(data.value))

        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), 0x505F40, ctypes.byref(data), 4, None)
        self.item_input_7.setText(str(data.value))
    
    def saveItem(self):
        global cnt_item
        a = self.listview_item.currentRow()
        if self.item_input_1.currentIndex() != cnt_item:
            data = ctypes.c_int(self.item_input_1.currentIndex())
            self.md.WriteProcessMemory(int(self.p), 0x4B0783 + a * 3, ctypes.byref(data), 1, None)
            data = ctypes.c_int(int(self.item_input_2.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), 0x4B0783 + a * 3 + 1, ctypes.byref(data), 1, None)
            data = ctypes.c_int(int(self.item_input_3.toPlainText()))
            self.md.WriteProcessMemory(int(self.p), 0x4B0783 + a * 3 + 2, ctypes.byref(data), 1, None)
        else:
            data = ctypes.c_int(255)
            self.md.WriteProcessMemory(int(self.p), 0x4B0783 + a * 3, ctypes.byref(data), 1, None)

        a = self.listview_item_2.currentRow()
        data = ctypes.c_int(int(self.item_input_4.toPlainText()))
        if version >= 1:
            if a <= 16:
                self.md.WriteProcessMemory(int(self.p), 0x4B09DB + a, ctypes.byref(data), 1, None)
            else:
                self.md.WriteProcessMemory(int(self.p), 0x510c80 + a-17, ctypes.byref(data), 1, None)
        else:
            self.md.WriteProcessMemory(int(self.p), 0x510c80 + a, ctypes.byref(data), 1, None)

        data = ctypes.c_int(int(self.item_input_5.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x4B077C, ctypes.byref(data), 4, None)

        data = ctypes.c_int(int(self.item_input_6.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x4B0782, ctypes.byref(data), 1, None)

        data = ctypes.c_int(int(self.item_input_7.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), 0x505F40, ctypes.byref(data), 4, None)

        self.onItem()

    def onPower(self):
        global cnt_item
        global addr_tianfu
        global addr_zhuanshu
        data = ctypes.c_int()
        a = self.listview_item_3.currentRow()
        #天赋
        self.md.ReadProcessMemory(int(self.p), addr_tianfu + a * 8, ctypes.byref(data), 2, None)
        self.power_input_1_1.setCurrentIndex(data.value)
        self.md.ReadProcessMemory(int(self.p), addr_tianfu + a * 8 + 2, ctypes.byref(data), 2, None)
        self.power_input_1_2.setCurrentIndex(data.value)
        self.md.ReadProcessMemory(int(self.p), addr_tianfu + a * 8 + 4, ctypes.byref(data), 2, None)
        self.power_input_1_3.setCurrentIndex(data.value)
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_tianfu + a * 8 + 6, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_1_4.setCurrentIndex(data.value)
        else:
            self.power_input_1_4.setCurrentIndex(80)
        self.md.ReadProcessMemory(int(self.p), addr_tianfu + a * 8 + 7, ctypes.byref(data), 1, None)
        self.power_input_1_5.setText(str(data.value))
        #专属1
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16, ctypes.byref(data), 2, None)
        self.power_input_2_1.setCurrentIndex(data.value)
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 2, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_2_2.setCurrentIndex(data.value)
        else:
            self.power_input_2_2.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 3, ctypes.byref(data), 1, None)
        self.power_input_2_3.setText(str(data.value))
        if data.value == 0:
            self.power_input_2_1.setCurrentIndex(1024)
            self.power_input_2_2.setCurrentIndex(cnt_item)
        #专属2
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 4, ctypes.byref(data), 2, None)
        self.power_input_2_4.setCurrentIndex(data.value)
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 6, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_2_5.setCurrentIndex(data.value)
        else:
            self.power_input_2_5.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 7, ctypes.byref(data), 1, None)
        self.power_input_2_6.setText(str(data.value))
        if data.value == 0:
            self.power_input_2_4.setCurrentIndex(1024)
            self.power_input_2_5.setCurrentIndex(cnt_item)
        #套装1
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 8, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_3_1.setCurrentIndex(data.value)
        else:
            self.power_input_3_1.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 9, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_3_2.setCurrentIndex(data.value)
        else:
            self.power_input_3_2.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 10, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_3_3.setCurrentIndex(data.value)
        else:
            self.power_input_3_3.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 11, ctypes.byref(data), 1, None)
        self.power_input_3_4.setText(str(data.value))
        if data.value == 0:
            self.power_input_3_1.setCurrentIndex(cnt_item)
            self.power_input_3_2.setCurrentIndex(cnt_item)
            self.power_input_3_3.setCurrentIndex(cnt_item)
        #套装2
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 12, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_3_5.setCurrentIndex(data.value)
        else:
            self.power_input_3_5.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 13, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_3_6.setCurrentIndex(data.value)
        else:
            self.power_input_3_6.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 14, ctypes.byref(data), 1, None)
        if data.value != 255:
            self.power_input_3_7.setCurrentIndex(data.value)
        else:
            self.power_input_3_7.setCurrentIndex(cnt_item)
        self.md.ReadProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 15, ctypes.byref(data), 1, None)
        self.power_input_3_8.setText(str(data.value))
        if data.value == 0:
            self.power_input_3_5.setCurrentIndex(cnt_item)
            self.power_input_3_6.setCurrentIndex(cnt_item)
            self.power_input_3_7.setCurrentIndex(cnt_item)

    def savePower(self):
        global cnt_item
        global addr_zhuanshu
        a = self.listview_item_3.currentRow()
        #天赋
        data = self.power_input_1_1.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_tianfu + a * 8, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.power_input_1_2.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_tianfu + a * 8 + 2, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.power_input_1_3.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_tianfu + a * 8 + 4, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.power_input_1_4.currentIndex()
        if data == 80:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_tianfu + a * 8 + 6, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = ctypes.c_int(int(self.power_input_1_5.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_tianfu + a * 8 + 7, ctypes.byref(data), 1, None)
        #专属1
        data = self.power_input_2_1.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.power_input_2_2.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 2, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = ctypes.c_int(int(self.power_input_2_3.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 3, ctypes.byref(data), 1, None)
        if data.value == 0:
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16, ctypes.byref(ctypes.c_int(0)), 2, None)
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 2, ctypes.byref(ctypes.c_int(0)), 1, None)
        #专属2
        data = self.power_input_2_4.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 4, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.power_input_2_5.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 6, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = ctypes.c_int(int(self.power_input_2_6.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 7, ctypes.byref(data), 1, None)
        if data.value == 0:
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 4, ctypes.byref(ctypes.c_int(0)), 2, None)
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 6, ctypes.byref(ctypes.c_int(0)), 1, None)
        #套装1
        data = self.power_input_3_1.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 8, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = self.power_input_3_2.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 9, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = self.power_input_3_3.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 10, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = ctypes.c_int(int(self.power_input_3_4.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 11, ctypes.byref(data), 1, None)
        if data.value == 0:
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 8, ctypes.byref(ctypes.c_int(0)), 1, None)
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 9, ctypes.byref(ctypes.c_int(0)), 1, None)
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 10, ctypes.byref(ctypes.c_int(0)), 1, None)
        #套装2
        data = self.power_input_3_5.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 12, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = self.power_input_3_6.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 13, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = self.power_input_3_7.currentIndex()
        if data == cnt_item:
            data = 255
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 14, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = ctypes.c_int(int(self.power_input_3_8.toPlainText()))
        self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 15, ctypes.byref(data), 1, None)
        if data.value == 0:
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 12, ctypes.byref(ctypes.c_int(0)), 1, None)
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 13, ctypes.byref(ctypes.c_int(0)), 1, None)
            self.md.WriteProcessMemory(int(self.p), addr_zhuanshu + a * 16 + 14, ctypes.byref(ctypes.c_int(0)), 1, None)

        self.onPower()

    def onVar(self):
        while self.listview_var_1.rowCount() != 0:
            self.listview_var_1.removeRow(0)
        while self.listview_var_2.rowCount() != 0:
            self.listview_var_2.removeRow(0)
        while self.listview_var_3.rowCount() != 0:
            self.listview_var_3.removeRow(0)
        data = ctypes.c_int()
        a = int(self.var_input_1.toPlainText())
        if a > 4096:
            a = 0
        for i in range(a,min(a+100,4096)):
            self.md.ReadProcessMemory(int(self.p), 0x492FC8 + i * 4, ctypes.byref(data), 4, None)
            self.listview_var_1.insertRow(i-a)
            self.listview_var_1.setItem(i-a,0,QtWidgets.QTableWidgetItem(str(i)))
            if data.value == 0:
                self.listview_var_1.setItem(i-a,1,QtWidgets.QTableWidgetItem("False"))
                self.listview_var_1.item(i-a,1).setForeground(QtGui.QBrush(QtGui.QColor(0, 0, 255)))
            else:
                self.listview_var_1.setItem(i-a,1,QtWidgets.QTableWidgetItem("True"))
                self.listview_var_1.item(i-a,1).setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
            self.listview_var_1.setItem(i-a,2,QtWidgets.QTableWidgetItem('{:06X}'.format(0x492FC8+i*4)))
        a = int(self.var_input_2.toPlainText())
        if a > 4096:
            a = 0
        for i in range(a,min(a+100,4096)):
            self.md.ReadProcessMemory(int(self.p), 0x502000 + i * 4, ctypes.byref(data), 4, None)
            self.listview_var_2.insertRow(i-a)
            self.listview_var_2.setItem(i-a,0,QtWidgets.QTableWidgetItem(str(i)))
            self.listview_var_2.setItem(i-a,1,QtWidgets.QTableWidgetItem(str(data.value)))
            self.listview_var_2.setItem(i-a,2,QtWidgets.QTableWidgetItem('{:06X}'.format(0x502000+i*4)))
        a = int(self.var_input_3.toPlainText())
        if a > 4096:
            a = 0
        for i in range(a,min(a+100,4096)):
            self.md.ReadProcessMemory(int(self.p), 0x506000 + i * 4, ctypes.byref(data), 4, None)
            self.listview_var_3.insertRow(i-a)
            self.listview_var_3.setItem(i-a,0,QtWidgets.QTableWidgetItem(str(i)))
            self.listview_var_3.setItem(i-a,1,QtWidgets.QTableWidgetItem(str(data.value)))
            self.listview_var_3.setItem(i-a,2,QtWidgets.QTableWidgetItem('{:06X}'.format(0x506000+i*4)))   

    def saveVar(self, kind):
        if kind == 1:
            if self.listview_var_1.currentRow() >= 0:
                addr = self.listview_var_1.item(self.listview_var_1.currentRow(),2)
                value = self.listview_var_1.item(self.listview_var_1.currentRow(),1)
                if value.data(0) == "True" or value.data(0) == "1" or value.data(0) == "t":
                    data = 1
                else:
                    data = 0
                self.md.WriteProcessMemory(int(self.p), int(addr.data(0),16), ctypes.byref(ctypes.c_int(data)), 4, None)
        elif kind == 2:
            if self.listview_var_2.currentRow() >= 0:
                addr = self.listview_var_2.item(self.listview_var_2.currentRow(),2)
                value = self.listview_var_2.item(self.listview_var_2.currentRow(),1)
                data = int(value.data(0))
                self.md.WriteProcessMemory(int(self.p), int(addr.data(0),16), ctypes.byref(ctypes.c_int(data)), 4, None)
        elif kind == 3:
            if self.listview_var_3.currentRow() >= 0:
                addr = self.listview_var_3.item(self.listview_var_3.currentRow(),2)
                value = self.listview_var_3.item(self.listview_var_3.currentRow(),1)
                data = int(value.data(0))
                self.md.WriteProcessMemory(int(self.p), int(addr.data(0),16), ctypes.byref(ctypes.c_int(data)), 4, None)
        self.onVar() 

    def saveDIY(self):
        if self.listview_diy.currentRow() < 0:
            return
        n = self.listview_diy.currentRow()
        try:
            addr = int(self.listview_diy.item(n,3).text(),16)
            cnt = int(self.listview_diy.item(n,4).text(),16)
            num = int(self.listview_diy.item(n,1).text(),10)
            self.md.WriteProcessMemory(int(self.p), addr, ctypes.byref(ctypes.c_int(num)), cnt, None)
            self.DIY_Page(1)
        except:
            return

    def onMk(self):
        global addr_bisha
        data = ctypes.c_int()
        a = self.listview_mk.currentRow()
        #天赋
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16, ctypes.byref(data), 2, None)
        self.mk_input_1_1.setCurrentIndex(data.value)
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 3, ctypes.byref(data), 2, None)
        self.mk_input_1_3.setCurrentIndex(data.value)
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 6, ctypes.byref(data), 2, None)
        self.mk_input_1_5.setCurrentIndex(data.value)
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 9, ctypes.byref(data), 2, None)
        self.mk_input_1_7.setCurrentIndex(data.value)
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 12, ctypes.byref(data), 2, None)
        self.mk_input_1_9.setCurrentIndex(data.value)
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 2, ctypes.byref(data), 1, None)
        self.mk_input_1_2.setText(str(data.value))
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 5, ctypes.byref(data), 1, None)
        self.mk_input_1_4.setText(str(data.value))
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 8, ctypes.byref(data), 1, None)
        self.mk_input_1_6.setText(str(data.value))
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 11, ctypes.byref(data), 1, None)
        self.mk_input_1_8.setText(str(data.value))
        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 14, ctypes.byref(data), 1, None)
        self.mk_input_1_10.setText(str(data.value))

        self.md.ReadProcessMemory(int(self.p), addr_bisha + a * 16 + 15, ctypes.byref(data), 1, None)
        self.mk_input_1_11.setText(str(data.value))
    
    def saveMk(self):
        global addr_bisha
        a = self.listview_mk.currentRow()
        #天赋
        data = self.mk_input_1_1.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.mk_input_1_3.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 3, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.mk_input_1_5.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 6, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.mk_input_1_7.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 9, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = self.mk_input_1_9.currentIndex()
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 12, ctypes.byref(ctypes.c_int(data)), 2, None)
        data = int(self.mk_input_1_2.toPlainText())
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 2, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = int(self.mk_input_1_4.toPlainText())
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 5, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = int(self.mk_input_1_6.toPlainText())
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 8, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = int(self.mk_input_1_8.toPlainText())
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 11, ctypes.byref(ctypes.c_int(data)), 1, None)
        data = int(self.mk_input_1_10.toPlainText())
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 14, ctypes.byref(ctypes.c_int(data)), 1, None)

        data = int(self.mk_input_1_11.toPlainText())
        self.md.WriteProcessMemory(int(self.p), addr_bisha + a * 16 + 15, ctypes.byref(ctypes.c_int(data)), 1, None)

    def mousePressEvent(self, event):
        if event.buttons () == QtCore.Qt.LeftButton:
            if event.x()>self.label_pivot.x() and event.x()<self.label_pivot.x()+self.label_pivot.width()\
            and event.y()-20>self.label_pivot.y() and event.y()-20<self.label_pivot.y()+self.label_pivot.height():
                x = win32gui.LoadImage(0,'准星.cur',win32con.IMAGE_CURSOR,0,0,win32con.LR_LOADFROMFILE)
                win32api.SetCursor(x)
                self.label_pivot.setPixmap(QtGui.QPixmap(""))
                self.mouse_capture = True
    
    def mouseReleaseEvent(self, event):
        if self.mouse_capture == False:
            return
        #还原鼠标的图标
        x = win32gui.LoadImage(0,32512,win32con.IMAGE_CURSOR,0,0,win32con.LR_SHARED)
        win32api.SetCursor(x)
        #还原准星
        pix = QtGui.QPixmap('准星.png')
        self.label_pivot.setPixmap(pix)
        self.mouse_capture = False
        #捕获进程
        PROCESS_ALL_ACCESS = (0x000F0000|0x00100000|0xFFF)
        if self.process == NULL:
            print("Found an error, try to ignore it.")
            return
        self.p = win32api.OpenProcess(PROCESS_ALL_ACCESS, False, self.process.pid)
        self.md = ctypes.windll.LoadLibrary("C:\\Windows\\System32\\kernel32")
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), 0x40100E, ctypes.byref(data), 2, None)
        #检查进程是不是曹操传
        ccz = False
        if data.value == 0x774:
            ccz = True
        point = win32api.GetCursorPos()
        hwnd = win32gui.WindowFromPoint(point)
        clsname = win32gui.GetClassName(hwnd)
        if clsname == "豪华曹操传":
            ccz = True
        self.toolBar.setEnabled(ccz)
        self.widget_1.setEnabled(ccz)
        self.widget_2.setEnabled(ccz)
        self.ok = ccz
        if ccz == False:
            self.widget_1.show()
            self.widget_2.hide()
            self.widget_3.hide()
            self.widget_4.hide()
            self.widget_5.hide()
            self.widget_6.hide()
            self.widget_7.hide()
            self.widget_8.hide()
            return

        #确定版本
        global version
        if self.version_0.isChecked() == True:
            version = 0
        if self.version_1.isChecked() == True:
            res = self.getFileVersion()
            if res == '4':
                version = 0
                self.version_0.setChecked(True)
            elif res == '3':
                version = 2
                self.version_2.setChecked(True)
            elif res == '2':
                version = 3
                self.version_3.setChecked(True)
            else:
                version = 4
                self.version_4.setChecked(True)
        if self.version_2.isChecked() == True:
            version = 2
        if self.version_3.isChecked() == True:
            version = 3
        if self.version_4.isChecked() == True:
            version = 4

        if version == 2:
            data = ctypes.c_int()
            self.md.ReadProcessMemory(int(self.p), 0x41A8A0, ctypes.byref(data), 1, None)
            if data.value == 0x55:
                version = 1

        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        global life
        global cnt_item
        global addr_tianfu
        global addr_zhuanshu
        global addr_bisha
        global condition_change
        if version >= 1:
            addr_war = 0x4B2C50
            len_war = 0x24
            cnt_wo = 16
            cnt_you = 19
            cnt_di = 80
            cnt_item = 154
            life = b'\xE0\x92\x40\x00'
            addr_bisha = 0x508800
        else:
            addr_war = 0x4A7B20
            len_war = 0x30
            cnt_wo = 20
            cnt_you = 40
            cnt_di = 190
            cnt_item = 255
            life = b'\xC7\x92\x40\x00'
            addr_bisha = 0x511800
        if version >= 3:
            addr_zhuanshu = 0x50E800
        else:
            addr_zhuanshu = 0x50E400 
        if version == 4:
            life = b'\x0F\x93\x40\x00'
        if version == 0:
            addr_tianfu = 0x508998
        else:
            addr_tianfu = 0x5089B0
        if version == 0:
            data = ctypes.c_int()
            self.md.ReadProcessMemory(int(self.p), 0x4240CA, ctypes.byref(data), 1, None)
            if data.value == 0xFC:
                condition_change = True
                self.war_input_5.setVisible(False)
                self.war_input_6.setVisible(False)
                self.war_input_7.setVisible(False)
                self.war_input_8.setVisible(False)
                self.war_input_51.setVisible(True)
                self.war_input_52.setVisible(True)
                self.war_input_53.setVisible(True)
                self.war_input_54.setVisible(True)
            else:
                self.war_input_5.setVisible(True)
                self.war_input_6.setVisible(True)
                self.war_input_7.setVisible(True)
                self.war_input_8.setVisible(True)
                self.war_input_51.setVisible(False)
                self.war_input_52.setVisible(False)
                self.war_input_53.setVisible(False)
                self.war_input_54.setVisible(False)

        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), 0x401007, ctypes.byref(data), 2, None)
        if data.value == 0xF4E9:
            self.on_action_C_triggered()
            version = -1
        data = ctypes.c_int(0)
        #检查各个按钮的初始状态
        self.md.ReadProcessMemory(int(self.p), 4445556, ctypes.byref(data), 1, None)
        if data.value == 0x74:
            self.checkBox_1.setChecked(False)
        else:
            self.checkBox_1.setChecked(True)
        self.md.ReadProcessMemory(int(self.p), 0x4242B0, ctypes.byref(data), 1, None)
        if data.value == 0x90:
            self.checkBox_2.setChecked(True)
        else:
            self.checkBox_2.setChecked(False)
        self.md.ReadProcessMemory(int(self.p), 0x44E9D3, ctypes.byref(data), 1, None)
        if data.value == 0x74:
            self.checkBox_3.setChecked(False)
        else:
            self.checkBox_3.setChecked(True)
        self.md.ReadProcessMemory(int(self.p), 0x43D5DC, ctypes.byref(data), 1, None)
        if data.value == 0x74:
            self.checkBox_4.setChecked(False)
        else:
            self.checkBox_4.setChecked(True)
        self.md.ReadProcessMemory(int(self.p), 0x43F74F, ctypes.byref(data), 1, None)
        if data.value == 0x55:
            self.checkBox_5.setChecked(False)
        else:
            self.checkBox_5.setChecked(True)
        self.md.ReadProcessMemory(int(self.p), 0x4387B7, ctypes.byref(data), 1, None)
        if data.value == 0x74:
            self.checkBox_6.setChecked(False)
        else:
            self.checkBox_6.setChecked(True)
        self.md.ReadProcessMemory(int(self.p), 0x44E571, ctypes.byref(data), 1, None)
        if data.value == 0x8B:
            self.checkBox_7.setChecked(True)
        else:
            self.checkBox_7.setChecked(False)
        self.md.ReadProcessMemory(int(self.p), addr_war, ctypes.byref(data), 2, None)
        if data.value == 0xFFFF:
            self.checkBox_8.setChecked(False)
        else:
            self.md.ReadProcessMemory(int(self.p), addr_war+0xE, ctypes.byref(data), 1, None)
            if data.value == 7:
                self.checkBox_8.setChecked(False)
            else:
                self.checkBox_8.setChecked(True)
        data = ctypes.c_int()
        self.md.ReadProcessMemory(int(self.p), 0x404388, ctypes.byref(data), 1, None)
        if data.value == 0x55:
            self.checkBox_9.setChecked(False)
        else:
            self.checkBox_9.setChecked(True)

        #读入data人物列表
        #读取角色列表
        self.listview_data.clear()
        self.war_input_1.clear()
        self.power_input_1_1.clear()
        self.power_input_1_2.clear()
        self.power_input_1_3.clear()
        self.power_input_2_1.clear()
        self.power_input_2_4.clear()
        self.mk_input_1_1.clear()
        self.mk_input_1_3.clear()
        self.mk_input_1_5.clear()
        self.mk_input_1_7.clear()
        self.mk_input_1_9.clear()
        mem = ctypes.c_long()
        name = ctypes.c_byte()
        self.md.ReadProcessMemory(int(self.p), 0x4CEA00, ctypes.byref(mem), 4, None)
        for i in range(0,1024):
            names=b""
            for j in range(0,8):
                self.md.ReadProcessMemory(int(self.p), mem.value+i*0x48+j+8, ctypes.byref(name), 1, None)
                names+=name
            try:
                names=names.decode("gbk")
            except:
                names="非法字符"
            self.listview_data.addItem(str(i)+":"+names)
            self.war_input_1.addItem(str(i)+":"+names)
            self.power_input_1_1.addItem(str(i)+":"+names)
            self.power_input_1_2.addItem(str(i)+":"+names)
            self.power_input_1_3.addItem(str(i)+":"+names)
            self.power_input_2_1.addItem(str(i)+":"+names)
            self.power_input_2_4.addItem(str(i)+":"+names)
            self.mk_input_1_1.addItem(str(i)+":"+names)
            self.mk_input_1_3.addItem(str(i)+":"+names)
            self.mk_input_1_5.addItem(str(i)+":"+names)
            self.mk_input_1_7.addItem(str(i)+":"+names)
            self.mk_input_1_9.addItem(str(i)+":"+names)
        self.power_input_1_1.addItem("空")
        self.power_input_1_2.addItem("空")
        self.power_input_1_3.addItem("空")
        self.power_input_2_1.addItem("空")
        self.power_input_2_4.addItem("空")
        self.mk_input_1_1.addItem("空")
        self.mk_input_1_3.addItem("空")
        self.mk_input_1_5.addItem("空")
        self.mk_input_1_7.addItem("空")
        self.mk_input_1_9.addItem("空")

        #读取兵种名称
        self.data_input_31.clear()
        self.power_input_1_4.clear()
        for i in range(0,80):
            names=b""
            for j in range(0,9):
                self.md.ReadProcessMemory(int(self.p), 0x5000D0+i*0x9+j, ctypes.byref(name), 1, None)
                names+=name
            try:
                names=names.decode("gbk")
            except:
                names="非法字符"
            self.data_input_31.addItem(str(i)+":"+names)
            self.power_input_1_4.addItem(str(i)+":"+names)
        self.power_input_1_4.addItem("空")
        #读取宝物名称
        self.data_input_32.clear()
        self.data_input_35.clear()
        self.data_input_38.clear()
        self.item_input_1.clear()
        self.power_input_2_2.clear()
        self.power_input_2_5.clear()
        self.power_input_3_1.clear()
        self.power_input_3_2.clear()
        self.power_input_3_3.clear()
        self.power_input_3_5.clear()
        self.power_input_3_6.clear()
        self.power_input_3_7.clear()
        for i in range(0,cnt_item):
            '''if i >=87 and i <= 129:
                continue'''
            names=b""
            for j in range(0,12):
                self.md.ReadProcessMemory(int(self.p), 0x4A1140+i*25+j, ctypes.byref(name), 1, None)
                names+=name
            try:
                names=names.decode("gbk")
            except:
                names="非法字符"
            self.data_input_32.addItem(str(i)+":"+names)
            self.data_input_35.addItem(str(i)+":"+names)
            self.data_input_38.addItem(str(i)+":"+names)
            self.item_input_1.addItem(str(i)+":"+names)
            self.power_input_2_2.addItem(str(i)+":"+names)
            self.power_input_2_5.addItem(str(i)+":"+names)
            self.power_input_3_1.addItem(str(i)+":"+names)
            self.power_input_3_2.addItem(str(i)+":"+names)
            self.power_input_3_3.addItem(str(i)+":"+names)
            self.power_input_3_5.addItem(str(i)+":"+names)
            self.power_input_3_6.addItem(str(i)+":"+names)
            self.power_input_3_7.addItem(str(i)+":"+names)
        self.data_input_32.addItem("空")
        self.data_input_35.addItem("空")
        self.data_input_38.addItem("空")
        self.item_input_1.addItem("空")
        self.power_input_2_2.addItem("空")
        self.power_input_2_5.addItem("空")
        self.power_input_3_1.addItem("空")
        self.power_input_3_2.addItem("空")
        self.power_input_3_3.addItem("空")
        self.power_input_3_5.addItem("空")
        self.power_input_3_6.addItem("空")
        self.power_input_3_7.addItem("空")

        self.listview_item.clear()
        for i in range(0,256):
            self.listview_item.addItem("空")

        #读取消耗品名称
        self.listview_item_2.clear()
        if version >= 1:
            for i in range(0,43):
                names=b""
                for j in range(0,12):
                    self.md.ReadProcessMemory(int(self.p), 0x4A19BF+i*25+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gb18030")
                except:
                    print(names)
                    names="非法字符"
                self.listview_item_2.addItem(names)
        else:
            for i in range(0,105):
                names=b""
                for j in range(0,12):
                    self.md.ReadProcessMemory(int(self.p), 0x4A1FE6+i*25+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_item_2.addItem(names)

        #读取天赋/必杀
        self.listview_item_3.clear()
        self.listview_mk.clear()
        if version == 0:
            for i in range(0,180):
                names=b""
                for j in range(0,15):
                    self.md.ReadProcessMemory(int(self.p), 0x4FF560+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_item_3.addItem(str(i)+":"+names)
            for i in range(0,80):
                names=b""
                for j in range(0,11):
                    self.md.ReadProcessMemory(int(self.p), 0x4A7510+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_mk.addItem(str(i)+":"+names)
        elif version <= 2:
            for i in range(0,144):
                names=b""
                for j in range(0,15):
                    self.md.ReadProcessMemory(int(self.p), 0x4FF7A0+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_item_3.addItem(str(i)+":"+names)
            for i in range(0,36):
                names=b""
                for j in range(0,11):
                    self.md.ReadProcessMemory(int(self.p), 0x4FF551+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_mk.addItem(str(i)+":"+names)
        elif version == 3:
            self.md.ReadProcessMemory(int(self.p), 0x4F0000+i*16+j, ctypes.byref(name), 1, None)
            if name.value != 0:
                addr = 0x4F0000
                cnt = 126
            else:
                addr = 0x4FF960
                cnt = 91
            for i in range(0,cnt):
                names=b""
                for j in range(0,15):
                    self.md.ReadProcessMemory(int(self.p), addr+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_item_3.addItem(str(i)+":"+names)
            for i in range(0,36):
                names=b""
                for j in range(0,11):
                    self.md.ReadProcessMemory(int(self.p), 0x4FF710+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_mk.addItem(str(i)+":"+names)
        else:
            for i in range(0,88):
                names=b""
                for j in range(0,15):
                    self.md.ReadProcessMemory(int(self.p), 0x4FFA80+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_item_3.addItem(str(i)+":"+names)
            for i in range(0,36):
                names=b""
                for j in range(0,11):
                    self.md.ReadProcessMemory(int(self.p), 0x4FF710+i*16+j, ctypes.byref(name), 1, None)
                    names+=name
                try:
                    names=names.decode("gbk")
                except:
                    print(names)
                    names="非法字符"
                self.listview_mk.addItem(str(i)+":"+names)

        #初始设置
        self.listview_data.setCurrentRow(0)
        self.war_kind_1.setChecked(True)
        lock_list.clear()
        lock_hp.clear()
        lock_mp.clear()
        self.listview_war_2.clear()
        self.listview_item.setCurrentRow(0)
        self.listview_item_2.setCurrentRow(0)
        self.listview_item_3.setCurrentRow(0)
        self.listview_mk.setCurrentRow(0)

        self.onData()
        self.onWar(0)
        self.onItem()
        self.onVar()
        self.DIY_Page(0)
        self.diy_input_4.setCurrentIndex(0)

        #开启多线程
        if self.my_thread == NULL:
            self.my_thread = threading.Thread(target=self.LockThread)
            self.my_thread.setDaemon(True)
            self.my_thread.start()

    def mouseMoveEvent(self, event):
        if self.mouse_capture == True:
            point = win32api.GetCursorPos()
            hwnd = win32gui.WindowFromPoint(point)
            title = win32gui.GetWindowText(hwnd)
            clsname = win32gui.GetClassName(hwnd)
            hread_id, self.process_id = win32process.GetWindowThreadProcessId(hwnd)  #线程ID  进程ID
            self.process = psutil.Process(self.process_id)
            self.label_window1.setText(title)
            self.label_window2.setText(clsname)

    def changeEvent(self, event):
        if event.type() == QtCore.QEvent.ActivationChange:
            if self.window().isActiveWindow():
                if self.ok == True:
                    self.onData()
                    self.onWar(0)
                    self.onItem()
                    self.onPower()
                    self.onVar()
                    self.DIY_Page(1)

    def recal(self):
        if len(self.listview_data.selectedIndexes())<=0:
            return
        n = self.listview_data.selectedIndexes()[0].row()
        mem = ctypes.c_long()
        self.md.ReadProcessMemory(int(self.p), 0x4CEA00, ctypes.byref(mem), 4, None)
        hk = my_hook()
        hk.recal(self.p, mem.value+0x48*n)
        del hk

    def refreshFangzhen(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        if self.war_input_11.currentIndex() == 3 or self.war_input_11.currentIndex() == 5:
            self.war_12.show()
            self.war_input_12.show()
            self.war_input_12.clear()
            data2 = ctypes.c_int()
            data = ctypes.c_int()
            name = ctypes.c_byte()
            mem = ctypes.c_int()
            self.md.ReadProcessMemory(int(self.p), 0x4CEA00, ctypes.byref(mem), 4, None)
            for i in range(0,cnt_wo + cnt_you + cnt_di):
                self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war, ctypes.byref(data), 2, None)
                if data.value!=65535:
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war + 5, ctypes.byref(data2), 1, None)
                    names=b""
                    for j in range(0,8):
                        self.md.ReadProcessMemory(int(self.p), mem.value+data.value*0x48+j+8, ctypes.byref(name), 1, None)
                        names+=name
                    try:
                        names=names.decode("gbk")
                    except:
                        names="非法字符"
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war+4, ctypes.byref(data2), 1, None)
                    self.war_input_12.addItem(str(data2.value)+":"+names)
                self.war_input_12.setCurrentIndex(0)
        else:
            self.war_12.hide()
            self.war_input_12.hide()

    def onConnect(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        data = ctypes.c_int()
        war_code = 0
        if self.war_kind_1.isChecked() == True:
            war_code = self.listview_war.currentRow()
        if self.war_kind_2.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo
        if self.war_kind_3.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo + cnt_you
        self.md.ReadProcessMemory(int(self.p), addr_war + len_war*war_code, ctypes.byref(data), 2, None)
        self.listview_data.setCurrentRow(data.value)
        self.on_action_M_triggered()

    def onKill(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        x1 = int(self.war_input_47.toPlainText())
        y1 = int(self.war_input_48.toPlainText())
        x2 = int(self.war_input_49.toPlainText())
        y2 = int(self.war_input_50.toPlainText())
        for i in range(cnt_wo + cnt_you,cnt_wo + cnt_you + cnt_di):
            x0 = ctypes.c_int(0)
            y0 = ctypes.c_int(0)
            self.md.ReadProcessMemory(int(self.p), addr_war+len_war*i+6, ctypes.byref(x0), 1, None)
            self.md.ReadProcessMemory(int(self.p), addr_war+len_war*i+7, ctypes.byref(y0), 1, None)
            if x1<=x0.value and x2>=x0.value and y1<=y0.value and y2>=y0.value:
                self.md.WriteProcessMemory(int(self.p), addr_war+len_war*i+0x10, ctypes.byref(ctypes.c_int(0)), 4, None)

    def onLife(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        global life
        data = ctypes.c_int()
        war_code = 0
        if self.war_kind_1.isChecked() == True:
            war_code = self.listview_war.currentRow()
        if self.war_kind_2.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo
        if self.war_kind_3.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo + cnt_you
        if self.war_input_16.currentIndex() == 0:
            self.md.ReadProcessMemory(int(self.p), addr_war + len_war*war_code+0xF, ctypes.byref(data), 1, None)
            dir = data.value
        else:
            dir = self.war_input_16.currentIndex() - 1
        x = int(self.war_input_9.toPlainText())
        y = int(self.war_input_10.toPlainText())
        self.md.ReadProcessMemory(int(self.p), addr_war + len_war*war_code, ctypes.byref(data), 2, None)
        hk = my_hook()
        hk.life(self.p, dir, x, y, data.value, life)
        self.war_life.setEnabled(False)
        self.war_life.setStyleSheet("background-color:rgb(255, 255, 255);\ncolor:rgb(190,190,190)")
        self.onWar(1)
        del hk

    def onLock(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        if self.listview_war.currentRow() == -1:
            return
        war_code = 0
        if self.war_kind_1.isChecked() == True:
            war_code = self.listview_war.currentRow()
        if self.war_kind_2.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo
        if self.war_kind_3.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo + cnt_you
        self.listview_war_2.addItem(self.listview_war.item(self.listview_war.currentRow()).text())
        lock_list.append(war_code)
        data = ctypes.c_int()
        #HPCur
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x10, ctypes.byref(data), 4, None)
        lock_hp.append(data.value)
        #MPCur
        self.md.ReadProcessMemory(int(self.p), addr_war+war_code*len_war+0x14, ctypes.byref(data), 4, None)
        lock_mp.append(data.value)

    def offLock(self):
        if self.listview_war_2.currentRow() == -1:
            return
        del lock_list[self.listview_war_2.currentRow()]
        del lock_hp[self.listview_war_2.currentRow()]
        del lock_mp[self.listview_war_2.currentRow()]
        self.listview_war_2.takeItem(self.listview_war_2.currentRow())

    def LockThread(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di

        global lock_list
        global lock_hp
        global lock_mp
        
        while True:
            pl = psutil.pids()
            ccz = False
            for pid in pl:
                if pid == self.process_id:
                    ccz = True
                    break
            if ccz == False:
                self.toolBar.setEnabled(ccz)
                self.widget_1.setEnabled(ccz)
                self.widget_2.setEnabled(ccz)
                self.ok = ccz
                self.widget_1.show()
                self.widget_2.hide()
                self.widget_3.hide()
                self.widget_4.hide()
                self.widget_5.hide()
                self.widget_6.hide()
                self.widget_7.hide()
                self.widget_8.hide()
                return

            if auto_life == True:
                for i in range(0,cnt_wo):
                    code = ctypes.c_int(0)
                    hp = ctypes.c_int(0)
                    view = ctypes.c_int(0)
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war, ctypes.byref(code), 4, None)
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war+0x10, ctypes.byref(hp), 4, None)
                    self.md.ReadProcessMemory(int(self.p), addr_war+i*len_war+0xC, ctypes.byref(view), 1, None)
                    if hp.value == 0 and code.value!=0xFFFF and view.value == 3:
                        dir = ctypes.c_int(0)
                        x = ctypes.c_int(0)
                        y = ctypes.c_int(0)
                        self.md.ReadProcessMemory(int(self.p), addr_war + len_war*i+0xF, ctypes.byref(dir), 1, None)
                        self.md.ReadProcessMemory(int(self.p), addr_war + len_war*i+6, ctypes.byref(x), 1, None)
                        self.md.ReadProcessMemory(int(self.p), addr_war + len_war*i+7, ctypes.byref(y), 1, None)
                        hk = my_hook()
                        hk.life(self.p, dir.value, x.value, y.value, code.value, life)

            if len(lock_list)!=len(lock_hp) or len(lock_list)!=len(lock_mp):
                continue
            for i in range(0,len(lock_list)):
                #HPCur
                data = ctypes.c_int(lock_hp[i])
                self.md.WriteProcessMemory(int(self.p), addr_war+lock_list[i]*len_war+0x10, ctypes.byref(data), 4, None)
                #MPCur
                data = ctypes.c_int(lock_mp[i])
                self.md.WriteProcessMemory(int(self.p), addr_war+lock_list[i]*len_war+0x14, ctypes.byref(data), 4, None)
            time.sleep(1)

    def getFileVersion(self):
        import os
        info = win32api.GetFileVersionInfo(self.process.exe(), os.sep)
        ms = info['FileVersionMS']
        ls = info['FileVersionLS']
        version = '%d' % (win32api.LOWORD(ls))
        print(version)
        return version
    def onTurn(self):
        global addr_war
        global len_war
        global cnt_wo
        global cnt_you
        global cnt_di
        if self.war_input_16.currentIndex() <=0:
            return
        data = ctypes.c_int()
        war_code = 0
        if self.war_kind_1.isChecked() == True:
            war_code = self.listview_war.currentRow()
        if self.war_kind_2.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo
        if self.war_kind_3.isChecked() == True:
            war_code = self.listview_war.currentRow() + cnt_wo + cnt_you
        self.md.ReadProcessMemory(int(self.p), addr_war + len_war*war_code, ctypes.byref(data), 2, None)

        hk = my_hook()
        hk.changeDir(self.p, self.war_input_16.currentIndex()-1, data.value)
        self.onWar(1)
        del hk

    def allItem(self, n):
        global cnt_item
        if n == 1:
            a = 0
            i = 0
            while True:
                data = ctypes.c_int()
                self.md.ReadProcessMemory(int(self.p), 0x4B0783 + i * 3, ctypes.byref(data), 1, None)
                if data.value != 255:
                    i += 1
                    continue
                if version >= 1:
                    if a == 87:
                        a = 130
                    if a == cnt_item:
                        break
                else:
                    if a == 150:
                        break

                data = ctypes.c_int()
                self.md.ReadProcessMemory(int(self.p), 0x4A1140+a*25+0x14, ctypes.byref(data), 1, None)
                if data.value == 255:
                    a += 1
                    continue
                data = ctypes.c_int(a)
                self.md.WriteProcessMemory(int(self.p), 0x4B0783 + i * 3, ctypes.byref(data), 1, None)
                data = ctypes.c_int(int(self.item_input_2.toPlainText()))
                if data.value > 9:
                    data.value = 9
                self.md.WriteProcessMemory(int(self.p), 0x4B0783 + i * 3 + 1, ctypes.byref(data), 1, None)
                data2 = ctypes.c_int(int(self.item_input_3.toPlainText()))
                if data2.value == 255 and data.value != 9:
                    data2.value = 250
                self.md.WriteProcessMemory(int(self.p), 0x4B0783 + i * 3 + 2, ctypes.byref(data2), 1, None)
                a += 1
        if n == 2:
            if version >= 1:
                for i in range(0,43):
                    data = ctypes.c_int(255)
                    if i <= 16:
                        self.md.WriteProcessMemory(int(self.p), 0x4B09DB + i, ctypes.byref(data), 1, None)
                    else:
                        self.md.WriteProcessMemory(int(self.p), 0x510c80 + i-17, ctypes.byref(data), 1, None)
            else:
                for i in range(0,105):
                    data = ctypes.c_int(255)
                    self.md.WriteProcessMemory(int(self.p), 0x510c80 + i, ctypes.byref(data), 1, None)
        if n == 3:
            for i in range(0,256):
                data = ctypes.c_int(255)
                self.md.WriteProcessMemory(int(self.p), 0x4B0783 + i * 3, ctypes.byref(data), 1, None)
            if version >= 1:
                for i in range(0,43):
                    data = ctypes.c_int(0)
                    if i <= 16:
                        self.md.WriteProcessMemory(int(self.p), 0x4B09DB + i, ctypes.byref(data), 1, None)
                    else:
                        self.md.WriteProcessMemory(int(self.p), 0x510c80 + i-17, ctypes.byref(data), 1, None)
            else:
                for i in range(0,105):
                    data = ctypes.c_int(0)
                    self.md.WriteProcessMemory(int(self.p), 0x510c80 + i, ctypes.byref(data), 1, None)
        self.onItem()

    def DIY_Page(self, n):
        global cnt_item
        while self.listview_diy.rowCount() != 0:
            self.listview_diy.removeRow(0)
        dirname = "DIY.csv"
        try:
            with open(dirname) as csvfile:
                a = 1
        except:
            return
        #初始化
        if n == 0:
            self.diy_input_4.clear()
            with open(dirname) as csvfile:
                csv_reader = csv.reader(csvfile)
                for row in csv_reader:
                    if row[0] != '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] == '' and row[5] == '':
                        self.diy_input_4.addItem(row[0])
            return
        #显示数据
        with open(dirname) as csvfile:
            csv_reader = csv.reader(csvfile)
            table = -1
            a = 0
            for row in csv_reader:
                if table != self.diy_input_4.currentIndex():
                    if row[0] != '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] == '' and row[5] == '':
                        table += 1
                        if table == self.diy_input_4.currentIndex():
                            next(csv_reader)
                    continue
                if row[0] != '' and row[1] == '' and row[2] == '' and row[3] == '' and row[4] == '' and row[5] == '':
                    break
                xunhuan = int(row[4])
                for i in range(0,xunhuan):
                    '''if (int(row[2],16) >= 0x492FC8 and int(row[2],16) < 0x496FC8) or\
                        (int(row[2],16) >= 0x502000 and int(row[2],16) < 0x50A000):
                        continue'''
                    self.listview_diy.insertRow(a)
                    if xunhuan == 1:
                        self.listview_diy.setItem(a,0,QtWidgets.QTableWidgetItem(row[0]))
                    else:
                        self.listview_diy.setItem(a,0,QtWidgets.QTableWidgetItem(row[0]+"_"+str(i)))
                    self.listview_diy.setItem(a,3,QtWidgets.QTableWidgetItem('{:X}'.format(int(row[2],16)+i*int(row[3]),16)))
                    self.listview_diy.setItem(a,4,QtWidgets.QTableWidgetItem(row[3]))
                    self.listview_diy.setItem(a,5,QtWidgets.QTableWidgetItem(row[5]))
                    data = ctypes.c_int()
                    self.md.ReadProcessMemory(int(self.p), int(row[2],16)+i*int(row[3]), ctypes.byref(data), int(row[3]), None)
                    self.listview_diy.setItem(a,1,QtWidgets.QTableWidgetItem(str(data.value)))
                    if row[1] == "战场编号":
                        tmp = data.value
                        self.md.ReadProcessMemory(int(self.p), addr_war+tmp*len_war, ctypes.byref(data), 2, None)
                        if data.value >= 1024:
                            strs = "空"
                        else:
                            strs = self.listview_data.item(data.value).text()
                        self.listview_diy.setItem(a,2,QtWidgets.QTableWidgetItem(strs))
                    elif row[1] == "Data编号":
                        if data.value >= 1024:
                            strs = "无效编号"
                        else:
                            strs = self.listview_data.item(data.value).text()
                        self.listview_diy.setItem(a,2,QtWidgets.QTableWidgetItem(strs))
                    elif row[1] == "宝物":
                        if data.value >= cnt_item:
                            strs = "无效编号"
                        else:
                            strs = self.item_input_1.itemText(data.value)
                        self.listview_diy.setItem(a,2,QtWidgets.QTableWidgetItem(strs))
                    a += 1