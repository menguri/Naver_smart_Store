from cmath import nan
from urllib.request import urlopen
from bs4 import BeautifulSoup as bs
from urllib.parse import quote_plus
import pandas as pd

from math import nan
from selenium.webdriver.chrome.options import Options
import selenium
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
import re
import os
import sys
from unicodedata import category
from time import sleep
import datetime
import pandas as pd
from openpyxl.workbook import Workbook
from urllib.request import urlopen
import requests
from bs4 import BeautifulSoup as bs4
from html_table_parser import parser_functions as parser
import collections
if not hasattr(collections, 'Callable'):
    collections.Callable = collections.abc.Callable
import json


# 절대 경로
def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(relative_path)))
    return os.path.join(base_path, relative_path)

# 크롬 경로
chrome_exe = resource_path('chromedriver.exe')

# 크롬 옵션
options = webdriver.ChromeOptions()
options.add_experimental_option('excludeSwitches', ['enable-logging'])
options.add_argument("--no-sandbox")
options.add_argument("--disable-setuid-sandbox")
options.add_argument("start-maximized")
options.add_argument("--disable-software-rasterizer")
options.add_argument('headless')
options.add_argument('window-size=1920x1080')
options.add_argument("disable-gpu")


link = "https://smartstore.naver.com/snkrbuilding/products/7055655958"

# # 1. 크롤링 입장
driver = webdriver.Chrome(executable_path=chrome_exe, chrome_options=options)
driver.get(url=link)
# 해당하는 링크(count 수만큼) 차곡차곡 정리하기
sleep(2)
link_list = []
html = driver.page_source
soup = bs4(html, 'html.parser')

item=soup.select_one('script[data-react-helmet="true"]').text
jsondata=json.loads(item)
c_list = jsondata['category'].split('>')
cate = pd.read_csv(r"C:\Users\M207\Desktop\kang\code_factory\SmartStoreCrawling\category.csv", encoding='cp949')

if len(c_list) == 1:
    a = cate[cate['대분류'] == c_list[0]]
elif len(c_list) == 2:
    a = cate[(cate['대분류'] == c_list[0])&(cate['중분류'] == c_list[1])]
elif len(c_list) == 3:
    a = cate[(cate['대분류'] == c_list[0])&(cate['중분류'] == c_list[1])&(cate['소분류'] == c_list[2])]
else:
    a = cate[(cate['대분류'] == c_list[0])&(cate['중분류'] == c_list[1])&(cate['소분류'] == c_list[2])&(cate['세분류'] == c_list[3])]

    
print(c_list)
print(a)
print(a['카테고리번호'].tolist()[0])

