import re
from django.conf import settings
from telegram import Bot, InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime
from tgbot.models import Profile


bot = Bot(token=settings.TELE_TOKEN)
CHANNEL_ID_HIGH_LEVEL = settings.CHANNEL_ID_HIGH_LEVEL
CHANNEL_ID_LOW_LEVEL = settings.CHANNEL_ID_LOW_LEVEL
CHANNEL_ID_MAIN = settings.CHANNEL_ID_MAIN
HIGH_LEVEL_SQUAD = settings.HIGH_LEVEL_SQUAD


def vacancy_notification(form):
    """
    Receiving a dictionary with data of new posted vacancy
    Applying filtering to send notification to relevant users
    """
    title = '#' + form["title"].replace(' ', '_').replace(',', '').replace(
        '.', '',).replace('(', '').replace(')', '').replace('-', '_')
    try:
        date = datetime.strptime(form["joining_date"], '%Y-%m-%d')
        date_formatted = date.strftime("%d %B, %Y")
    except:
        date_formatted = form["joining_date"].strftime("%d %B, %Y")
    main_text = f'{form["title"]}\n'\
                f'Тип судна: {form["vessel"]}\n'\
                f'Зарплата: {form["salary"]}\n'\
                f'Уровень английского: {form["english"]}\n'\
                f'Дата посадки: {date_formatted}\n'
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
    if form['email'] is not None and form['email'] != '':
        main_text += f'E-mail: {str(form["email"])}\n'
    if form['text'] != '':
        main_text += f'Дополнительная информация: {str(form["text"])}\n'
    for p in Profile.objects.filter(subscription=True):
        if (p.title_subscriptions is None or form['title'] in p.title_subscriptions
            or 'Пропустить' in p.title_subscriptions
                or '' == p.title_subscriptions):
            new_date = datetime.strptime(form["joining_date"], '%Y-%m-%d')
            cleaned_date = datetime.combine(new_date, datetime.min.time())
            if p.date_ready is not None and p.date_ready != '':
                d = datetime.strptime(p.date_ready, '%Y-%m-%d')
            else:
                d = cleaned_date
            if cleaned_date >= d:
                if p.salary_subscription == '' or p.salary_subscription == 'Не важно' or p.salary_subscription is None:
                    cleaned_sub_salary = 0
                else:
                    cleaned_sub_salary = int(re.findall(r'[0-9]+',
                                                        p.salary_subscription.split('-')[0])[0])
                cleaned_salary = int(re.findall(r'[0-9]+', form['salary'])[0])
                if p.contract_subscription == '' or p.contract_subscription == 'Не важно' or p.contract_subscription is None:
                    cleaned_sub_contract = 12
                else:
                    cleaned_sub_contract = int(re.findall(
                        r'[0-9]+', p.contract_subscription)[0])
                if form['voyage_duration'] is None or form['voyage_duration'] == '':
                    cleaned_contract = 6
                else:
                    cleaned_contract = int(re.findall(
                        r'[0-9]+', form['voyage_duration'])[0])
                if cleaned_salary >= cleaned_sub_salary:
                    if cleaned_contract <= cleaned_sub_contract:
                        try:
                            bot.send_message(p.external_id, main_text)
                        except:
                            pass
    main_text = main_text.replace(form['title'], title)
    bot.send_message(chat_id=CHANNEL_ID_MAIN,
                     text=main_text)
    if form["title"] in HIGH_LEVEL_SQUAD:
        bot.send_message(chat_id=CHANNEL_ID_HIGH_LEVEL,
                         text=main_text)
    else:
        bot.send_message(chat_id=CHANNEL_ID_LOW_LEVEL,
                         text=main_text)
