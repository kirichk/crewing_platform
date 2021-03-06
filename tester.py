import re
import os
import requests
import django
from time import sleep
from bs4 import BeautifulSoup
from django.conf import settings
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "crewing.settings")
django.setup()

from web_hiring.models import Post

URL = 'https://ukrcrewing.com.ua'


def contact_extractor(url):
    soup = BeautifulSoup(requests.get(url).text, "lxml")
    details = soup.find("div", class_="page-content agency-page-content")
    for row in details.find_all("div", class_="colmn"):
        row_content = row.text.split(":")
        if row_content[0] == "Телефон" and len(row_content) > 1:
            return row_content[1]
    return "Информация отсутсвует"


def email_extractor(url):
    soup = BeautifulSoup(requests.get(url).text, "lxml")
    details = soup.find("div", class_="page-content agency-page-content")
    for row in details.find_all("div", class_="colmn"):
        row_content = row.text.split(":")
        if row_content[0] == "Эл.почта" and len(row_content) > 1:
            return row_content[1]
    return "Информация отсутсвует"


def vacancy_extractor():
    all_objects = Post.objects.all()
    counter = 0
    print(f"Количество вакансий - {len(all_objects)}")
    for object in all_objects.iterator():
        sleep(0.5)
        counter += 1
        if counter % 10 == 0:
            print(f"Пройдено {counter} вакансий")
        soup = BeautifulSoup(requests.get(object.link).text, "lxml")
        details = soup.find("div", class_="vacancy-full-content")
        try:
            for row in details.find_all("div", class_="colmn"):
                row_content = row.text.split(":")
                if row_content[0] == "Крюинг":
                    link = row.find("a")
                    email = email_extractor(URL + link['href'])
                    object.email = email
                    print(f"{object.title} - {object.crewer}: {object.email}")
            object.save()
        except AttributeError:
            continue


vacancy_extractor()
