import json
import re
from datetime import date, datetime, timedelta
from django.conf import settings
from django.forms.models import model_to_dict
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from loguru import logger
from web_hiring.models import Post
from .resources import keyboards_content as kb
from .resources import rich_media_content as rm
from .resources.tools import (view_definer, model_text_details,
                              model_transcriptor, action_insert)


logger.add('logs/info.log', format='{time} {level} {message}',
            level='INFO', rotation="1 MB", compression='zip')


@logger.catch
def user_message_handler(viber, viber_request):
    """Receiving a message from user and sending replies."""
    logger.info(f'user_data: {viber_request.sender.id}')
    message = viber_request.message
    tracking_data = message.tracking_data
    # Data for Message
    reply_text = ''
    reply_keyboard = {}
    reply_rich_media = {}

    if tracking_data:
        tracking_data = json.loads(tracking_data)
    else:
        tracking_data = {}

    logger.info(f'user_data: {tracking_data}')
    text = viber_request.message.text

    if text[:6] == 'newday':
        last_hours = datetime.now() - timedelta(hours=24)
        post_list = model_transcriptor(Post.objects.filter(
                                        publish_date__gte=last_hours))[::-1]
        callback = text.split('_')
        if post_list:
            reply_text, reply_rich_media, reply_keyboard = view_definer(
                                                            post_list,
                                                            tracking_data,
                                                            callback,
                                                            'newday')
        else:
            reply_text = 'Новых вакансий пока нет.'
            reply_keyboard = kb.GO_TO_MENU_KEYBOARD
    elif text[:6] == 'filter':
        callback = text.split('_')
        if len(callback) > 1 and callback[1] == 'title':
            tracking_data['title'] = callback[2]
        if len(callback) > 1 and callback[1] == 'salary':
            tracking_data['salary'] = callback[2]
        if ('title' in tracking_data and tracking_data['title'] != '') or\
            ('salary' in tracking_data and tracking_data['salary'] != ''):
            reply_text = 'Вы выбрали следующие параметры поиска.\n'
            if 'title' in tracking_data and tracking_data['title'] != '':
                reply_text += f'\nДолжность: {tracking_data["title"]}'
            if 'salary' in tracking_data and tracking_data['salary'] != '':
                reply_text += f'\nЗарплата: {tracking_data["salary"]}'
        else:
            reply_text = 'Выберите параметр по которому отфильтровать вакансии.'
        reply_keyboard = kb.FILTER_KEYBOARD
    elif text[:6] == 'detail':
        callback_id = text.split('_')[1]
        back_menu = text.split('_')[2]
        post = Post.objects.get(id=callback_id)
        reply_text = model_text_details(post)
        reply_keyboard = action_insert(kb.RETURN_KEYBOARD, back_menu)
    elif text == 'title':
        reply_text = 'Выберите интересующую должность.'
        reply_keyboard = kb.GO_TO_MENU_KEYBOARD
        reply_rich_media = rm.TITLE_MEDIA
    elif text == 'salary':
        reply_text = 'Выберите интересующую зарплату.'
        reply_keyboard = kb.GO_TO_MENU_KEYBOARD
        reply_rich_media = rm.SALARY_MEDIA
    elif text == 'reset':
        garbage_title = tracking_data.pop('title', None)
        garbage_salary = tracking_data.pop('salary', None)
        reply_text = 'Выберите параметр по которому отфильтровать вакансии.'
        reply_keyboard = kb.FILTER_KEYBOARD
    elif text[:6] == 'search':
        all_entries = Post.objects.all()
        callback = text.split('_')

        if 'title' in tracking_data and tracking_data['title'] != '':
            logger.info(f'user_data: {tracking_data["title"]}')
            all_entries = all_entries.filter(title__in=tracking_data['title'].split(', '))
        post_list = model_transcriptor(all_entries)[::-1]
        titles_unique = set([x['title'] for x in post_list])
        # logger.info(f'user_data: {titles_unique}')
        if post_list == []:
            reply_text = 'По Вашему фильтру вакансий не найдено.'
            reply_keyboard = kb.GO_TO_MENU_KEYBOARD
        else:
            result = []
            for post in post_list:
                if 'salary' not in tracking_data or \
                tracking_data['salary'] == '' or \
                tracking_data['salary'] == 'Не важно':
                    cleaned_sub_salary_start = 0
                    cleaned_sub_salary_end = 1000000
                else:
                    cleaned_sub_salary = re.findall(r'[0-9]+',tracking_data['salary'])
                    cleaned_sub_salary_start = int(cleaned_sub_salary[0])
                    cleaned_sub_salary_end = int(cleaned_sub_salary[1])
                cleaned_salary = int(re.findall(r'[0-9]+', post['salary'])[0])
                if cleaned_sub_salary_start != '' \
                   and cleaned_sub_salary_end != '' \
                   and cleaned_sub_salary_start <= cleaned_salary \
                   and cleaned_salary <= cleaned_sub_salary_end:
                    result.append(post)
            reply_text, reply_rich_media, reply_keyboard = view_definer(
                                                            result,
                                                            tracking_data,
                                                            callback,
                                                            'search')
    elif text == 'menu':
        # Setting the possibility to write a comment
        tracking_data['page'] = '0'
        reply_text = 'Выберите действие чтобы продолжить.'
        reply_keyboard = kb.MENU_KEYBOARD
    else:
        reply_text = 'Выберите действие чтобы продолжить.'
        reply_keyboard = kb.MENU_KEYBOARD

    tracking_data = json.dumps(tracking_data)
    if reply_rich_media:
        reply = [RichMediaMessage(rich_media=reply_rich_media,
                         alt_text=reply_text,
                         tracking_data=tracking_data,
                         min_api_version=7)]
        reply.append(TextMessage(text=reply_text,
                             keyboard=reply_keyboard,
                             tracking_data=tracking_data,
                             min_api_version=3))
    else:
        reply = [TextMessage(text=reply_text,
                             keyboard=reply_keyboard,
                             tracking_data=tracking_data,
                             min_api_version=3)]
    viber.send_messages(viber_request.sender.id, reply)
