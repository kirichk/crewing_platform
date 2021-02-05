import os
import re
from datetime import date, datetime, timedelta
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                        ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (CallbackContext, CallbackQueryHandler, Updater,
                        MessageHandler, CommandHandler, ConversationHandler,
                        Filters)
from telegram.utils.request import Request
from telegram_bot_pagination import InlineKeyboardPaginator
from django.conf import settings
from django.forms.models import model_to_dict
from crewing.settings import SALARY_MATCHES
from .models import Profile
from web_hiring.models import Post
from tgbot.tools.calendar import telegramcalendar
from loguru import logger


logger.add('info.log', format='{time} {level} {message}',
            level='INFO', rotation="1 MB", compression='zip')
# PHONE, SALARY_RANGE = range(2)
PAGE_SPLIT = 8
CURRENT_PAGE = 0
CALENDAR, CALENDAR_SELECTOR, EDIT, FILTER, EMAIL_CONFIRM = range(5)
# FILTER_TITLE = FILTER_FLEET = FILTER_SALARY = FILTER_CONTRACT = FILTER_CREW = FILTER_DATE = NEXT_STAGE_CALLBACK = CURRENT_STAGE = ''

@logger.catch
def model_transcriptor(model):
    '''
    Transcripting Django queryset to list of vacancies with only fields
    that needed for a preview
    '''
    result = []
    for item in model:
        result.append(
            {
                'id':item.id,
                'title':item.title,
                'salary':item.salary,
                'voyage_duration':item.voyage_duration,
                'crew':item.crew,
                'joining_date':item.joining_date.strftime('%d.%m.%Y')
            }
        )
    return result


def model_text_details(post):
    try:
        date = datetime.strptime(post.joining_date, '%Y-%m-%d')
        date_formatted = date.strftime("%d %B, %Y")
    except:
        date_formatted = post.joining_date.strftime("%d %B, %Y")
    main_text = f'{post.title}\n'\
                f'Тип судна: {post.vessel}\n'\
                f'Зарплата: {post.salary}\n'\
                f'Уровень английского: {post.english}\n'\
                f'Дата посадки: {date_formatted}\n'
    if post.voyage_duration is not None and post.voyage_duration != '':
        main_text += f'Длительность рейса: {str(post.voyage_duration)}\n'
    if post.sailing_area is not None and post.sailing_area != '':
        main_text += f'Регион работы: {str(post.sailing_area)}\n'
    if post.dwt is not None and post.dwt != '':
        main_text += f'DWT: {str(post.dwt)}\n'
    if post.years_constructed is not None and post.years_constructed != '':
        main_text += f'Год постройки судна: {str(post.years_constructed)}\n'
    if post.crew is not None and post.crew != '':
        main_text += f'Экипаж: {str(post.crew)}\n'
    if post.crewer is not None and post.crewer != '':
        main_text += f'Крюинг: {str(post.crewer)}\n'
    if post.contact is not None and post.contact != '':
        main_text += f'Контактная информация: {str(post.contact)}\n'
    if post.text != '':
        main_text += f'Дополнительная информация: {str(post.text)}\n'
    return main_text


@logger.catch
def subsription_cleaner(text):
    '''
    Checking if subscription start correctly
    '''
    if text.startswith(',') or text.endswith(', '):
        text = text.replace(', ', '')
    else:
        text = text.replace(', ,', ',')
    return text


