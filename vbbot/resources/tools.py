"""Additional functions for Viber bot."""
from datetime import datetime
from loguru import logger
from . import keyboards_content as kb


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
        date_raw = datetime.strptime(post.joining_date, '%Y-%m-%d')
        date_formatted = date_raw.strftime("%d %B, %Y")
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
def action_insert(keyboard, identifier):
    if identifier == 'filter':
        for button in keyboard['Buttons']:
            if 'newday' in button['ActionBody']:
                button['ActionBody'].replace('newday', 'filter')
    return keyboard


@logger.catch
def keyboard_consctructor(items: list) -> dict:
    """Pasting infromation from list of items to keyboard menu template."""
    keyboard = {
        "DefaultHeight": False,
        "BgColor": "#FFFFFF",
        "Type": "keyboard",
        "Buttons": [{
                "Columns": item[2],
                "Rows": 1,
                "BgColor": "#A9E2F3",
                "BgLoop": True,
                "ActionType": "reply",
                "ActionBody": item[0],
                "ReplyType": "message",
                "Text": item[1]
        } for item in items]
    }
    return keyboard


@logger.catch
def paginator(post_list: list, page: int, identifier: str):
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
                "ActionBody": f"detail-{item['id']}-{identifier}",
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
def view_definer(post_list, tracking_data, callback, identifier):
    if 'page' in tracking_data and tracking_data['page'] != '':
        max_pages = int((len(post_list) / 42 - 1))
        if callback[1] == 'more':
            if max_pages > int(tracking_data['page']):
                tracking_data['page'] = str(int(tracking_data['page']) + 1)
                reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_ALL,
                                               identifier)
            if max_pages == int(tracking_data['page']):
                tracking_data['page'] = str(int(tracking_data['page']) + 1)
                reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_MENU_BACK,
                                               identifier)
        if callback[1] == 'back':
            if int(tracking_data['page']) != 0:
                tracking_data['page'] = str(int(tracking_data['page']) - 1)
                reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_ALL,
                                               identifier)
            else:
                reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_MENU_MORE,
                                               identifier)
        if callback[1] == 'return':
            if max_pages > int(tracking_data['page']):
                reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_ALL,
                                               identifier)
            else:
                reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_MENU_BACK,
                                               identifier)
        if tracking_data['page'] == '0':
            reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_MENU_MORE,
                                           identifier)
        if max_pages == 0:
            reply_keyboard = kb.GO_TO_MENU_KEYBOARD
    else:
        tracking_data['page'] = '0'
        reply_keyboard = action_insert(kb.CONTROL_KEYBOARD_MENU_MORE,
                                       identifier)
    reply_rich_media = paginator(post_list, int(tracking_data['page']), identifier)
    reply_text = 'Выше показаны вакансии за сегодня. Для возвращения в '\
                 'меню воспользуйтесь клавиатурой внизу.'
    return (reply_text, reply_rich_media, reply_keyboard)
