import os
import re
from time import sleep

import django
import requests
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone
from loguru import logger

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewing.settings")
django.setup()

from web_hiring.models import Post
from web_hiring.notificators import vacancy_notification


proxies = {
    "https": "https://0YkwQu:Vnpw9b@181.177.84.94:9441"
}


logger.add(
    "logs/info.log",
    format="{time} {level} {message}",
    level="INFO",
    rotation="1 MB",
    compression="zip",
)

START_URL = settings.START_URL
START_PAGE = requests.get(START_URL, proxies=proxies)


def try_connection(url):
    page = ''
    while page == '':
        try:
            page = requests.get(url, proxies=proxies)
            break
        except:
            print("Connection refused by the server..")
            print("Let me sleep for 5 seconds")
            print("ZZzzzz...")
            sleep(5)
            print("Was a nice sleep, now let me continue...")
            continue
    return page

@logger.catch
def contact_extractor(url):
    page = try_connection(url)
    soup = BeautifulSoup(page.text, "lxml")
    details = soup.find("div", class_="page-content agency-page-content")
    for row in details.find_all("div", class_="colmn"):
        row_content = row.text.split(":")
        if row_content[0] == "Телефон" and len(row_content) > 1:
            return row_content[1]
    return "Информация отсутсвует"


@logger.catch
def email_extractor(url):
    page = try_connection(url)
    soup = BeautifulSoup(page.text, "lxml")
    details = soup.find("div", class_="page-content agency-page-content")
    for row in details.find_all("div", class_="colmn"):
        row_content = row.text.split(":")
        if row_content[0] == "Эл.почта" and len(row_content) > 1:
            return row_content[1]
    return "Информация отсутсвует"



@logger.catch
def pagination(page):
    """
    Searching for urls of all paginators
    """
    soup = BeautifulSoup(page.text, "lxml")
    pages_list = []
    text_div = soup.find("div", class_="small").text
    vacancies_count = int(re.findall(r"\d+", text_div)[0])
    if vacancies_count % 30 == 0:
        pages_count = vacancies_count / 30
    else:
        pages_count = vacancies_count // 30 + 1
    for num in range(1, pages_count + 1):
        pages_list.append(START_URL.replace("p1", f"p{num}"))
    return pages_list


@logger.catch
def vacancies_search(pages: list):
    """
    Searching for vacancies on each page from the list
    """
    result = []
    for page in pages:
        raw_page = try_connection(page)
        soup = BeautifulSoup(raw_page.text, "lxml")
        table = soup.find("table", class_="nwrap")
        page_dict = []
        for rows in table.find_all("tr")[1:]:
            columns = [
                "Position",
                "Vessel type",
                "Voyage duration",
                "Salary",
                "Joining date",
                "Vacancy posted",
            ]
            info = []
            for column in rows.find_all("td"):
                try:
                    info.append(column.a["href"])
                    info.append(column.text)
                except TypeError:
                    info.append(column.text)
            final = {"link": "https://ukrcrewing.com.ua" + info[0]}
            final.update(dict(zip(columns, info[1:])))
            page_dict.append(final)
        result.extend(page_dict)
    return result


@logger.catch
def check_new(url):
    """
    Checking first page if there are new vacancies that should be added
    """
    result = []
    page = try_connection(url)
    soup = BeautifulSoup(page.text, "lxml")
    table = soup.find("table", class_="nwrap")
    page_dict = []
    try:
        for rows in table.find_all("tr")[1:]:
            columns = [
                "Position",
                "Vessel type",
                "Voyage duration",
                "Salary",
                "Joining date",
                "Vacancy posted",
            ]
            info = []
            for column in rows.find_all("td"):
                if link_match_check(column):
                    result.extend(page_dict)
                    return result
                try:
                    info.append(column.a["href"])
                    info.append(column.text)
                except TypeError:
                    info.append(column.text)
            final = {"link": "https://ukrcrewing.com.ua" + info[0]}
            final.update(dict(zip(columns, info[1:])))
            print(final)
            page_dict.append(final)
        result.extend(page_dict)
    except AttributeError:
        print('Error occured')
    finally:
        return result