@logger.catch
def page_definer(posts):
    '''
    Receiving a list of posts and defining what amount of pages will contain them
    '''
    if len(posts) % PAGE_SPLIT == 0:
        return int(len(posts) / PAGE_SPLIT)
    else:
        return int(len(posts) // PAGE_SPLIT + 1)
    print(len(posts))


@logger.catch
def show_item_list(update, data, callback, callback_specific):
    '''
    Receiving a list of posts and defining what amount of pages will contain them
    '''
    if data[-1][0] == 'Другое':
        list_even = data[1:-1:2]
        list_non_even = data[2:-2:2]
    else:
        list_even = data[1::2]
        list_non_even = data[2:-1:2]
    list_non_even.append(('Пропустить','Выбраны все варианты'))
    if callback == 'fleet':
        inline_keyboard=[
                [
                InlineKeyboardButton(
                    text=i[0],
                    callback_data=f'choice{callback}_{callback_specific}_' + i[1]),
                InlineKeyboardButton(
                    text=list_non_even[list_even.index(i)][0],
                    callback_data=f'choice{callback}_{callback_specific}_' \
                                    + list_non_even[list_even.index(i)][1])
                ] for i in list_even]
        inline_keyboard.append(
                [
                 InlineKeyboardButton(
                     text='Вернуться',
                     callback_data=f'{callback}_{callback_specific}_'),
                ])
        inline_buttons = InlineKeyboardMarkup(inline_keyboard)
    else:
        inline_buttons = InlineKeyboardMarkup(
                inline_keyboard=[
                [
                InlineKeyboardButton(
                    text=i[0],
                    callback_data=f'choice{callback}_{callback_specific}_' + i[1]),
                InlineKeyboardButton(
                    text=list_non_even[list_even.index(i)][0],
                    callback_data=f'choice{callback}_{callback_specific}_' \
                                    + list_non_even[list_even.index(i)][1])
                ] for i in list_even
            ],
        )
    update.callback_query.edit_message_text(
        text='Выберите интересующий Вас вариант.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def item_selection_handler(update, data, callback_data, callback_next, text):
    callback = update.callback_query.data.split('_')
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить',
                                    callback_data=f'{callback_data}_add_'),
                InlineKeyboardButton(text='Удалить',
                                    callback_data=f'{callback_data}_remove_')
            ],
            [
                InlineKeyboardButton(text=f'Подтвердить',
                                    callback_data=f'{callback_next}'),
            ]
        ],
    )
    if callback[1] == 'remove':
        subscriptions = data.replace(callback[2],'')
        data = subsription_cleaner(subscriptions)
        if 'Выбраны все варианты' in data:
            data = 'Выбраны все варианты'
        update.callback_query.edit_message_text(
            text=f'Вы удалили {callback[2]}\n{text}:\n\n'\
                    f'{data}\n\nХотите добавить еще, удалить выбранные или продолжить?',
            reply_markup=inline_buttons,
        )
    else:
        if data == '' or data is None:
            data = callback[2]
        elif callback[2] in data:
            pass
        else:
            data += ', ' + callback[2]
            data = subsription_cleaner(data)
        if 'Выбраны все варианты' in data:
            data = 'Выбраны все варианты'
        update.callback_query.edit_message_text(
            text=f'{text}:\n\n'\
                    f'{data}\n\nХотите добавить еще, '\
                        f'удалить выбранные или продолжить?',
            reply_markup=inline_buttons,
        )
    return data


@logger.catch
def vacancy_paginator(vacancies: list, pattern: str,
                      page: int, text: str, update, context):
    vacancies = vacancies[::-1]
    if len(vacancies) == 0:
        inline_keyboard = [[InlineKeyboardButton('Вернуться ',
                                                 callback_data='start')]]
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        update.callback_query.edit_message_text(
            text='Не найдено. Попробуйте изменить фильтр',
            reply_markup=inline_buttons
        )
    else:
        page_num = page_definer(vacancies)
        paginator = InlineKeyboardPaginator(
            page_num,
            current_page=page,
            data_pattern=f'{pattern}'+'#{page}'
        )
        # Defining a range of vacancies that should be applicable to current page
        # And adding each vacancy as a new button
        vacancies_range = vacancies[page*PAGE_SPLIT-PAGE_SPLIT:page*PAGE_SPLIT]
        for i in vacancies_range:
            paginator.add_before(InlineKeyboardButton(
                        text=f'{i["title"]} | {i["salary"]} | {i["joining_date"]}',
                        callback_data=f'detail_{pattern}'+f'#{page}'+f'_{i["id"]}'))
        # If user pressed current page twicely, than will add space to button
        # To change markup and avoid BadRequest error from telegram
        if context.user_data[CURRENT_PAGE] == page:
            paginator.add_after(InlineKeyboardButton('Вернуться ',
                                                    callback_data='start'))
        else:
            paginator.add_after(InlineKeyboardButton('Вернуться',
                                                    callback_data='start'))
        update.callback_query.edit_message_text(
            text=text,
            reply_markup=paginator.markup,
            parse_mode='Markdown'
        )
        # Updating current page to real current page
        context.user_data[CURRENT_PAGE] = page
    return ConversationHandler.END


@logger.catch
def start_buttons_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    try:
        request = update.callback_query
        user_id = request.from_user.id
    except AttributeError:
        request = update.message
        user_id = request.from_user.id
    inline_keyboard = [
        [
            InlineKeyboardButton(text='Все новые вакансии ' + u'\U0001F50E',
                                callback_data='new')
        ],[
            InlineKeyboardButton(text='Настроить фильтр вакансий ' + u'\U0001F504',
                                callback_data='filter_'),
        ],[
            InlineKeyboardButton(text='Заполнить апликейшн ' + u'\U0001F6E5',
                                callback_data='profile'),
        ],
    ]

    if not Profile.objects.filter(external_id=user_id).exists():
        inline_keyboard.insert(2,
            [InlineKeyboardButton(text='Вакансии согласно вашему апликейшн ' + u'\U0001F477',
                callback_data='profile')]
        )
        inline_keyboard.insert(3,
            [InlineKeyboardButton(text='Получать уведомления о новых вакансиях ' + u'\U0001F514',
                callback_data='newsletter_all')]
        )
    else:
        inline_keyboard.insert(2,
            [InlineKeyboardButton(text='Вакансии согласно вашему апликейшн ' + u'\U0001F477',
                callback_data='searchsubscription#1')]
        )
        inline_keyboard.insert(3,
            [InlineKeyboardButton(text='Получать уведомления о новых вакансиях ' + u'\U0001F514',
                callback_data='newsletter_')]
        )
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    if request == update.message:
        context.user_data['FILTER_TITLE'] = ''
        context.user_data['FILTER_FLEET'] = ''
        context.user_data['FILTER_SALARY'] = ''
        context.user_data['FILTER_DATE'] = ''
        context.user_data['FILTER_CONTRACT'] = ''
        context.user_data['FILTER_CREW'] = ''
        update.message.reply_text(
            text='Вы находитесь в главном меню. Чтобы вернуться сюда в любой '\
                'момент нажмите или выберите команду /menu. Выберите действие '\
                'чтобы продолжить.',
            reply_markup=inline_buttons,
        )
    else:
        update.callback_query.edit_message_text(
            text='Вы находитесь в главном меню. Чтобы вернуться сюда в любой '\
                'момент нажмите или выберите команду /menu. Выберите дейсвтие '\
                'чтобы продолжить.',
            reply_markup=inline_buttons,
        )
    context.user_data[CURRENT_PAGE] = 0
    return ConversationHandler.END


