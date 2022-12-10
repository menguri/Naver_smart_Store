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


# step 0 - 카테고리 데이터 받아오기
def step0(link):
    response = requests.get(link)
    cate_list = []
    if response.status_code == 200:
        html = response.text
        soup = bs4(html, 'html.parser')
        # 카테고리 부분 크롤링
        for href in soup.find_all('li', {'class':'_2jm5JW3D5W type_white_gnb YI_nVHGI_0 N=a:lca.depth1'}):
            cate_list.insert(-1, href.text)
        for href in soup.find_all('li', {'class':'_2jm5JW3D5W type_white_gnb YI_nVHGI_0 N=a:lca.all'}):
            cate_list.insert(0, href.text)

    if cate_list[0] == "전체상품":
        cate_list = ["전체상품"]
    
    return cate_list


# step 1 - 기본적인 상품 데이터를 크롤링하는 함수
def step1(link, category, sort, count):
    print("step1 시작~~!!")
    global sort_list, cate_list
    df = pd.DataFrame(columns=['상품상태'])
    category_csv = pd.read_csv(resource_path('category.csv'), encoding='cp949')
    print(1)

    # 1. 크롤링 입장
    driver = webdriver.Chrome(executable_path=chrome_exe, chrome_options=options)
    driver.get(url=link)

    # 2. 카테고리/정렬까지 선택.
    sleep(2)
    try:
        driver.find_element(By.XPATH, f'//a[text()="{category}"]').click()
    except:
        driver.find_element(By.XPATH, f'//button[text()="더보기"]').click()
        driver.find_element(By.XPATH, f'//a[text()="{category}"]').click()
    sleep(2)
    driver.find_element(By.XPATH, f'//button[text()="{sort}"]').click()

    # 해당하는 링크(count 수만큼) 차곡차곡 정리하기
    sleep(2)
    link_list = []
    html = driver.page_source
    soup = bs4(html, 'html.parser')
    n = 1
    # Q: 왜 첫번째꺼가 맨 뒤로 가지?
    for href in soup.find_all("li", "-qHwcFXhj0"):
        if n > count:
            break
        else:
            link_list.insert(0, href.find("a")["href"])
            n += 1
    
    # 3. 링크 리스트 for문으로 돌리면서 dataframe 가져오기
    link_list.reverse()
    for i in link_list:
        driver.get(url="https://smartstore.naver.com"+i)
        sleep(4)
        # 상품상태, 상품번호, 상품명, 판매가, 대표이미지 url, 제조사, 브랜드, 배송방법, 배송비유형, 기본배송비, 반품배송비, 교환배송비
        # table의 경우, table을 자체적으로 가져와보자.
        # 페이지 소스 가져오기
        html = driver.page_source
        soup = bs4(html, 'html.parser')
        
        # 카테고리ID 확보
        item=soup.select_one('script[data-react-helmet="true"]').text
        jsondata=json.loads(item)
        c_list = jsondata['category'].split('>')

        if len(c_list) == 1:
            a = category_csv[category_csv['대분류'] == c_list[0]]
        elif len(c_list) == 2:
            a = category_csv[(category_csv['대분류'] == c_list[0])&(category_csv['중분류'] == c_list[1])]
        elif len(c_list) == 3:
            a = category_csv[(category_csv['대분류'] == c_list[0])&(category_csv['중분류'] == c_list[1])&(category_csv['소분류'] == c_list[2])]
        else:
            a = category_csv[(category_csv['대분류'] == c_list[0])&(category_csv['중분류'] == c_list[1])&(category_csv['소분류'] == c_list[2])&(category_csv['세분류'] == c_list[3])]
        category_id = str(a['카테고리번호'].tolist()[0])

        # 상품이름, 상품가격, 대표 이미지, 택배 배송, 배송비
        product_name = soup.find('h3', {'class':'_3oDjSvLwq9 _copyable'}).text
        product_price = int(soup.find('span', {'class':'_1LY7DqCnwR'}).text.replace(',',''))
        product_image = soup.find('img', {'class':'_2P2SMyOjl6'}).get('src')
        shipping_method = "택배배송"
        normal_fee = "3000"
        aa = "50"
        bb = "과세상품"
        cc = "Y"
        dd = "Y"
        ee = "0200037"
        ff = "상품상세참조"
        gg = "N"
        hh = "유료"
        ii = "선결제"
        jj = "0"
        kk = "50"
        ll = "3000"
        oo = "6000"
        nn = "3000"

        list_df = [[category_id, product_name, product_price, product_image, shipping_method, normal_fee, aa, bb, cc, dd, ee, ff, gg, hh, ii, jj, kk, ll, oo, nn]]
        exam_df = pd.DataFrame(list_df, columns = ['카테고리ID','상품명', '원_판매가', '대표_이미지_파일명', '배송방법', '기본배송비', '재고수량','부가세','미성년자_구매','구매평_노출여부','원산지_코드','수입사','복수원산지_여부','배송비_유형','배송비_결제방식','조건부무료_상품판매가합계','수량별부과_수량','반품배송비','교환배송비','지역별_차등배송비_정보'])
        # 상품번호, 상품상태, 제조사, 브랜드, 모델명, 원산지
        table_data = soup.find('table', {'class':'_1_UiXWHt__'})
        table = parser.make2d(table_data)
        table_data = [[]]
        table_columns = []
        for i in table:
            table_columns.insert(0, i[0])
            table_columns.insert(0, i[1])
            table_data[0].insert(0, i[2])
            table_data[0].insert(0, i[3])
        table_df = pd.DataFrame(data=table_data, columns=table_columns)
        
        # dataframe 합치기
        df_e = pd.concat([exam_df,table_df],axis=1)
        # 최종 dataframe에 합치기
        df = pd.concat([df,df_e], axis=0)
    driver.quit()
    df.reset_index(drop=True,inplace=True)
    return df


