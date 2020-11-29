import re
from django.conf import settings
from telegram import Bot
from tgbot.models import Profile


bot = Bot(token=settings.TELE_TOKEN)


def vacancy_notification(form):
    """
    Receiving a dictionary with data of new posted vacancy
    Applying filtering to send notification to relevant users
    """
    for p in Profile.objects.all():
        if form['title'] in p.title_subscriptions or 'Все' in p.title_subscriptions:
            salaries = p.salary_range
            cleaned_salary = re.findall(r'[0-9]+', form['salary'])[0]
            # if highlighted salary in vacancy is higher than user expactations
            if int(salaries) <= int(cleaned_salary):
                # Adding to notiication non-empty rows
                main_text = f'{form["title"]}\n'\
                            f'Флот: {form["fleet"]}\n'\
                            f'Тип судна: {form["vessel"]}\n'\
                            f'Зарплата: {form["salary"]}\n'\
                            f'Уровень английского: {form["english"]}\n'\
                            f'Дата посадки: {str(form["joining_date"])}\n'
                if form['voyage_duration'] is not None and form['voyage_duration'] != '':
                    main_text += f'Длительность рейса: {str(form["voyage_duration"])}\n'
                if form['sailing_area'] is not None and form['sailing_area'] != '':
                    main_text += f'Регион работы: {str(form["sailing_area"])}\n'
                if form['dwt'] is not None and form['dwt'] != '':
                    main_text += f'DWT: {str(form["dwt"])}\n'
                if form['years_constructed'] is not None and form['years_constructed'] != '':
                    main_text += f'Год постройки судна: {str(form["years_constructed"])}\n'
                if form['crew'] is not None and form['crew'] != '':
                    main_text += f'Экипаж: {str(form["crew"])}\n'
                if form['crewer'] is not None and form['crewer'] != '':
                    main_text += f'Крюинг: {str(form["crewer"])}\n'
                if form['text'] != '':
                    main_text += f'Дополнительная информация: {str(form["text"])}\n'
                bot.send_message(p.external_id,main_text)