@logger.catch
def detail_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    callback = update.callback_query.data.split('_')
    post = Post.objects.get(id=callback[-1])
    text = model_text_details(post)
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='Вернуться', callback_data=callback[1])]
        ],
    )
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=inline_buttons,
    )


@logger.catch
def searchfilter_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    all_entries = Post.objects.all()
    print(all_entries)
    if context.user_data['FILTER_TITLE'] != 'Пропустить' and context.user_data['FILTER_TITLE'] != '' and context.user_data['FILTER_TITLE'] != 'Выбраны все варианты':
        all_entries = all_entries.filter(
                                    title__in=context.user_data['FILTER_TITLE'].split(', '))
    if context.user_data['FILTER_FLEET'] != 'Пропустить' and context.user_data['FILTER_FLEET'] != '' and context.user_data['FILTER_FLEET'] != 'Выбраны все варианты':
        all_entries = all_entries.filter(
                                    vessel__in=context.user_data['FILTER_FLEET'].split(', '))
    if context.user_data['FILTER_DATE'] != '' and context.user_data['FILTER_DATE'] is not None:
        all_entries = all_entries.filter(
                                    joining_date__gte=context.user_data['FILTER_DATE'])
    post_list = model_transcriptor(all_entries)
    print(post_list)
    if post_list == []:
        update.callback_query.edit_message_text(
            text='По Вашему фильтру вакансий не найдено. /menu'
        )
        return ConversationHandler.END
    else:
        result = []
        for post in post_list:
            if context.user_data['FILTER_SALARY'] == '' or context.user_data['FILTER_SALARY'] == 'Не важно':
                cleaned_sub_salary_start = 0
                cleaned_sub_salary_end = 1000000
            else:
                cleaned_sub_salary = re.findall(r'[0-9]+',context.user_data['FILTER_SALARY'])
                cleaned_sub_salary_start = int(cleaned_sub_salary[0])
                cleaned_sub_salary_end = int(cleaned_sub_salary[1])
            if context.user_data['FILTER_CONTRACT'] == '' or context.user_data['FILTER_CONTRACT'] == 'Не важно':
                cleaned_sub_contract = 0
            else:
                cleaned_sub_contract = int(re.findall(r'[0-9]+', context.user_data['FILTER_CONTRACT'])[0])
            cleaned_salary = int(re.findall(r'[0-9]+', post['salary'])[0])
            if post['voyage_duration'] is None:
                cleaned_contract = 6
            else:
                cleaned_contract = int(re.findall(r'[0-9]+', post['voyage_duration'])[0])
            if cleaned_sub_salary_start != '' \
               and cleaned_sub_salary_end != '' \
               and cleaned_sub_salary_start <= cleaned_salary \
               and cleaned_salary <= cleaned_sub_salary_end:
                if cleaned_contract <= cleaned_sub_contract:
                        result.append(post)
        page = int(update.callback_query.data.split('#')[1])
        vacancy_paginator(vacancies=result,
                        pattern='searchfilter',
                        page=page,
                        text='Перечень вакансий по указаному фильтру.',
                        update=update,
                        context=context)


