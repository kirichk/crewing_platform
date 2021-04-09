import os
import re
import csv
import string
import django
from datetime import date, datetime, timedelta
from time import sleep

import requests
from bs4 import BeautifulSoup
from loguru import logger

from django.conf import settings
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewing.settings")
django.setup()

from django.utils import timezone

bot = Bot(token=settings.TELE_TOKEN)

USERNAME = 'ukrseamen@stream.com.ua'
PASSWORD = 'ukrseamen828'
ADMIN = '389609639'
# LETTERS = list(string.ascii_uppercase)
LETTERS = ['A']
print(LETTERS)

KEYS = ['Name', 'Certificate', 'Expire date', 'Phone', 'Email']

LOGIN_URL = 'https://ukrcrewing.com.ua/en/login'
CONTACTS_MAIN_PAGE_URL = 'https://ukrcrewing.com.ua/en/seaman/p1/LETTER?on_page=100'

req_headers = {
    'content-type': 'application/x-www-form-urlencoded'
}

formdata = {
    'email': USERNAME,
    'password': PASSWORD,
    'SubmitIt' : 'Log in',
    'from': LOGIN_URL
}


def csv_creator():
    with open('people.csv', 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, KEYS)
        dict_writer.writeheader()


def csv_writer(data):
    with open('people.csv', 'a', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, KEYS)
        dict_writer.writerows(data)


@logger.catch
def pagination(session):
    """
    Searching for urls of all paginators
    """
    pages_list = []
    for letter in LETTERS:
        WEB_PAGE = CONTACTS_MAIN_PAGE_URL.replace("LETTER", letter)
        page = session.get(WEB_PAGE)
        soup = BeautifulSoup(page.text, "lxml")
        text_div = soup.find("div", class_="small").text
        vacancies_count = int(re.findall(r"\d+", text_div)[0])
        if vacancies_count % 100 == 0:
            pages_count = int(vacancies_count / 100)
        else:
            pages_count = int(vacancies_count // 100 + 1)
        for num in range(1, pages_count + 1):
            pages_list.append(WEB_PAGE.replace("p1", f"p{num}"))
        logger.info(f'{len(pages_list)} pages founded')
    return pages_list


@logger.catch
def profiles_search(pages, session):
    """
    Searching for vacancies on each page from the list
    """
    result = []
    for page in pages:
        sleep(1)
        soup = BeautifulSoup(session.get(page).text, "lxml")
        table = soup.find("table", class_="seaman-list-table va-top seaman-list-table-2")
        for rows in table.find_all("tr")[1:]:
            for column in rows.find("td", 'seaman-name-td'):
                try:
                    result.append("https://ukrcrewing.com.ua" + column["href"])
                except TypeError:
                    continue
    logger.info(f'{len(result)} profiles detected')
    return result


@logger.catch
def duplicates_checker(source, new):
    """
    Checking for duplicates in existing list of contacts
    """
    for item in source:
        if new == item['phone']:
            return False
    return True


@logger.catch
def info_search(profiles, session):
    """
    Scraping all the information from collected contacts pages
    """
    csv_creator()
    counter = 0
    results = []
    for profile in profiles:
        info = {}
        sleep(0.5)
        soup = BeautifulSoup(session.get(profile).text, "lxml")
        soup.find_all("a", string="Elsie")
        details = soup.find("div", class_="page-content seaman-page-content")
        info['Name'] = details.h1.text
        for item in details.find_all("tr"):
            if "basic safety" in str(item).lower():
                data = [x.text for x in item.find_all_next('td')]
                cleaned_date = datetime.strptime(data[3], '%d.%m.%Y')
                if datetime.now() + timedelta(days=200) > cleaned_date:
                    info['Certificate'] = data[0]
                    info['Expire date'] = data[3]
                    for row in details.find_all("div", class_="colmn3"):
                        row_content = row.text.split(":")
                        if row_content[0] == "Personal mobile number":
                            info['Phone'] = row_content[1]
                        if row_content[0] == "E-Mail":
                            info['Email'] = row_content[1]
                    results.append(info)
                    csv_writer([info])
                    f = open('people.csv','rb')
                    bot.send_document(chat_id=ADMIN, document=f, filename='people.csv')
                    if len(results) % 100 == 0:
                        f = open('people.csv','rb')
                        bot.send_document(chat_id=ADMIN, document=f, filename='people.csv')
                    logger.info(f'{len(results)} profiles added\n{info}')
        counter += 1
        if counter % 10 == 0:
            logger.info(f'Processed {counter} profiles out of {len(profiles)} profiles')
    logger.info(f'Finished adding {len(profiles)} profiles')
    return results


@logger.catch
def scraping_funnel():
    with requests.Session() as session:
            # Authenticate
        login = session.post(LOGIN_URL, data=formdata,
                        headers=req_headers, allow_redirects=False)
        if login.status_code == 302:
            pages = pagination(session)
            profiles = profiles_search(pages, session)
            contact_info = info_search(profiles, session)
        else:
            print('Authentication error')


if __name__ == '__main__':
    scraping_funnel()
