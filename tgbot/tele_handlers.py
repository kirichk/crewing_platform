import os
from telegram import (InlineKeyboardButton, InlineKeyboardMarkup, Update,
                        ReplyKeyboardMarkup, KeyboardButton)
from telegram.ext import (CallbackContext, CallbackQueryHandler, Updater,
                        MessageHandler, CommandHandler, ConversationHandler,
                        Filters)
from telegram.utils.request import Request
from django.conf import settings
from .models import Profile
from datetime import datetime, timedelta
from loguru import logger


logger.add('info.log', format='{time} {level} {message}',
            level='DEBUG', rotation="1 MB", compression='zip')
PHONE, SALARY_RANGE = range(2)


@logger.catch
def start_buttons_handler(update: Update, context: CallbackContext):
    contact_keyboard = KeyboardButton('Поделиться номером',
                                        request_contact=True,
                                        callback_data='phone_number')
    reply_markup = ReplyKeyboardMarkup(keyboard=[[ contact_keyboard ]],
                                        resize_keyboard=True,
                                        one_time_keyboard=True)
    update.message.reply_text(
                    'Здравствуйте! Для того чтобы начать регистрацию'\
                    ' пожалуйста нажмите "Поделиться номером".',
                    reply_markup=reply_markup)
    return PHONE


@logger.catch
def phone_handler(update: Update, context: CallbackContext):
    """ Начало взаимодействия по клику на inline-кнопку
    """
    t_list_even = settings.TITLE_CHOICES[1:-1:2]
    t_list_non_even = settings.TITLE_CHOICES[2:-2:2]
    t_list_non_even.append(('Все','Все'))
    inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
            [
            InlineKeyboardButton(
                text=i[0],
                callback_data='title-' + i[0]),
            InlineKeyboardButton(
                text=t_list_non_even[t_list_even.index(i)][0],
                callback_data='title-' + t_list_non_even[t_list_even.index(i)][0])
            ] for i in t_list_even
        ],
    )
    try:
        request = update.message
        if request.contact.first_name is None:
            request.contact.first_name = ''
        if request.contact.last_name is None:
            request.contact.last_name = ''
        p = Profile.objects.get_or_create(
            external_id=request.chat_id,
            name=request.from_user.username,
            full_name = (request.contact.first_name +
                        ' ' + request.contact.last_name),
            phone=request.contact.phone_number
        )[0]
        p.save()
        request.reply_text(
            text='Спасибо! Выберите должности которые могут вас интересовать.',
            reply_markup=inline_buttons,
        )
    except AttributeError:
        request = update.callback_query
        request.edit_message_text(
            text='Добавьте еще должности которые могут вас интересовать.',
            reply_markup=inline_buttons,
        )
    return ConversationHandler.END


@logger.catch
def title_handler(update: Update, context: CallbackContext):
    logger.info('user_data: %s', context.user_data)
    choice = update.callback_query.data.split('-')[1]
    p = Profile.objects.get(external_id=update.callback_query.message.chat_id)
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить', callback_data='tconfirm-add'),
                InlineKeyboardButton(text='Удалить', callback_data='tconfirm-rmv')
            ],
            [
                InlineKeyboardButton(text='Перейти дальше', callback_data='tconfirm-next'),
            ]
        ],
    )
    if update.callback_query.data[-3:] == 'rmv':
        subscriptions = p.title_subscriptions.replace(choice,'')
        if subscriptions.startswith(','):
            if len(subscriptions) > 2:
                subscriptions = subscriptions[2:]
            else:
                subscriptions = subscriptions.replace(', ', '')
        else:
            subscriptions = subscriptions.replace(', ,', ',')
        p.title_subscriptions = subscriptions
        p.save()
        update.callback_query.edit_message_text(
            text=f'Вы удалили {choice}\nСейчас вы подписаны на следующие вакансии:\n\n'\
                    f'{subscriptions}\n\nХотите добавить еще, удалить выбранные или перейти дальше?',
            reply_markup=inline_buttons,
        )
    else:
        subscriptions = p.title_subscriptions
        if p.title_subscriptions == '':
            p.title_subscriptions += choice
        elif choice not in p.title_subscriptions:
            p.title_subscriptions += ', ' + choice
        p.save()
        if subscriptions == '':
            text_entry = choice
        else:
            text_entry = subscriptions + ", " + choice
        update.callback_query.edit_message_text(
            text=f'Вы выбрали {choice}\nСейчас вы подписаны на следующие вакансии:\n\n'\
                    f'{text_entry}\n\nХотите добавить еще, удалить выбранные или перейти дальше?',
            reply_markup=inline_buttons,
        )
    return ConversationHandler.END


