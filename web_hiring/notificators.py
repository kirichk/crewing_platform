import re
from django.conf import settings
from telegram import Bot
from datetime import datetime
from tgbot.models import Profile


bot = Bot(token=settings.TELE_TOKEN)
CHANNEL_ID = settings.CHANNEL_ID


def vacancy_notification(form):
    """
    Receiving a dictionary with data of new posted vacancy
    Applying filtering to send notification to relevant users
    """
    title = '#' + form["title"].replace(' ', '_').replace(',', '').replace('.', '',).replace('(','').replace(')', '').replace('-', '_')
    main_text = f'{title}\n'\
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
    if form['contact'] is not None and form['contact'] != '':
        main_text += f'Контактная информация: {str(form["contact"])}\n'
    if form['text'] != '':
        main_text += f'Дополнительная информация: {str(form["text"])}\n'
    for p in Profile.objects.filter(subscription=True):
        if (form['title'] in p.title_subscriptions
            or 'Пропустить' in p.title_subscriptions
            or '' == p.title_subscriptions):
            if p.date_ready is not None and p.date_ready != '':
                d = datetime.strptime(p.date_ready, '%Y-%m-%d')
            else:
                d = form["joining_date"]
            if form["joining_date"] >= d:
                if p.salary_subscription == '' or p.salary_subscription == 'Не важно' or p.salary_subscription is None:
                    cleaned_sub_salary = 0
                else:
                    cleaned_sub_salary = int(re.findall(r'[0-9]+',
                                                p.salary_subscription.split('-')[0])[0])
                cleaned_salary = int(re.findall(r'[0-9]+', form['salary'])[0])
                if p.contract_subscription == '' or p.contract_subscription == 'Не важно' or p.contract_subscription is None:
                    cleaned_sub_contract = 0
                else:
                    cleaned_sub_contract = int(re.findall(r'[0-9]+', p.contract_subscription)[0])
                if form['voyage_duration'] is None or form['voyage_duration'] == '':
                    cleaned_contract = 6
                else:
                    cleaned_contract = int(re.findall(r'[0-9]+', form['voyage_duration'])[0])
                if cleaned_salary >= cleaned_sub_salary:
                    if cleaned_contract >= cleaned_sub_contract:
                        bot.send_message(p.external_id,main_text)
    bot.send_message(CHANNEL_ID, main_text)
