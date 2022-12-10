# import -------------------------------------------------------------------------------
from selenium.webdriver.chrome.options import Options
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
import re
import os
import sys
from unicodedata import category
from time import sleep
import datetime
import pandas as pd
from openpyxl.workbook import Workbook
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from urllib.parse import quote_plus
import requests
from bs4 import BeautifulSoup as bs4
from html_table_parser import parser_functions as parser
import collections
# if not hasattr(collections, 'Callable'):
#     collections.Callable = collections.abc.Callable
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtGui import QIcon
from PyQt5 import QtCore
from PyQt5.QtCore import QCoreApplication
# import def
import function
# import end -------------------------------------------------------------------------------

# 경로 설정 ---------------------------------------------------------------------------------
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(relative_path)))
    return os.path.join(base_path, relative_path)

# 크롬, UI 경로
chrome_exe = resource_path('chromedriver.exe')
form_1 = resource_path('1.ui')
form_2 = resource_path('2.ui')
form_3 = resource_path('3.ui')
form_4 = resource_path('4.ui')
# UI파일 연결
form_class_1 = uic.loadUiType(form_1)[0]
form_class_2 = uic.loadUiType(form_2)[0]
form_class_3 = uic.loadUiType(form_3)[0]
form_class_4 = uic.loadUiType(form_4)[0]
# 경로 설정 end ---------------------------------------------------------------------------------

# option 설정 ---------------------------------------------------------------------------------
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox")
options.add_argument("start-maximized")
options.add_argument("--disable-software-rasterizer")
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")
# option 설정 end ---------------------------------------------------------------------------------

# DataFrmae MVC class 선언 ---------------------------------------------------------------------------------
class DataFrameModel(QtCore.QAbstractTableModel):
    DtypeRole = QtCore.Qt.UserRole + 1000
    ValueRole = QtCore.Qt.UserRole + 1001

    def __init__(self, df=pd.DataFrame(), parent=None):
        super(DataFrameModel, self).__init__(parent)
        self._dataframe = df

    def setDataFrame(self, dataframe):
        self.beginResetModel()
        self._dataframe = dataframe.copy()
        self.endResetModel()

    def dataFrame(self):
        return self._dataframe

    dataFrame = QtCore.pyqtProperty(pd.DataFrame, fget=dataFrame, fset=setDataFrame)

    @QtCore.pyqtSlot(int, QtCore.Qt.Orientation, result=str)
    def headerData(self, section: int, orientation: QtCore.Qt.Orientation, role: int = QtCore.Qt.DisplayRole):
        if role == QtCore.Qt.DisplayRole:
            if orientation == QtCore.Qt.Horizontal:
                return self._dataframe.columns[section]
            else:
                return str(self._dataframe.index[section])
        return QtCore.QVariant()

    def rowCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return len(self._dataframe.index)

    def columnCount(self, parent=QtCore.QModelIndex()):
        if parent.isValid():
            return 0
        return self._dataframe.columns.size

    def data(self, index, role=QtCore.Qt.DisplayRole):
        if not index.isValid() or not (0 <= index.row() < self.rowCount() \
            and 0 <= index.column() < self.columnCount()):
            return QtCore.QVariant()
        row = self._dataframe.index[index.row()]
        col = self._dataframe.columns[index.column()]
        dt = self._dataframe[col].dtypes

        val = self._dataframe.iloc[row][col]
        if role == QtCore.Qt.DisplayRole:
            return str(val)
        elif role == DataFrameModel.ValueRole:
            return val
        if role == DataFrameModel.DtypeRole:
            return dt
        return QtCore.QVariant()

    def roleNames(self):
        roles = {
            QtCore.Qt.DisplayRole: b'display',
            DataFrameModel.DtypeRole: b'dtype',
            DataFrameModel.ValueRole: b'value'
        }
        return roles

# DataFrmae MVC class 선언 END ---------------------------------------------------------------------------------

# GUI class 선언 ---------------------------------------------------------------------------------
class WindowClass(QMainWindow, form_class_1) :
    def __init__(self) :
        super().__init__()
        self.setupUi(self)
        self.code = ""
    
    def input_code(self):
        code = self.code_edit.toPlainText()
        if function.code_avail(code) == True:
            self.hide()
            self.second = secondwindow()
            self.second.show()
            self.close()
        else:
            print("코드를 다시 입력하세요.")


