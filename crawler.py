import time
import warnings
warnings.filterwarnings('ignore')
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import csv

driver = webdriver.Chrome()
url = "https://map.kakao.com/"
driver.get(url)

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

        # 상세페이지 링크 추출
        try:
            detail_link_tag = bakery.select_one('.moreview')
            detail_url = detail_link_tag['href']  # e.g., https://place.map.kakao.com/1924550713
            review_url = detail_url + "#comment"
        except:
            print(f"[경고] {name} 상세페이지 링크 추출 실패")
            continue

        # 새 창에서 리뷰 페이지 열기
        driver.execute_script(f"window.open('{review_url}');")
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)

        rev = extract_review()

        temp.append(name)
        temp.append(rating)
        temp.append(addr[3:])
        temp.append(rev)
        bakery_list.append(temp)

        # 리뷰 창 닫고 돌아가기
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        time.sleep(1)


def extract_review():
    time.sleep(2)
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')

    review_lists = soup.select('.list_review > li') 
    rev = []

    if review_lists:
        for review in review_lists:
            comment_tag = review.select_one('.desc_review > p')
            if comment_tag:
                rev.append(comment_tag.text.strip())
    else:
        rev.append(' ')

    return rev



page = 1  # 현재 페이지
page2 = 1  # 5개 중 몇번째인지(버튼이 5개씩있어서 6번째가 되면 다시 1로 바꿔줘야함)

for i in range(1, 2):
    try:
        page2 += 1
        print(page, 'page')
        # 페이지 버튼 번호(1에서 5 사이 값)
        if i > 5:
            xpath = '/html/body/div[5]/div[2]/div[1]/div[7]/div[6]/div/a['+str(i-5)+']'
        else:
            xpath = '/html/body/div[5]/div[2]/div[1]/div[7]/div[6]/div/a['+str(i)+']'
        
        driver.find_element(By.XPATH, xpath).send_keys(Keys.ENTER)  # 페이지 선택
        bakeryNamePrint()  # 장소 정보 크롤링     
        
        # page2가 5를 넘어가면 다시 1로 바꿔주고 다음 버튼 클릭
        if page2 > 5:
            page2 = 1
            driver.find_element(By.XPATH, r'//* [@id="info.search.page.next"]').send_keys(Keys.ENTER)
        
        page += 1
    
    except Exception as e:
        print(f"페이지 {i} 에서 에러 발생: {e}")
        break
        
print('crawling done')

with open('bakery_list.csv', 'w', newline='', encoding='utf-8-sig') as f:
    writer = csv.writer(f)
    writer.writerow(['이름', '평점', '주소', '리뷰'])  
    for row in bakery_list:
        writer.writerow([row[0], row[1], row[2], ' | '.join(row[3])])