@logger.catch
def searchsubscription_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    p = Profile.objects.get(external_id=update.callback_query.from_user.id)
    all_entries = Post.objects.all()
    if p.title_subscriptions != 'Пропустить' and p.title_subscriptions != '' and  p.title_subscriptions != 'Выбраны все варианты':
        all_entries = all_entries.filter(
                                    title__in=p.title_subscriptions.split(', '))
    if p.fleet_subscriptions != 'Пропустить' and p.fleet_subscriptions != '' and  p.fleet_subscriptions != 'Выбраны все варианты':
        all_entries = all_entries.filter(
                                    vessel__in=p.fleet_subscriptions.split(', '))
    if p.date_ready != '' and p.date_ready is not None:
        all_entries = all_entries.filter(
                                    joining_date__gte=datetime.strptime(p.date_ready, '%Y-%m-%d'))
    post_list = model_transcriptor(all_entries)
    if post_list == []:
        update.callback_query.edit_message_text(
            text='По Вашему профилю вакансий не найдено. /menu'
        )
        return ConversationHandler.END
    else:
        result = []
        for post in post_list:
            if p.salary_subscription == '' or p.salary_subscription == 'Не важно' or p.salary_subscription is None:
                cleaned_sub_salary_start = 0
                cleaned_sub_salary_end = 1000000
            else:
                cleaned_sub_salary = re.findall(r'[0-9]+',p.salary_subscription)
                cleaned_sub_salary_start = int(cleaned_sub_salary[0])
                cleaned_sub_salary_end = int(cleaned_sub_salary[1])
            if p.contract_subscription == '' or p.contract_subscription == 'Не важно' or p.contract_subscription is None:
                cleaned_sub_contract = 0
            else:
                cleaned_sub_contract = int(re.findall(r'[0-9]+', p.contract_subscription)[0])
            cleaned_salary = int(re.findall(r'[0-9]+', post['salary'])[0])
            if post['voyage_duration'] is None:
                cleaned_contract = 6
            else:
                cleaned_contract = int(re.findall(r'[0-9]+', post['voyage_duration'])[0])
            if cleaned_sub_salary_start != '' \
               and cleaned_sub_salary_end != '' \
               and cleaned_sub_salary_start <= cleaned_salary \
               and cleaned_salary <= cleaned_sub_salary_end:
                if cleaned_contract <= cleaned_sub_contract:
                    result.append(post)
        page = int(update.callback_query.data.split('#')[1])
        vacancy_paginator(vacancies=result,
                        pattern='searchsubscription',
                        page=page,
                        text='Перечень вакансий по Вашему профилю.',
                        update=update,
                        context=context)


@logger.catch
def new_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='За день', callback_data='newday#1'),
                InlineKeyboardButton(text='За неделю', callback_data='newweek#1'),
            ]
        ],
    )
    update.callback_query.edit_message_text(
        text='Выберите за какой период вы хотите просмотреть вакансии',
        reply_markup=inline_buttons,
    )
    context.user_data[CURRENT_PAGE] = 0
    return ConversationHandler.END


@logger.catch
def newday_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    post_list = model_transcriptor(Post.objects.filter(
                                    publish_date__gte=date.today()))
    if post_list == []:
        update.callback_query.edit_message_text(
            text='Новых вакансий пока нет. /menu'
        )
        return ConversationHandler.END
    else:
        page = int(update.callback_query.data.split('#')[1])
        vacancy_paginator(vacancies=post_list,
                        pattern='newday',
                        page=page,
                        text='Перечень новых вакансий за день.',
                        update=update,
                        context=context)


@logger.catch
def newweek_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    week_ago_date = date.today() - timedelta(days=7)
    post_list = model_transcriptor(Post.objects.filter(
                                    publish_date__gte=week_ago_date))
    if post_list == []:
        update.callback_query.edit_message_text(
            text='Новых вакансий пока нет. /menu'
        )
        return ConversationHandler.END
    else:
        page = int(update.callback_query.data.split('#')[1])
        vacancy_paginator(vacancies=post_list,
                        pattern='newweek',
                        page=page,
                        text='Перечень новых вакансий за неделю.',
                        update=update,
                        context=context)