# step 2 - 기존 내용(csv 파일 저장)인 AS 전화번호, AS 안내내용, 판매가 추가금액 -> 데이터 프레임에 추가하는 함수
def step2(df):
    print("step2 시작~~!!")
    as_info = pd.read_csv(resource_path('as.csv'))

    # A/S 정보는 일괄 추가
    as_info_df = as_info[['A/S 전화번호', 'A/S 안내내용']].copy()
    for i in range(len(df)-1):
        as_info_df = pd.concat([as_info_df, as_info_df.loc[[0]]], axis=0, ignore_index=True)

    as_info_df.columns = ['AS_전화번호', 'AS_안내내용']
    df = pd.concat([df,as_info_df], axis=1)

    # 추가된 판매가
    sale_plus = as_info[['판매가 추가','방식']].copy()
    if sale_plus['방식'][0] == '원' :
        # df['판매가'] = df['판매가'] + sale_plus['판매가 추가'][0]
        df.insert(2, '판매가', df['원_판매가'] + sale_plus['판매가 추가'][0])
    else:
        # df['판매가'] = df['판매가'] * (1 + sale_plus['판매가 추가'][0]*0.01)
        df.insert(2, '판매가', df['원_판매가'] * (1 + sale_plus['판매가 추가'][0]*0.01))
    df.drop('원_판매가', axis=1, inplace=True)
    # 최종 결과물
    return df


# step 3 - 기존 내용(csv 파일 저장)을 바탕으로, 금지어로 필터링 함수
def step3(df):
    print("step3 시작~~!!")
    ban = pd.read_csv(resource_path('ban.csv'))
    ban_list = ban['금지어'].values.tolist()

    # 상품이름에서 ban 키워드들을 필터링
    df = df[~df['상품명'].str.contains('|'.join(ban_list))]
    df.reset_index(drop=True,inplace=True)

    # 최종 결과물
    return df


