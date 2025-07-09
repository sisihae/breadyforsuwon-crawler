import time
import warnings
warnings.filterwarnings('ignore')
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv
import re

driver = webdriver.Chrome()
url = "https://map.kakao.com/"
driver.get(url)
time.sleep(15)

searchloc = '수원 빵집'

search_area = driver.find_element(By.XPATH, r'//*[@id="search.keyword.query"]') # 카카오맵 검색창
search_area.send_keys(searchloc)  # 검색어 전달
driver.find_element(By.XPATH, r'//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)  # 돋보기 클릭

time.sleep(2)

driver.find_element(By.XPATH, r'//*[@id="info.main.options"]/li[2]/a').send_keys(Keys.ENTER)  # 장소 탭

time.sleep(5)

bakery_list = [] 

def bakeryNamePrint():
    time.sleep(2)

    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    bakery_items = soup.select('.placelist > .PlaceItem')

    for i, bakery in enumerate(bakery_items):
        temp = []

        name = bakery.select_one('.head_item > .tit_name > .link_name').text.strip()
        rating = bakery.select_one('.rating > .score > em').text.strip()
        addr = bakery.select_one('.addr > p').text.strip()

         # 상세정보 탭으로 이동
        driver.find_element(By.XPATH, r'//*[@id="info.search.place.list"]/li['+str(i+1)+']/div[5]/div[4]/a[1]').send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        url = driver.current_url
        match = re.search(r"/(\d+)$", url)
        if match:
            id = match.group(1)

        # driver.get(url + "#comment")
        # comments = extract_comment()
        driver.get(url + "#review")
        aisummary = extract_aisummary()

        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(2)

        temp.append(name)
        temp.append(id)
        temp.append(rating)
        temp.append(addr[3:])
        temp.append(aisummary)
        bakery_list.append(temp)


def extract_aisummary():
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    summary = soup.select('.info_review > .option_review') 
    pairs = []

    for line in summary:
        category = line.find('em', class_='emph_txt').text.strip()
        value = line.find_all('span')[-1].text.strip()
        pairs.append(f"{category}: {value}")

    result = " / ".join(pairs)
    return result


for i in range(1, 35):
    try:
        print('page', i)
        # 페이지 버튼 번호(1에서 5 사이 값)
        page = i%5 if i%5 else 5
        if page > 1:
            xpath = '/html/body/div[5]/div[2]/div[1]/div[7]/div[6]/div/a['+str(page)+']'
            driver.find_element(By.XPATH, xpath).send_keys(Keys.ENTER)  # 페이지 선택
        bakeryNamePrint()  # 장소 정보 크롤링     

        # page2가 5를 넘어가면 다시 1로 바꿔주고 다음 버튼 클릭
        if page == 5:
            driver.find_element(By.XPATH, r'//* [@id="info.search.page.next"]').send_keys(Keys.ENTER)
            
    except Exception as e:
        print(f"페이지 {i} 에서 에러 발생: {e}")
        break
        
print('crawling done')

with open('bakery_list2.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['name', 'id', 'rating', 'address', 'aisummary'])  
    for row in bakery_list:
        writer.writerow([row[0], row[1], row[2], row[3], row[4]])