@logger.catch
def title_edit(update: Update, context: CallbackContext):
    logger.info('user_data: %s', context.user_data)
    p = Profile.objects.get(external_id=update.callback_query.message.chat_id)
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить', callback_data='addt'),
                InlineKeyboardButton(text='Удалить', callback_data='rmvt')
            ],
            [
                InlineKeyboardButton(text='Вернуться', callback_data='srconfirm-next'),
            ]
        ],
    )
    if update.callback_query.data[-3:] == 'rmv':
        choice = update.callback_query.data.split('-')[1]
        subscriptions = p.title_subscriptions.replace(choice,'')
        if subscriptions.startswith(','):
            if len(subscriptions) > 2:
                subscriptions = subscriptions[2:]
            else:
                subscriptions = subscriptions.replace(', ', '')
        else:
            subscriptions = subscriptions.replace(', ,', ',')
        p.title_subscriptions = subscriptions
        p.save()
        update.callback_query.edit_message_text(
            text=f'Вы удалили {choice}\nСейчас вы подписаны на следующие вакансии:\n\n'\
                    f'{subscriptions}\n\nХотите добавить еще, удалить выбранные или вернуться?',
            reply_markup=inline_buttons,
        )
    elif update.callback_query.data == 'editt':
        update.callback_query.edit_message_text(
            text=f'Сейчас вы подписаны на следующие вакансии:\n\n'\
                    f'{p.title_subscriptions}\n\nХотите добавить еще, удалить выбранные или вернуться?',
            reply_markup=inline_buttons,
        )
    else:
        choice = update.callback_query.data.split('-')[1]
        subscriptions = p.title_subscriptions
        if p.title_subscriptions == '':
            p.title_subscriptions += choice
        elif choice not in p.title_subscriptions:
            p.title_subscriptions += ', ' + choice
        p.save()
        if subscriptions == '':
            text_entry = choice
        else:
            text_entry = subscriptions + ", " + choice
        update.callback_query.edit_message_text(
            text=f'Вы выбрали {choice}\nСейчас вы подписаны на следующие вакансии:\n\n'\
                    f'{text_entry}\n\nХотите добавить еще, удалить выбранные или вернуться?',
            reply_markup=inline_buttons,
        )
    return ConversationHandler.END


@logger.catch
def add_title_handler(update: Update, context: CallbackContext):
    t_list_even = settings.TITLE_CHOICES[1:-1:2]
    t_list_non_even = settings.TITLE_CHOICES[2:-2:2]
    t_list_non_even.append(('Все','Все'))
    inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
            [
            InlineKeyboardButton(
                text=i[0],
                callback_data='editt-' + i[0]),
            InlineKeyboardButton(
                text=t_list_non_even[t_list_even.index(i)][0],
                callback_data='editt-' + t_list_non_even[t_list_even.index(i)][0])
            ] for i in t_list_even
        ],
    )
    update.callback_query.edit_message_text(
        text='Добавьте еще должности которые могут вас интересовать.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def remove_title_handler(update: Update, context: CallbackContext):
    logger.info('user_data: %s', context.user_data)
    p = Profile.objects.get(external_id=update.callback_query.message.chat_id)
    subscriptions = p.title_subscriptions
    t_list = subscriptions.split(', ')
    inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
            [InlineKeyboardButton(
                text=i,
                callback_data='editt-' + i + '-rmv')] for i in t_list
        ],
    )
    # Entry.objects.filter(blog=b).update(headline='Everything is the same')
    update.callback_query.edit_message_text(
        text='Нажмите на должности которые Вас более не интересуют.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def clear_title_handler(update: Update, context: CallbackContext):
    logger.info('user_data: %s', context.user_data)
    p = Profile.objects.get(external_id=update.callback_query.message.chat_id)
    subscriptions = p.title_subscriptions
    t_list = subscriptions.split(', ')
    inline_buttons = InlineKeyboardMarkup(
            inline_keyboard=[
            [InlineKeyboardButton(
                text=i,
                callback_data='title-' + i + '-rmv')] for i in t_list
        ],
    )
    # Entry.objects.filter(blog=b).update(headline='Everything is the same')
    update.callback_query.edit_message_text(
        text='Нажмите на должности которые Вас более не интересуют.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def min_salary_handler(update: Update, context: CallbackContext):
    logger.info('user_data: %s', context.user_data)
    update.callback_query.edit_message_text(
        text='Укажите минимальную зарплату которая вас интересует.\n$ в месяц (Пример:2000)'
    )
    return SALARY_RANGE


@logger.catch
def range_salary_handler(update: Update, context: CallbackContext):
    logger.info('user_data: %s', context.user_data)
    p = Profile.objects.get(external_id=update.message.chat_id)
    p.salary_range = update.message.text
    p.save()
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Подтвердить', callback_data='srconfirm-next'),
                InlineKeyboardButton(text='Изменить', callback_data='srconfirm-edit')
            ]
        ],
    )
    update.message.reply_text(
        text=f'Вы указали минимальную зарплату {update.message.text} $/месяц',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END


@logger.catch
def reg_end(update: Update, context: CallbackContext):
    logger.info('user_data: %s', context.user_data)
    p = Profile.objects.get(external_id=update.callback_query.message.chat_id)
    update.callback_query.edit_message_text(
        text=f'Теперь вы будете получать уведомления о новых вакансиях по данным позициям:\n\n'\
        f'{p.title_subscriptions}\n\n В диапазоне зарплат {p.salary_range} $/месяц.\n\n'\
        f'Для того чтобы изменить параметры, введите или намите на команду /menu'
    )
    return ConversationHandler.END


@logger.catch
def menu_handler(update: Update, context: CallbackContext):
    inline_buttons = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Должности', callback_data='editt'),
                InlineKeyboardButton(text='Зарплата', callback_data='srconfirm-edit')
            ]
        ],
    )
    update.message.reply_text(
        text=f'Выберите какие параметры вы хотите поменять.',
        reply_markup=inline_buttons,
    )
    return ConversationHandler.END