@logger.catch
def newsletter_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    callback = update.callback_query.data.split('_')
    p = Profile.objects.get_or_create(
        external_id=update.callback_query.from_user.id,
        name=update.callback_query.from_user.username
    )[0]
    if p.subscription:
        inline_keyboard = [
            [
                InlineKeyboardButton(text='Отписаться',
                                    callback_data='newsletter_unsub'),
            ],
            [
                InlineKeyboardButton(text='Вернуться в меню',
                                    callback_data='start'),
            ]
        ]
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        text = 'Вы подписаны на следующее:\n\n'
        if p.__dict__['title_subscriptions'] != '':
            text += f'Должности: {p.title_subscriptions}\n'
        if p.__dict__['fleet_subscriptions'] != '':
            text += f'Типы судна: {p.fleet_subscriptions}\n'
        if p.__dict__['salary_subscription'] != '':
            if p.salary_subscription == '10000-1000000$':
                salary = '10000$+'
            else:
                salary = p.salary_subscription
            text += f'Зарплата: {salary}\n'
        if p.__dict__['crew_subscription'] != '':
            text += f'Экипаж: {p.crew_subscription}\n'
        if p.__dict__['contract_subscription'] != '':
            text += f'Длительнесть контракта: {p.contract_subscription}\n'
        if text == 'Вы подписаны на следующее:\n\n':
            text += 'Все вакансии'
    else:
        inline_keyboard = [
            [
                InlineKeyboardButton(text='Подписаться',
                                    callback_data='newsletter_confirm'),
            ],
            [
                InlineKeyboardButton(text='Вернуться в меню',
                                    callback_data='start'),
            ]
        ]
        inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
        text = 'Вы хотите подтвердить подписку на вакансии по Вашему профилю?'
    if callback[1] == 'confirm':
        p.subscription = True
        p.save()
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Отписаться',
                                    callback_data='newsletter_unsub'),
            ],
            [
                InlineKeyboardButton(text='Вернуться в меню',
                                    callback_data='start'),
            ]
        ]
        text = 'Вы подписались на рассылку:\n\n'
        if p.__dict__['title_subscriptions'] != '':
            text += f'Должности: {p.title_subscriptions}\n'
        if p.__dict__['fleet_subscriptions'] != '':
            text += f'Типы судна: {p.fleet_subscriptions}\n'
        if p.__dict__['salary_subscription'] != '':
            if p.salary_subscription == '10000-1000000$':
                salary = '10000$+'
            else:
                salary = p.salary_subscription
            text += f'Зарплата: {salary}\n'
        if p.__dict__['crew_subscription'] != '':
            text += f'Экипаж: {p.crew_subscription}\n'
        if p.__dict__['contract_subscription'] != '':
            text += f'Длительнесть контракта: {p.contract_subscription}\n'
        if text == 'Вы подписались на рассылку:\n\n':
            text += 'Все вакансии'
    elif callback[1] == 'unsub':
        p.subscription = False
        p.save()
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подписаться',
                                    callback_data='newsletter_confirm'),
            ],
            [
                InlineKeyboardButton(text='Вернуться в меню',
                                    callback_data='start'),
            ]
        ]
        text = 'Вы отписались от рассылки.'
    elif callback[1] == 'all':
        text = 'У Вас не заполнен профиль, поэтому при подписке Вам будет '\
                'приходить все вакансии. Хотите подтвердить или перейти к '\
                'заполнению профиля?'
        inline_keyboard.insert(0,
            [InlineKeyboardButton(text='Мой профиль',
                callback_data='profile')]
        )
    else:
        p.save()
    inline_buttons = InlineKeyboardMarkup(inline_keyboard=inline_keyboard)
    update.callback_query.edit_message_text(
        text=text,
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def filter_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    callback = update.callback_query.data.split('_')
    if callback[0] == 'profile':
        profile_handler(update, context)
        return ConversationHandler.END
    text = ''
    message = ''
    if ';' in update.callback_query.data:
        selected,date = telegramcalendar.process_calendar_selection(update, context)
        if selected:
            context.user_data['FILTER_DATE'] = date
        else:
            context.user_data['FILTER_DATE'] = ''
            return FILTER
    else:
        if callback[1] == 'clear':
            context.user_data['FILTER_TITLE'] = ''
            context.user_data['FILTER_FLEET'] = ''
            context.user_data['FILTER_SALARY'] = ''
            context.user_data['FILTER_DATE'] = ''
            context.user_data['FILTER_CONTRACT'] = ''
            context.user_data['FILTER_CREW'] = ''
        if callback[1] == 'salary':
            context.user_data['FILTER_SALARY'] = callback[2]
        if callback[1] == 'contract':
            context.user_data['FILTER_CONTRACT'] = callback[2]
        if callback[1] == 'crew':
            context.user_data['FILTER_CREW'] = callback[2]
    if context.user_data['FILTER_DATE'] != '':
        date_choise = context.user_data['FILTER_DATE'].strftime("%d/%m/%Y")
        text += f'\nНачальная дата старта: {date_choise}'
    if context.user_data['FILTER_SALARY'] != '':
        text += f'\nЗарплата: {SALARY_MATCHES[context.user_data["FILTER_SALARY"]]}'
    if context.user_data['FILTER_CONTRACT'] != '':
        text += f'\nДлительность контракта: {context.user_data["FILTER_CONTRACT"]}'
    if context.user_data['FILTER_CREW'] != '':
        text += f'\nЭкипаж: {context.user_data["FILTER_CREW"]}'
    if context.user_data['FILTER_TITLE'] != '':
        text += f'\nДолжность: {context.user_data["FILTER_TITLE"]}'
    if context.user_data['FILTER_FLEET'] != '':
        text += f'\nТипы судна: {context.user_data["FILTER_FLEET"]}'
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Должность',
                                    callback_data='title_add_'),
                InlineKeyboardButton(text='Зарплата',
                                    callback_data='salary_filter'),
            ],[
                InlineKeyboardButton(text='Типы судна',
                                    callback_data='fleet_add_'),
                InlineKeyboardButton(text='Длительность контракта',
                                    callback_data='contract_filter'),
            ],[
                InlineKeyboardButton(text='Экипаж',
                                    callback_data='crew_filter'),
                InlineKeyboardButton(text='Дата готовности',
                                    callback_data='date_filter'),
            ],[
                InlineKeyboardButton(text='Поиск',
                                    callback_data='searchfilter#1'),
            ],[
                InlineKeyboardButton(text='Сбросить',
                                    callback_data='filter_clear'),
            ],[
                InlineKeyboardButton(text='Вернуться',
                                    callback_data='start'),
            ],
        ],
    )
    if text == '':
        message = 'Выберите какие-то параметры для того чтобы начать поиск.'
    else:
        message = f'Вы выбрали следующие параметры поиска\n{text}.'
    update.callback_query.edit_message_text(
        text=message,
        reply_markup=inline_buttons,
    )
    context.user_data['NEXT_STAGE_CALLBACK'] = 'filter_'
    return ConversationHandler.END


