import os
import json
from datetime import date, datetime, timedelta
from django.conf import settings
from django.forms.models import model_to_dict
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.contact_message import ContactMessage
from viberbot.api.messages.location_message import LocationMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from loguru import logger
from web_hiring.models import Post
from .resources import keyboards_content as kb


logger.add('logs/info.log', format='{time} {level} {message}',
            level='INFO', rotation="1 MB", compression='zip')


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


@logger.catch
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
def paginator(post_list: list, page: int):
    splitted_list_for_carousel = list(divide_chunks(post_list, 42))
    displayed_list = splitted_list_for_carousel[page]
    reply_rich_media = {
        "Type":"rich_media",
           "ButtonsGroupColumns":6,
           "ButtonsGroupRows":7,
           "BgColor":"#FFFFFF",
           "Buttons":[]
    }
    buttons = []
    for item in displayed_list:
        buttons.append(
            {
                "Columns": 6,
                "Rows": 1,
                "BgColor": "#A9E2F3",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": f"detail-{item['id']}",
                "Text": f"<b>{item['title']}</b>\n{item['salary']}, {item['joining_date']}",
            }
        )
    reply_rich_media['Buttons'] += buttons
    return reply_rich_media


@logger.catch
def divide_chunks(data: list, divider: int):
    # looping till length l
    for i in range(0, len(data), divider):
        yield data[i:i + divider]


@logger.catch
def user_message_handler(viber, viber_request):
    """Receiving a message from user and sending replies."""
    message = viber_request.message
    tracking_data = message.tracking_data
    # Data for usual TextMessage
    reply_text = ''
    reply_keyboard = {}
    # Data for RichMediaMessage
    reply_alt_text = ''
    reply_rich_media = {}

    if tracking_data:
        tracking_data = json.loads(tracking_data)
    else:
        tracking_data = {}
    text = viber_request.message.text
    if text[:6] == 'newday':
        logger.info(f'user_data: {tracking_data}')
        post_list = model_transcriptor(Post.objects.filter(
                                        publish_date__gte=date.today()))
        callback = text.split('-')
        if post_list:
            if 'page' in tracking_data and tracking_data['page'] != '':
                max_pages = int((len(post_list) / 42 - 1))
                if callback[1] == 'more':
                    if max_pages > int(tracking_data['page']):
                        tracking_data['page'] = str(int(tracking_data['page']) + 1)
                        reply_keyboard = kb.CONTROL_KEYBOARD_ALL
                    if max_pages == int(tracking_data['page']):
                        tracking_data['page'] = str(int(tracking_data['page']) + 1)
                        reply_keyboard = kb.CONTROL_KEYBOARD_MENU_BACK
                if callback[1] == 'back':
                    if int(tracking_data['page']) != 0:
                        tracking_data['page'] = str(int(tracking_data['page']) - 1)
                        reply_keyboard = kb.CONTROL_KEYBOARD_ALL
                    else:
                        reply_keyboard = kb.CONTROL_KEYBOARD_MENU_MORE
                if callback[1] == 'return':
                    if max_pages > int(tracking_data['page']):
                        reply_keyboard = kb.CONTROL_KEYBOARD_ALL
                    else:
                        reply_keyboard = kb.CONTROL_KEYBOARD_MENU_BACK
                if tracking_data['page'] == '0':
                    reply_keyboard = kb.CONTROL_KEYBOARD_MENU_MORE
            else:
                START_PAGE = True
                tracking_data['page'] = '0'
                reply_keyboard = kb.CONTROL_KEYBOARD_MENU_MORE
            reply_rich_media = paginator(post_list, int(tracking_data['page']))
            reply_text = 'Выше показаны вакансии за сегодня. Для возвращения в меню воспользуйтесь клавиатурой внизу.'
        else:
            reply_text = 'Новых вакансий пока нет.'
            reply_keyboard = kb.GO_TO_MENU_KEYBOARD
    elif text[:6] == 'detail':
        callback_id = text.split('-')[1]
        post = Post.objects.get(id=callback_id)
        reply_text = model_text_details(post)
        reply_keyboard = kb.RETURN_KEYBOARD
    elif text == 'menu':
        # Setting the possibility to write a comment
        tracking_data['page'] = '0'
        reply_text = 'Выберите действие чтобы продолжить.'
        reply_keyboard = kb.MENU_KEYBOARD
    else:
        reply_text = ''
        reply_keyboard = {}

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
