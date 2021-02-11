import os
import json
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

    if tracking_data is None:
        tracking_data = {'comment_mode': 'off'}
    else:
        tracking_data = json.loads(tracking_data)

    text = viber_request.message.text

    if text == 'menu':
        # Setting the possibility to write a comment
        reply_text = 'Выберите действие чтобы продолжить.'
        reply_keyboard = kb.MENU_KEYBOARD
        reply_rich_media = {
          "Type":"rich_media",
          "ButtonsGroupColumns":6,
          "ButtonsGroupRows":7,
          "BgColor":"#FFFFFF",
          "Buttons":[
             {
                "Columns":6,
                "Rows":3,
                "ActionType":"open-url",
                "ActionBody":"https://www.google.com",
                "Image":"http://html-test:8080/myweb/guy/assets/imageRMsmall2.png"
             },
             {
                "Columns":6,
                "Rows":2,
                "Text":"<font color=#323232><b>Headphones with Microphone, On-ear Wired earphones</b></font><font color=#777777><br>Sound Intone </font><font color=#6fc133>$17.99</font>",
                "ActionType":"open-url",
                "ActionBody":"https://www.google.com",
                "TextSize":"medium",
                "TextVAlign":"middle",
                "TextHAlign":"left"
             },
             {
                "Columns":6,
                "Rows":1,
                "ActionType":"reply",
                "ActionBody":"https://www.google.com",
                "Text":"<font color=#ffffff>Buy</font>",
                "TextSize":"large",
                "TextVAlign":"middle",
                "TextHAlign":"middle",
                "Image":"https://s14.postimg.org/4mmt4rw1t/Button.png"
             },
             {
                "Columns":6,
                "Rows":1,
                "ActionType":"reply",
                "ActionBody":"https://www.google.com",
                "Text":"<font color=#8367db>MORE DETAILS</font>",
                "TextSize":"small",
                "TextVAlign":"middle",
                "TextHAlign":"middle"
             }
          ]
       }
    # elif text[:5] == 'order':
    #     # Handling user selection of product, and dislpaying his choice
    #     ordered_item = text.split('-')[1]
    #     if 'order' in tracking_data:
    #         tracking_data['order'].append(ordered_item)
    #     else:
    #         tracking_data['order'] = [ordered_item]
    #     reply_text = f'Вы выбрали:\n{", ".join(tracking_data["order"])}\n\n'\
    #         'Если желаете выбрать что-нибудь еще, нажмите Меню. '\
    #         'Для продолжения, нажмите Оформить заказ.'
    #     reply_keyboard = kb.ORDER_COMFIRMATION_KEYBOARD
    # elif text == 'send_order':
    #     # Final step, sends all info to manager and resets tracking_data
    #     tracking_data['comment_mode'] = 'off'
    #     mesage_to_admin = "Новый заказ!\n"
    #     if tracking_data['name'] is not None:
    #         mesage_to_admin += f"Имя: {tracking_data['name']}\n"
    #     mesage_to_admin += f"Номер: {tracking_data['phone']}\n"\
    #                        f"Заказ: {', '.join(tracking_data['order'])}\n"\
    #                        f"Адрес: {tracking_data['location']}\n"
    #     if 'comment' in tracking_data:
    #         mesage_to_admin += f"Комментарий: {tracking_data['comment']}\n"
    #     viber.send_messages(ADMIN, TextMessage(text=mesage_to_admin))
    #     tracking_data['order'] = []
    #     tracking_data['location'] = ''
    #     tracking_data['comment'] = ''
    #     reply_text = 'Спасибо за заказ, менеджер в скором времени'\
    #                  ' свяжется с Вами.'
    #     reply_keyboard = kb.MENU_KEYBOARD
    else:
        reply_text = ''
        reply_keyboard = {}

    tracking_data = json.dumps(tracking_data)
    if reply_rich_media:

        reply = [RichMediaMessage(rich_media=reply_rich_media,
                         alt_text=reply_text,
                         tracking_data=tracking_data,
                         min_api_version=7)]
    else:
        reply = [TextMessage(text=reply_text,
                             keyboard=reply_keyboard,
                             tracking_data=tracking_data,
                             min_api_version=3)]
    viber.send_messages(viber_request.sender.id, reply)
