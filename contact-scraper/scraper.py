import os
import re
from time import sleep

import requests
import vobject
from bs4 import BeautifulSoup
from loguru import logger

# import django
# from django.conf import settings
#
#
# os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewing.settings")
# django.setup()

# LOGIN_URL = settings.LOGIN_URL
# CONTACTS_MAIN_PAGE_URL = settings.CONTACTS_MAIN_PAGE_URL

logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="1 MB",
    compression="zip",
)

LOGIN_URL = 'https://ukrcrewing.com.ua/en/login'
CONTACTS_MAIN_PAGE_URL = 'https://ukrcrewing.com.ua/en/seaman/p1/B?on_page=100'

USERNAME = '' # put correct usename here
PASSWORD = '' # put correct password here

req_headers = {
    'content-type': 'application/x-www-form-urlencoded'
}

formdata = {
    'email': USERNAME,
    'password': PASSWORD,
    'SubmitIt' : 'Log in',
    'from': LOGIN_URL
}


@logger.catch
def vcard_handler(person: dict):
    """
    Converting contact info to vcard
    """
    contact = {'n': person['name'],
              'fn': person['name'],
              'tel': person['phone'],
              'email': person['email']}

    vcard = vobject.readOne('\n'.join([f'{k}:{v}' for k, v in contact.items()]))
    vcard.name = 'VCARD'
    vcard.useBegin = True

    with open('testB.vcf', 'a', newline='') as f:
        f.write(vcard.serialize())


@logger.catch
def pagination(page):
    """
    Searching for urls of all paginators
    """
    soup = BeautifulSoup(page.text, "lxml")
    pages_list = []
    text_div = soup.find("div", class_="small").text
    vacancies_count = int(re.findall(r"\d+", text_div)[0])
    if vacancies_count % 100 == 0:
        pages_count = vacancies_count / 100
    else:
        pages_count = vacancies_count // 100 + 1
    for num in range(1, pages_count + 1):
        pages_list.append(CONTACTS_MAIN_PAGE_URL.replace("p1", f"p{num}"))
    logger.info(f'{len(pages_list)} pages founded')
    return pages_list


@logger.catch
def profiles_search(pages: list, session: requests.Session):
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
def duplicates_checker(source: list, new: str):
    """
    Checking for duplicates in existing list of contacts
    """
    for item in source:
        if new == item['phone']:
            return False
    return True


@logger.catch
def info_search(profiles: list, session: requests.Session):
    """
    Scraping all the information from collected contacts pages
    """
    counter = 0
    results = []
    for profile in profiles:
        info = {}
        sleep(0.5)
        soup = BeautifulSoup(session.get(profile).text, "lxml")
        details = soup.find("div", class_="page-content seaman-page-content")
        info['name'] = details.h1.text
        try:
            for row in details.find_all("div", class_="colmn3"):
                row_content = row.text.split(":")
                if row_content[0] == "Contact number":
                    info['phone'] = row_content[1]
                if row_content[0] == "E-Mail":
                    info['email'] = row_content[1]
            if 'phone' in info and duplicates_checker(results, info['phone']):
                results.append(info)
                vcard_handler(info)
        except AttributeError:
            continue
        if len(results) % 10 == 0:
            counter += 10
            logger.info(f'{counter} profiles added out of {len(profiles)}')
    logger.info(f'Finished adding {len(profiles)} profiles')
    return results


@logger.catch
def scraping_funnel():
    with requests.Session() as session:
            # Authenticate
        login = session.post(LOGIN_URL, data=formdata,
                        headers=req_headers, allow_redirects=False)
        if login.status_code == 302:
            pages = pagination(session.get(CONTACTS_MAIN_PAGE_URL))
            profiles = profiles_search(pages, session)
            contact_info = info_search(profiles, session)
        else:
            print('Authentication error')


if __name__ == '__main__':
    scraping_funnel()