# step 4 - 기존 내용(csv 파일 저장)을 바탕으로, HTML 변환해서 데이터 프레임에 넣어주는 함수
def step4(df):
    print("step4 시작~~!!")
    html_df = pd.read_csv(resource_path('html.csv'))    

    # HTML 코드 넣기
    html_list = []
    for i in range(len(df)):
        html_list.append([html_df['html'][0].format(up_image=html_df['상단이미지'][0], goods_rename=df['상품명'][i], goods_image=df['대표_이미지_파일명'][i], down_image=html_df['하단이미지'][0])])
    html_df = pd.DataFrame(html_list, columns=['상품_상세정보'])

    df = pd.concat([df, html_df], axis=1)

    # EXCEL 양식 맞춰주기
    columns=['상품상태','카테고리ID','상품명','판매가','재고수량','AS_안내내용','AS_전화번호',
                                '대표_이미지_파일명','추가_이미지_파일명','상품_상세정보','판매자_상품코드','판매자_바코드','제조사','브랜드',
                                '제조일자','유효일자','부가세','미성년자_구매','구매평_노출여부','원산지_코드','수입사','복수원산지_여부',
                                '원산지_직접입력','배송방법','배송비_유형','기본배송비','배송비_결제방식','조건부무료_상품판매가합계','수량별부과_수량',
                                '반품배송비','교환배송비','지역별_차등배송비_정보','별도설치비','판매자_특이사항','즉시할인_값','즉시할인_단위',
                                '복수구매할인_조건_값','복수구매할인_조건_단위','복수구매할인_값','복수구매할인_단위','상품구매시_포인트_지급_값',
                                '상품구매시_포인트_지급_단위','텍스트리뷰_작성시_지급_포인트','포토동영상_리뷰_작성시_지급_포인트','한달사용_텍스트리뷰_작성시_지급_포인트',
                                '한달사용_포토동영상리뷰_작성시_지급_포인트','톡톡친구스토어찜고객_리뷰_작성시_지급_포인트','톡톡친구스토어찜고객_리뷰_작성시_지급_포인트',
                                '무이자_할부_개월','사은품','옵션형태','옵션명','옵션값','옵션가','옵션_재고수량','추가상품명','추가상품값','추가상품가',
                                '추가상품_재고수량','상품정보제공고시_품명','상품정보제공고시_모델명','상품정보제공고시_인증허가사항','상품정보제공고시_제조자',
                                '스토어찜회원_전용여부','문화비_소득공제']
    for i in columns:
        if i not in df.columns:
            if i == '스토어찜회원_전용여부':
                df[i] = "n"
            else:
                df[i] = nan

    # 칼럼 재배치
    df=df[columns]

    # 최종 결과물
    return df


def final(df, location):

    # image folder 저장
    os.makedirs(f"{location}/result")
    for i in range(len(df)):
        imgUrl = df['대표_이미지_파일명'][i]
        imgName = df['상품명'][i]
        with urlopen(imgUrl) as f:
            with open(f"{location}/result/{imgName}.jpg",'wb') as h: # 이미지 + 사진번호 + 확장자는 jpg
                img = f.read() #이미지 읽기
                h.write(img) # 이미지 저장

    # 대표_이미지_파일명 변경
    df['대표_이미지_파일명'] = df['상품명'].copy()

    # file 저장
    save_xlsx = pd.ExcelWriter(f"{location}/result.xlsx")
    df.to_excel(save_xlsx, index = False) # xlsx 파일로 변환
    save_xlsx.save() #xlsx 파일로 저장

# step 5 - HTML 코드 관리부분을 py에서 수정하는 함수(결국 csv 수정하는 느낌으로)
def replace_html(up, html, down):
    html_df = pd.DataFrame([[up, html, down]], columns=['상단이미지','html','하단이미지'])
    html_df.to_csv(resource_path('html.csv'))


# step 6 - A/S 부분 수정하는 함수
def replace_as(number, info, sale, sale_method):
    as_df = pd.DataFrame([[number, info, sale, sale_method]], columns=['A/S 전화번호','A/S 안내내용','판매가 추가','방식'])
    as_df.to_csv(resource_path('as.csv'))

# step 8 - 금지어 수정하는 함수
def replace_ban(ban_list):
    ban_df = pd.DataFrame(ban_list, columns=['금지어'])
    ban_df.to_csv(resource_path('ban.csv'))

# step 7 - 생성된 데이터 프레임에서, 사용자가 원하는 행을 삭제하도록 하는 함수
def remove_row(df, row_list):
    df.drop(row_list,inplace=True)
    df.reset_index(drop=True,inplace=True)

    # 최종 결과물 전달
    return df

# step 8 - 코드 입력 시 맞는지 확인 함수
def code_avail(code):
    code_df = pd.read_csv(resource_path('code.csv'))
    code_list = code_df['code'].tolist()
    if code in code_list:
        return True




# 실행 -----------------------------------------------------------------------------------------------------------------------------------------
# 파라미터 입력
# link = "https://smartstore.naver.com/snkrbuilding"
# link_2 = "https://smartstore.naver.com/shoefairi"
# cate_list = step0(link_2)
# catego = cate_list[0]
# sort_list = ["인기도순", "누적판매순", "낮은가격순", "최신등록순", "리뷰많은순", "평점높은순"]
# sort = "평점높은순"
# count = 20


# # 실험
# # pd.read_csv('.csv', index_col=0)
# code = int(input())
# if code_avail(code) == True:
#     step1_df = step1(link_2, catego, sort, count)
#     step2_df = step2(step1_df)
#     step3_df = step3(step2_df)
#     step4_df = step4(step3_df)
#     final(step4_df)
# else:
#     print("올바른 코드를 입력해주세요.")