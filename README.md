# Naver_smart_Store
네이버 SmartStore에 업로드 된 상품 정보를 수집합니다. 상품 정보들은 상품 등록이 바로 가능한 Excel 파일로 변환됩니다. 
<br><br><br>

## [개발 동기]<br>
Kmong에서 개발 외주를 받아서 만들게 되었다. 의뢰인은 스마트 스토어의 링크와 카테고리를 입력하면 관련된 모든 상품 정보를 담아오길 원했다. 또한 HTML 코드를 작성자가 원하는대로 수정할 수 있길 바랐다.
<br><br><br>

## [개발 결과]<br>
Kmong 후기 <br><br>
![image](https://user-images.githubusercontent.com/58064919/206830872-91ec99da-a005-436c-b115-20649b13d2dc.png)
<br><br><br>


## [크롤링 대상]<br><br>
네이버 스마트스토어
https://sell.smartstore.naver.com/#/home/about
<br><br><br>


## [개발 언어]<br><br>
Python
library: BeautifulSoup, Selenium, pandas, seaborn, matplotlib, folium 
<br><br><br>

## [주의할 점]<br><br>
chromedriver 로 크롤링을 하기에, chromedriver와 사용자가 쓰고 있는 chrome 버전이 일치해야 돌아간다.
<br><br><br>

## [실행 파일 만드는 방법]<br><br>

(1) 초기 실행 파일 만들기 <br><br>
![image](https://user-images.githubusercontent.com/58064919/172084859-d886ede3-65f4-4c13-be16-4113ba8c9638.png)

(2) 마지막 줄에 깨알 icon을 추가해줍니다.<br><br>
![image](https://user-images.githubusercontent.com/58064919/172085287-2acaf6e8-1093-436b-a539-28108ad4c133.png)

(3) 수정된 파일을 다시 exe 파일로 구워주기 <br><br>
![image](https://user-images.githubusercontent.com/58064919/172085366-324dd071-c9f1-4073-a472-73caa7735a8d.png)
<br>
<br><br><br>

## [실행/결과 이미지]<br><br>

(1) 프로그램을 클릭하면 다음과 같은 창이 뜹니다. 의뢰인은 프로그램 도용을 막기 위해, 특정 코드를 입력해야 들어갈 수 있도록 하길 원했습니다.<br><br>
![image](https://user-images.githubusercontent.com/58064919/206830945-022e5c18-0ad3-4626-9f92-4d6f9b839532.png)
<br><br><br>

(2) 프로그램 메인 페이지입니다.<br><br>
![image](https://user-images.githubusercontent.com/58064919/206830989-c9854bab-bddc-4fed-84cf-64cabd8a68fd.png)
<br><br><br>

(3) 프로그램 HTML 편집 페이지입니다.<br><br>
![image](https://user-images.githubusercontent.com/58064919/206831084-18f1fec5-3ecf-4789-b7b6-b63ebdd7e1fc.png)
<br><br><br>