@logger.catch
def profile_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    inline_keyboard = [
        [InlineKeyboardButton(text='Главное меню', callback_data='start')],
    ]
    if not Profile.objects.filter(
            external_id=update.callback_query.from_user.id).exists():
        inline_keyboard.insert(0,
            [InlineKeyboardButton(text='Заполнить личный профиль',
                callback_data='title_add_')]
        )
        context.user_data['NEXT_STAGE_CALLBACK'] = 'salary_reg'
    else:
        inline_keyboard.insert(0,
            [InlineKeyboardButton(text='Изменить профиль',
                                    callback_data='profileedit_')]
        )
        inline_keyboard.insert(1,
            [InlineKeyboardButton(text='Удалить профиль',
                                    callback_data='profiledelete')]
        )
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=inline_keyboard
    )
    update.callback_query.edit_message_text(
        text='Выберите желаемое действие над личным профилем.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def profile_edit_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    p = Profile.objects.get(external_id=update.callback_query.from_user.id)
    callback = update.callback_query.data.split('_')
    text = ''
    if ';' in update.callback_query.data:
        selected,date = telegramcalendar.process_calendar_selection(update, context)
        if selected:
            date_choise = date.strftime("%d/%m/%Y")
            p = Profile.objects.get(external_id=update.callback_query.from_user.id)
            text = f'Вы подтвердили дату {date_choise}\n\n'
            p.date_ready = date
        else:
            return EDIT
    else:
        if callback[1] == 'salary':
            p.salary_subscription = callback[2]
        if callback[1] == 'contract':
            p.contract_subscription = callback[2]
        if callback[1] == 'crew':
            p.crew_subscription = callback[2]

    p.save()
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Должность',
                                    callback_data='choicetitle_add_')
            ],[
                InlineKeyboardButton(text='Зарплата',
                                    callback_data='salary_edit'),
                InlineKeyboardButton(text='Типы судна',
                                    callback_data='choicefleet_add_')
            ],[
                InlineKeyboardButton(text='Длительность контракта',
                                    callback_data='contract_edit'),
                InlineKeyboardButton(text='Экипаж',
                                    callback_data='crew_edit'),
            ],[
                InlineKeyboardButton(text='Дата готовности',
                                    callback_data='date_edit'),
                InlineKeyboardButton(text='Email',
                                    callback_data='email'),
            ],[
                InlineKeyboardButton(text='Вернуться',
                                    callback_data='profile'),
            ],
        ],
    )
    update.callback_query.edit_message_text(
        text=f'{text}Выберите какие параметры Вы хотите изменить.',
        reply_markup=inline_buttons,
    )
    context.user_data['NEXT_STAGE_CALLBACK'] = 'profileedit_'
    return ConversationHandler.END


