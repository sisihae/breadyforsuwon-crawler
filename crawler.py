import time
import warnings
warnings.filterwarnings('ignore')
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup

url = "https://map.kakao.com/"
driver.get(url)

searchloc = '수원 빵집'

search_area = driver.find_element(By.XPATH, r'//*[@id="search.keyword.query"]') # 카카오맵 검색창
search_area.send_keys(searchloc)  # 검색어 전달
driver.find_element(By.XPATH, r'//*[@id="search.keyword.submit"]').send_keys(Keys.ENTER)  # 돋보기 클릭

time.sleep(5)

driver.find_element(By.XPATH, r'//*[@id="info.main.options"]/li[2]/a').send_keys(Keys.ENTER)  # 장소 탭

bakery_list = [] 

def bakeryNamePrint():
    time.sleep(0.2)
    
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    bakery_lists = soup.select('.placelist > .PlaceItem') # 장소 정보를 모두 가져옴
    for i, bakery in enumerate(bakery_lists):
        temp = []
        
        name = bakery.select('.head_item > .tit_name > .link_name')[0].text
        rating = bakery.select('.rating > .score > em')[0].text
        addr = bakery.select('.addr > p')[0].text
        
        # 상세정보 탭으로 이동
        driver.find_element(By.XPATH, r'//*[@id="info.search.place.list"]/li['+str(i+1)+']/div[5]/div[4]/a[1]').send_keys(Keys.ENTER)
        driver.switch_to.window(driver.window_handles[-1])
        time.sleep(2)
        rev = extract_review()  # 리뷰 추출 함수 실행
        
        # 하나의 리스트로 만들어 bakery_list에 추가
        temp.append(name)
        temp.append(rating)
        temp.append(addr[3:])
        temp.append(rev)
        bakery_list.append(temp)


def extract_review():
    html = driver.page_source
    soup = BeautifulSoup(html, 'html.parser')
    
    # 후기 목록 찾기
    review_lists = soup.select('.list_evaluation > li')
    
    count = 0
    rev = []
    # 리뷰가 있는 경우
    if len(review_lists) != 0:
        for review in review_lists:
            comment = review.select('.txt_comment > span')[0].text  # 리뷰
            if len(comment) != 0:
                rev.append(comment)
    # 없으면 빈칸 추가
    else:
        rev.append(' ')
    
    # 다시 검색 탭으로 전환
    driver.close()
    driver.switch_to.window(driver.window_handles[0])
    time.sleep(2)
    
    return rev


page = 1  # 현재 페이지
page2 = 1  # 5개 중 몇번째인지(버튼이 5개씩있어서 6번째가 되면 다시 1로 바꿔줘야함)

for i in range(1, 9):
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
    
    except:
        break
        
print('crawling done')