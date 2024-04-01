import requests
from bs4 import BeautifulSoup
import re
from dateutil.parser import parse
import datetime

# 각 리스트에서 요일과 날짜를 추출하는 정규표현식
weekday_regex = re.compile(r'[월화수목금토일]')
date_regex = re.compile(r'\d{,4}[-|.|/]{0,1}\d{,2}[-|.|/]\d{,2}')

class SchoolCafeteriaAutoScraper(object):
    def __init__(self, stack_list=None):
        self.stack_list = stack_list or [] # 설정된 스택 리스트
    
    def _fetch_html(self, url):
        res = requests.get(url)
        html = res.text
        return html
    
    def _get_soup(self, url=None, html=None):
        html = self._fetch_html(url)
        return BeautifulSoup(html, "html.parser")
    
    # 요일과 날짜를 구분하여 리스트를 통일시키는 함수
    def _unify_lists(self, item):
        # 요일과 날짜 추출
        date, weekday = None, None
        weekday_match = weekday_regex.search(item)
        date_match = date_regex.search(item)
        if weekday_match:
          weekday = weekday_match.group()
        if date_match:
          date = date_match.group()
          non_digit_pattern = re.compile(r'\D')
          non_digit_chars = non_digit_pattern.findall(date)
          if len(non_digit_chars) == 1:
            non_digit = non_digit_chars[0]
            date = f"{datetime.datetime.now().year}{non_digit}{date}"
          date = parse(date)
        return date, weekday
    
    # 날짜 값 스크래핑
    def _get_date(self, soup):
      result_list = []
      thead_element = soup.find('thead')
      thead_tr_element = thead_element.find('tr')
      thead_th_elements = thead_tr_element.find_all('th')
      for th_element in thead_th_elements:
          date, weekday = self._unify_lists(th_element.text)
          if date and weekday:
            result_list.append(f"{date}({weekday})")
      return result_list

    # 시간대 별 메뉴 값 스크래핑
    def _get_menu(self, soup):
      result_list = []
      tbody_element = soup.find('tbody')
      tbody_tr_elements = tbody_element.find_all('tr')
      for tr_element in tbody_tr_elements:
        td_elements = tr_element.find_all('td')
        for td_element in td_elements:
          menu_list = td_element.get_text(separator='<br>').split('<br>')
          cleaned_menu = [menu.strip() for menu in menu_list if menu.strip()]
          # 빈 리스트가 아닌 경우에만 추가
          if cleaned_menu:
            result_list.append(cleaned_menu)
          
      return result_list
        

    def build(self, url=None, html=None):
        soup = self._get_soup(url=url, html=html)

        result_list = []
        # 날짜 값 파싱
        day_list = self._get_date(soup) # 날짜 리스트

        # 메뉴 값 파싱
        week_menu_list = [[] for _ in range(len(day_list))] # 요일별 메뉴 리스트
        test = self._get_menu(soup)
        print(test)
        #time_list = [[] for _ in range(len(tbody_element))] # 시간대 리스트
        

if __name__ == "__main__":
    scraper = SchoolCafeteriaAutoScraper()
    # urls = ['https://www.gnu.ac.kr/main/ad/fm/foodmenu/selectFoodMenuView.do?restSeq=6&mi=1342&schSysId=cdorm',
    #        'https://www.pusan.ac.kr/kor/CMS/MenuMgr/menuListOnBuilding.do?mCode=MN202#childTab_tmp',
    #        'https://www.cbnucoop.com/service/restaurant/']
    urls = ['https://www.cbnucoop.com/service/restaurant']
    for url in urls:
      scraper.build(url=url)