@logger.catch
def profile_delete_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    p = Profile.objects.get(external_id=update.callback_query.from_user.id)
    p.delete()
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Вернуться в меню',
                                    callback_data='start'),
            ],
        ],
    )
    update.callback_query.edit_message_text(
        text='Ваш профиль успешно удален.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def title_handler(update: Update, context: CallbackContext):
    """ Начало взаимодействия по клику на inline-кнопку
    """
    logger.info(f'user_data: {context.user_data}')
    callback = update.callback_query.data.split('_')
    show_item_list(update, settings.TITLE_CHOICES, callback[0], callback[1])
    p = Profile.objects.get_or_create(
        external_id=update.callback_query.from_user.id,
        name=update.callback_query.from_user.username
    )[0]
    p.save()
    return ConversationHandler.END


@logger.catch
def title_choose_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    if context.user_data['NEXT_STAGE_CALLBACK'] == 'filter_':
        updated_subs = item_selection_handler(
                            update=update,
                            data=context.user_data['FILTER_TITLE'],
                            callback_data='title',
                            callback_next=context.user_data['NEXT_STAGE_CALLBACK'],
                            text='Вы выбрали '\
                                'следующие должности в фильтре')
        context.user_data['FILTER_TITLE'] = updated_subs
    else:
        titles = ''
        p = Profile.objects.get_or_create(external_id=update.callback_query.from_user.id)[0]
        try:
            titles = p.title_subscriptions
        except AttributeError:
            p = Profile.objects.get(external_id=update.callback_query.from_user.id)
            titles = p.title_subscriptions
        finally:
            updated_subs = item_selection_handler(
                                update=update,
                                data=titles,
                                callback_data='title',
                                callback_next=context.user_data['NEXT_STAGE_CALLBACK'],
                                text='Сейчас Вы подписаны на '\
                                    'следующие должности')
            p.title_subscriptions = updated_subs
            p.save()
    return ConversationHandler.END


@logger.catch
def salary_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    text = ''
    if update.callback_query.data.split('_')[1] == 'reg':
        callback = 'fleet_add_'
        context.user_data['NEXT_STAGE_CALLBACK'] = 'contract_reg_'
    elif update.callback_query.data.split('_')[1] == 'edit':
        p = Profile.objects.get(external_id=update.callback_query.from_user.id)
        callback = 'profileedit_salary_'
        text = f'Сейчас у Вас указано значение: {p.salary_subscription}\n\n'
    else:
        callback = 'filter_salary_'
        if context.user_data['FILTER_SALARY'] == '':
            text = ''
        else:
            text = f'Сейчас у Вас указано значение: '\
                    f'{context.user_data["FILTER_SALARY"]}\n\n'
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='до 1000$',
                                callback_data=callback+'0-1000$'),
            InlineKeyboardButton(text='1000-3000$',
                                callback_data=callback+'1000-3000$')
            ],[
            InlineKeyboardButton(text='3000-5000$',
                                callback_data=callback+'3000-5000$'),
            InlineKeyboardButton(text='5000-10000$',
                                callback_data=callback+'5000-10000$')
            ],[
            InlineKeyboardButton(text='10000$+',
                                callback_data=callback+'10000-1000000$'),
            InlineKeyboardButton(text='Не важно',
                                callback_data=callback+'Не важно')
            ],
        ],
    )
    update.callback_query.edit_message_text(
        text=f'{text}Укажите промежуток зарплат который Вас интересует.',
        reply_markup=inline_buttons,
    )


