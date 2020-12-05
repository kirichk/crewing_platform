import requests
import sys
from django.conf import settings
from django.utils import timezone
from web_hiring.models import Post
sys.path.append('..')
import scraper
from crewing.celery import app


START_URL = settings.START_URL
START_PAGE = requests.get(START_URL)


@app.task
def delete_old_files():
    """
    Searching for posts that are not relavent
    (Current date > Joining date)
    """
    Post.objects.filter(joining_date__lte=timezone.datetime.today()).delete()
    print(f"completed deleting foos at {timezone.now()}")
    return f"completed deleting foos at {timezone.now()}"


@app.task
def find_new_posts():
    """
    Searching if there are new posts that should b added to db
    """
    print('Started searching for a new posts')
    vacancies_list = scraper.check_new(START_URL)
    new_vacancies = []
    if vacancies_list is not None:
        for vacancy in vacancies_list:
            if Post.objects.filter(link=vacancy['link']).exists():
                print(vacancy)
            else:
                new_vacancies.append(vacancy)
    if new_vacancies == []:
        print('No updates detected')
    else:
        print(new_vacancies)
        print('Finished')
        print('Started information extraction')
        scraper.info_search(new_vacancies, 'update')


@app.task
def scrape_all():
    print("Started pagination extraction")
    list_of_pages = scraper.pagination(START_PAGE)
    print("Finished")
    print("Started extraction vacancy links from pages")
    vacancies_list = scraper.vacancies_search(list_of_pages)
    print("Finished")
    print("Started information extraction")
    vacancies_information = scraper.info_search(vacancies_list, "base")
