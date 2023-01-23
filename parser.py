import requests
from bs4 import BeautifulSoup
import csv
import urllib.parse
import time


base_domain = "https://mos-sud.ru"

# Указываем ФИО для поиска дел или оставляем пустым для вывода полного списка
fio = urllib.parse.quote_plus("")

# Указываем номер судебного участка
court_num = '66'
user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'

# Создание csv файла
with open('services.csv', 'w') as csvfile:
    writer = csv.writer(csvfile, delimiter=';')
    writer.writerow(['Номер дела', 'дата', 'судья', 'Истец/Ответчик', 'категория'])

    for page in range(1, 20):
        time.sleep(0.3)
        url = f"{base_domain}/{court_num}/cases/civil?formType=shortForm&caseNumber=&participant={fio}&uid=&year=&caseDateFrom=&caseDateTo=&caseFinalDateFrom=&caseFinalDateTo=&caseLegalForceDateFrom=&caseLegalForceDateTo=&category=&judge=&publishingState=&hearingRangeDateFrom=&hearingRangeDateTo=&sessionRoom=&sessionRangeTimeFrom=&sessionRangeTimeTo=&sessionType=&docsDateFrom=&docsDateTo=&documentStatus=&documentType=&page={page}"

        payload = {}
        headers = {'User-Agent': user_agent}

        # Загружаем страницу с судебными делами
        response = requests.request("GET", url, headers=headers, data=payload, verify=False)
        page = response.text

        soup = BeautifulSoup(page, 'html.parser')
        trs = soup.find_all('tr')

        #Просматриваем все тэги TR и находим TD
        for tr in trs:
            td = tr.find_all('td')
            if len(td) == 0:
                continue

            if td[0].find('a') is None:
                continue

            uid = td[0].find('a').text
            link = td[0].find('a', href=True)['href']

            headers = {'User-Agent': user_agent, 'Referer': url}

            # Загружаем страницу с конеретным делом - здесь требуется указать Referer
            response = requests.request("GET", base_domain + link, headers=headers, data=payload, verify=False)
            page_case = response.text

            case_soup = BeautifulSoup(page_case, 'html.parser')
            data = case_soup.find_all('div', {'class': 'right'})

            case_date = data[4].text.strip()
            courter = data[6].text.strip()
            if courter.find(' - ') > 0:
                courter = data[5].text.strip()

            service = td[1].text.strip()
            category = td[3].text.strip()
            writer.writerow([uid, case_date, courter, service, category])