class secondwindow(QMainWindow, form_class_2) :
    def __init__(self) :
        super().__init__()
        self.initUi()
        self.show()
        self.category_list = ""
        self.link = ""
        self.category = ""
        self.count = ""
        self.sort = ""
        self.as_num = ""
        self.as_info = ""
        self.price = ""
        self.method = ""
        self.ban = ""
        self.remove = ""
        self.storage_location = ""
        self.df = pd.DataFrame()


    def initUi(self):
        self.setupUi(self)
        as_df = pd.read_csv(resource_path("as.csv"))
        ban_df = pd.read_csv(resource_path("ban.csv"))
        ban_list = ",".join(ban_df['금지어'].tolist())
        self.as_num_edit.setPlainText(str(as_df['A/S 전화번호'][0]))
        self.as_info_edit.setPlainText(as_df['A/S 안내내용'][0])
        self.price_edit.setPlainText(str(as_df['판매가 추가'][0]))
        self.method_edit.setPlaceholderText(as_df['방식'][0])
        self.ban_edit.setPlainText(ban_list)
        
    def html_settings(self):
        self.hide()
        self.third = thirdwindow()
        self.third.show()
        self.close()

    def step0(self):
        self.link = self.link_edit.text()
        try:
            self.category_list = function.step0(self.link)
            self.category_edit.addItems(self.category_list)
        except:
            pass

    def remove_row(self):
        try:
            self.remove = list(map(int, self.remove_edit.toPlainText().split(',')))
            self.df = function.remove_row(self.df, self.remove)
            model = DataFrameModel(self.df)
            self.dataframe_table.setModel(model)
        except:
            pass
    
    def crawling_start(self):
        self.category = self.category_edit.currentText()
        self.count = self.count_edit.value()
        self.sort = self.sort_edit.currentText()
        try:
            if self.link ==  "" or self.category == "" or self.sort == "":
                pass
            else:
                step1_df = function.step1(self.link, self.category, self.sort, self.count)
                step2_df = function.step2(step1_df)
                step3_df = function.step3(step2_df)
                self.df = function.step4(step3_df)
            model = DataFrameModel(self.df)
            self.dataframe_table.setModel(model)
        except:
            print('크롤링에 실패했습니다.')
            pass


    def replace_ban(self):
        ban = self.ban_edit.toPlainText()
        ban_list = ban.split(',')
        try:
            function.replace_ban(ban_list)
        except:
            print('삭제에 실패했습니다.')
            pass

    def replace_as(self):
        as_num = self.as_num_edit.toPlainText()
        as_info = self.as_info_edit.toPlainText()
        price = self.price_edit.toPlainText()
        method = self.method_edit.currentText()
        try:
            function.replace_as(as_num, as_info, price, method)
        except:
            pass

    def final(self):
        self.storage_location = self.storage_edit.toPlainText()
        try:
            function.final(self.df, self.storage_location) 
        except:
            pass
    
    def file_find(self):
        fname = QFileDialog.getExistingDirectory(self, 'Select Folder')
        self.storage_edit.setText(fname)


class thirdwindow(QMainWindow, form_class_3) :
    def __init__(self) :
        super().__init__()
        self.initUi()
        self.show()
        self.up = ""
        self.down = ""
        self.html = ""

    def initUi(self):
        self.setupUi(self)
        html_df = pd.read_csv(resource_path("html.csv"))
        self.up_image_edit.setPlainText(html_df['상단이미지'][0])
        self.html_edit.setPlainText(html_df['html'][0])
        self.down_image_edit.setPlainText(html_df['하단이미지'][0])

    def home_settings(self):
        self.hide()
        self.second = secondwindow()
        self.second.show()
        self.close()

    def replace_html(self):
        up = self.up_image_edit.toPlainText()
        html = self.html_edit.toPlainText()
        down = self.down_image_edit.toPlainText()
        try:
            function.replace_html(up, html, down)
        except:
            pass


class forthDialog(QMainWindow, form_class_4) :
    def __init__(self) :
        super().__init__()
        self.initUi()
        self.show()

    def initUi(self):
        self.setupUi(self)




if __name__ == "__main__" :
    #QApplication : 프로그램을 실행시켜주는 클래스
    app = QApplication(sys.argv) 

    #WindowClass의 인스턴스 생성
    myWindow = WindowClass() 

    #프로그램 화면을 보여주는 코드
    myWindow.show()

    #프로그램을 이벤트루프로 진입시키는(프로그램을 작동시키는) 코드
    app.exec_()


# GUI class 선언 end ---------------------------------------------------------------------------------