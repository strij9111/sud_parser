import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import time
from tqdm.auto import tqdm
import warnings
warnings.filterwarnings('ignore')


base_domain = "https://mos-sud.ru"

# Указываем ФИО для поиска дел или оставляем пустым для вывода полного списка
fio = urllib.parse.quote_plus("")

# Указываем номер судебного участка
court_num = '66'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'


def get_url(page_num: int) -> str:
    return f"{base_domain}/{court_num}/cases/civil?formType=shortForm&caseNumber=&participant={fio}&uid=&year=&caseDateFrom=&caseDateTo=&caseFinalDateFrom=&caseFinalDateTo=&caseLegalForceDateFrom=&caseLegalForceDateTo=&category=&judge=&publishingState=&hearingRangeDateFrom=&hearingRangeDateTo=&sessionRoom=&sessionRangeTimeFrom=&sessionRangeTimeTo=&sessionType=&docsDateFrom=&docsDateTo=&documentStatus=&documentType=&page={page_num}"
def parse_list(page_num: int) -> str:
    url = get_url(page_num)

    payload = {}
    headers = {'User-Agent': user_agent}

    # Загружаем страницу с судебными делами, игнорируем SSL
    response = requests.request("GET", url, headers=headers, data=payload, verify=False)
    return response.text

def parse_additional(page_case: str) -> dict:
    case_soup = BeautifulSoup(page_case, 'html.parser')
    data = case_soup.find_all('div', {'class': 'right'})

    case_date = data[4].text.strip()
    courter = data[6].text.strip()
    if courter.find(' - ') > 0:
        courter = data[5].text.strip()

    return {'case_date': case_date, 'courter': courter}


def parse_item(page: str) -> list[dict]:
    result = []

    soup = BeautifulSoup(page, 'html.parser')
    trs = soup.find_all('tr')

    # Просматриваем все тэги TR и находим TD
    for tr in trs:
        td = tr.find_all('td')
        if len(td) == 0:
            continue

        if td[0].find('a') is None:
            continue

        uid = td[0].find('a').text
        link = td[0].find('a', href=True)['href']
        service = td[1].text.strip()
        category = td[3].text.strip()

        result.append({'uid': uid, 'link': link, 'service': service, 'category': category})

    return result

def get_additional(link: str):
    headers = {'User-Agent': user_agent, 'Referer': get_url(page_num=1)}

    # Загружаем страницу с конеретным делом - здесь требуется указать Referer
    response = requests.request("GET", base_domain + link, headers=headers, verify=False)

    return response.text

# Создание csv файла
with open('court_cases.csv', 'w', encoding='utf-8') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['Номер дела', 'дата', 'судья', 'Истец/Ответчик', 'категория'])

    #Загружаем первые 20 страниц
    for page_num in tqdm(range(1, 2)):
        time.sleep(0.3)

        page = parse_list(page_num=page_num)
        items = parse_item(page)

        for item in items:
            page_case = get_additional(item['link'])
            additional = parse_additional(page_case=page_case)

            writer.writerow([item['uid'], additional['case_date'], additional['courter'], item['service'], item['category']])