@logger.catch
def fleet_handler(update: Update, context: CallbackContext):
    """ Начало взаимодействия по клику на inline-кнопку
    """
    callback = update.callback_query.data
    callback_spl = callback.split('_')
    if callback_spl[2] != '':
        p = Profile.objects.get(external_id=update.callback_query.from_user.id)
        p.salary_subscription = callback_spl[2]
        p.save()
    data = settings.FLEET_CHOICES
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text=data[1][0],
                                callback_data='vessel_' + callback + '_' + data[1][0]),
            InlineKeyboardButton(text=data[2][0],
                                callback_data='vessel_' + callback + '_' + data[2][0])
            ],[
            InlineKeyboardButton(text=data[3][0],
                                callback_data='choice' + callback_spl[0] + '_' +callback_spl[1] + '_Fishing Vessel'),
            InlineKeyboardButton(text=data[4][0],
                                callback_data='vessel_' + callback + '_' + data[4][0])
            ],[
            InlineKeyboardButton(text=data[5][0],
                                callback_data='vessel_' + callback + '_' + data[5][0]),
            InlineKeyboardButton(text='Пропустить',
                                callback_data='choice' + callback_spl[0] + '_' +callback_spl[1] + '_Выбраны все варианты')
            ],
        ],
    )
    update.callback_query.edit_message_text(
        text='Выберите интересующий Вас вариант.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def vessel_handler(update: Update, context: CallbackContext):
    """ Начало взаимодействия по клику на inline-кнопку
    """
    logger.info(f'user_data: {context.user_data}')
    callback = update.callback_query.data.split('_')
    show_item_list(update, settings.VESSEL_BASE[callback[4]], callback[1], callback[2])
    return ConversationHandler.END


@logger.catch
def fleet_choose_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    if context.user_data['NEXT_STAGE_CALLBACK'] == 'filter_':
        updated_subs = item_selection_handler(
                            update=update,
                            data=context.user_data['FILTER_FLEET'],
                            callback_data='fleet',
                            callback_next=context.user_data['NEXT_STAGE_CALLBACK'],
                            text='Вы выбрали '\
                                'следующие типы судна в фильтре')
        context.user_data['FILTER_FLEET'] = updated_subs
    else:
        p = Profile.objects.get_or_create(external_id=update.callback_query.from_user.id)[0]
        try:
            fleets = p.fleet_subscriptions
        except AttributeError:
            p = Profile.objects.get(external_id=update.callback_query.from_user.id)
            fleets = p.fleet_subscriptions
        finally:
            updated_subs = item_selection_handler(
                            update=update,
                            data=fleets,
                            callback_data='fleet',
                            callback_next=context.user_data['NEXT_STAGE_CALLBACK'],
                            text='Сейчас Вы подписаны на '\
                                'следующие типы судна')
            p.fleet_subscriptions = updated_subs
            p.save()
    return ConversationHandler.END


@logger.catch
def contract_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    callback_data = update.callback_query.data.split('_')
    text = ''
    if callback_data[1] == 'reg':
        callback = 'crew_reg_'
    elif callback_data[1] == 'edit':
        p = Profile.objects.get(external_id=update.callback_query.from_user.id)
        callback = 'profileedit_contract_'
        text = f'Сейчас у Вас указано значение: {p.contract_subscription}\n\n'
    else:
        callback = 'filter_contract_'
        if context.user_data['FILTER_CONTRACT'] == '':
            text = ''
        else:
            text = f'Сейчас у Вас указано значение: '\
                    f'{context.user_data["FILTER_CONTRACT"]}\n\n'
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='до 2',
                                 callback_data=callback+'до 2'),
            InlineKeyboardButton(text='до 4',
                                 callback_data=callback+'до 4')
            ],[
            InlineKeyboardButton(text='до 6',
                                 callback_data=callback+'до 6'),
            InlineKeyboardButton(text='до 8',
                                 callback_data=callback+'до 8')
            ],[
            InlineKeyboardButton(text='Не важно',
                                 callback_data=callback+'Не важно')
            ]
        ],
    )
    update.callback_query.edit_message_text(
        text=f'{text}Укажите желаемую длительность контракта.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def crew_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    callback_data = update.callback_query.data.split('_')
    text = ''
    if callback_data[1] == 'reg':
        callback = 'date_reg_'
        p = Profile.objects.get(external_id=update.callback_query.from_user.id)
        p.contract_subscription = callback_data[2]
        p.save()
    elif callback_data[1] == 'edit':
        p = Profile.objects.get(external_id=update.callback_query.from_user.id)
        callback = 'profileedit_crew_'
        text = f'Сейчас у Вас указано значение: {p.crew_subscription}\n\n'
    else:
        callback = 'filter_crew_'
        if context.user_data['FILTER_CREW'] == '':
            text = ''
        else:
            text = f'Сейчас у Вас указано значение: '\
                    f'{context.user_data["FILTER_CREW"]}\n\n'
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='Микс',
                                callback_data=callback+'Микс'),
            InlineKeyboardButton(text='Без знания англ.',
                                callback_data=callback+'Без знания англ')
            ],[
            InlineKeyboardButton(text='Не важно',
                                callback_data=callback+'Не важно')
            ]
        ],
    )
    update.callback_query.edit_message_text(
        text=f'{text}Укажите желаемый экипаж.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def date_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    if not hasattr(update, 'callback_query'):
        context.user_data['NEXT_STAGE_CALLBACK'] = ''
        start_buttons_handler(update, context)
    else:
        callback_data = update.callback_query.data.split('_')
        update.callback_query.edit_message_text("Выберите дату Вашей готовности",
                            reply_markup=telegramcalendar.create_calendar())
        if callback_data[1] == 'reg':
            p = Profile.objects.get(external_id=update.callback_query.from_user.id)
            p.crew_subscription = callback_data[2]
            p.save()
            return CALENDAR
        elif callback_data[1] == 'edit':
            return EDIT
        else:
            return FILTER


@logger.catch
def email_question_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    selected,date = telegramcalendar.process_calendar_selection(update, context)
    context.user_data['NEXT_STAGE_CALLBACK'] = 'reg'
    if selected:
        date_choise = date.strftime("%d/%m/%Y")
        p = Profile.objects.get(external_id=update.callback_query.from_user.id)
        p.date_ready = date
        p.save()
        inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
                [
                InlineKeyboardButton(text='Да',
                                    callback_data='email'),
                InlineKeyboardButton(text='Нет',
                                    callback_data='success_registration')
                ]
            ],
        )
        update.callback_query.edit_message_text(
            text=f'Вы выбрали {date.strftime("%d/%m/%Y")}\n\n'\
                    f'Предоставить адрес электронной почты?',
            reply_markup=inline_buttons,
        )
        return ConversationHandler.END
    else:
        return CALENDAR


@logger.catch
def email_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    update.callback_query.edit_message_text(
        text='Введите Ваш email пожалуйста.'
    )
    return EMAIL_CONFIRM


@logger.catch
def email_confirmer_handler(update: Update, context: CallbackContext):
    logger.info(f'user_data: {context.user_data}')
    p = Profile.objects.get(external_id=update.message.from_user.id)
    p.email = update.message.text
    p.save()
    if context.user_data['NEXT_STAGE_CALLBACK'] == 'reg':
        callback = 'success_registration'
    else:
        callback = 'profileedit_'
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='Подтвердить',
                                callback_data=callback),
            InlineKeyboardButton(text='Изменить',
                                callback_data='email')
            ]
        ],
    )
    update.message.reply_text(
        text=f"Вы указали {update.message.text}.",
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def success_handler(update: Update, context: CallbackContext):
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
            InlineKeyboardButton(text='Вернуться в меню',
                                callback_data='start')
            ]
        ],
    )
    update.callback_query.edit_message_text(
        text="Спасибо за регистрацию.",
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END