@logger.catch
def link_match_check(row):
    """
    Indicating that link is already in database
    """
    all_objects = Post.objects.all()
    try:
        row_link = row.a["href"]
        for object_founded in all_objects:
            return row_link == object_founded.link
    except TypeError:
        return False


@logger.catch
def info_search(vacancies: dict, mode: str):
    """
    Scraping all the information from collected vacancies pages
    """
    sailing_area = dwt = crew = english = crewer = contact = ""
    years_constructed = None

    for vacancy in vacancies:
        sleep(0.5)
        page = try_connection(vacancy["link"])
        soup = BeautifulSoup(page.text, "lxml")
        details = soup.find("div", class_="vacancy-full-content")
        try:
            for row in details.find_all("div", class_="colmn"):
                row_content = row.text.split(":")
                if row_content[0] == "Регион работы":
                    sailing_area = row_content[1]
                if row_content[0] == "DWT":
                    dwt = row_content[1]
                if row_content[0] == "Год постройки судна":
                    years_constructed = int(row_content[1])
                if row_content[0] == "Экипаж":
                    crew = row_content[1]
                if row_content[0] == "Уровень английского":
                    english = row_content[1]
                if row_content[0] == "Крюинг":
                    crewer = row_content[1]
                    link = row.find("a")
                    contact = contact_extractor("https://ukrcrewing.com.ua"
                                                + link['href'])
                    email = email_extractor("https://ukrcrewing.com.ua"
                                                + link['href'])
            for div in details.find_all("div"):
                div.decompose()
            for header in details.find_all("h1"):
                header.decompose()
            for whitespace in details.find_all("br"):
                whitespace.replace_with("\n")
            other_info = re.sub(r"\n+", "\n", details.text).strip()
            additional_info = other_info.replace(
                                    "Дополнительная информация:\n", ""
                                    )
            updated_date = (
                "20"
                + vacancy["Joining date"][6:]
                + "-"
                + vacancy["Joining date"][3:5]
                + "-"
                + vacancy["Joining date"][:2]
            )
            new_post = Post.objects.get_or_create(
                title=vacancy["Position"],
                fleet="",
                vessel=vacancy["Vessel type"],
                salary=vacancy["Salary"],
                joining_date=updated_date,
                voyage_duration=vacancy["Voyage duration"],
                sailing_area=sailing_area,
                dwt=dwt,
                years_constructed=years_constructed,
                crew=crew,
                crewer=crewer,
                contact=contact,
                email=email,
                english=english,
                link=vacancy["link"],
                text=additional_info,
                publish_date=timezone.now(),
            )[0]
            new_post.save()
            if mode == "update":
                vacancy_form = {
                    "title": vacancy["Position"],
                    "fleet": "",
                    "vessel": vacancy["Vessel type"],
                    "salary": vacancy["Salary"],
                    "joining_date": updated_date,
                    "voyage_duration": vacancy["Voyage duration"],
                    "sailing_area": sailing_area,
                    "dwt": dwt,
                    "years_constructed": years_constructed,
                    "crew": crew,
                    "crewer": crewer,
                    "contact": contact,
                    "email": email,
                    "english": english,
                    "text": additional_info,
                }
                vacancy_notification(vacancy_form)
            sailing_area = ""
            dwt = ""
            years_constructed = None
            crew = ""
            english = ""
            contact = ""
            email = ""
        except AttributeError:
            continue


if __name__ == "__main__":
    print("Started pagination extraction")
    list_of_pages = pagination(START_PAGE)
    print("Finished")
    print("Started extraction vacancy links from pages")
    vacancies_list = vacancies_search(list_of_pages)
    print("Finished")
    print("Started information extraction")
    vacancies_information = info_search(vacancies_list, "base")
    # START_URL = 'https://ukrcrewing.com.ua/vacancy/p1?v_sort=1&v_sort_dir=1'
    # vacancies_list = check_new(START_URL)
    # info_search(vacancies_list, 'parsing')
