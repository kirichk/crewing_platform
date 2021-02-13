import json
from datetime import date
from django.conf import settings
from django.forms.models import model_to_dict
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.messages.rich_media_message import RichMediaMessage
from loguru import logger
from web_hiring.models import Post
from .resources import keyboards_content as kb
from .resources.tools import view_definer, model_text_details, model_transcriptor


logger.add('logs/info.log', format='{time} {level} {message}',
            level='INFO', rotation="1 MB", compression='zip')


@logger.catch
def user_message_handler(viber, viber_request):
    """Receiving a message from user and sending replies."""
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
        post_list = model_transcriptor(Post.objects.filter(
                                        publish_date__gte=date.today()))
        callback = text.split('-')
        if post_list:
            reply_text, reply_rich_media, reply_keyboard = view_definer(
                                                            post_list,
                                                            tracking_data,
                                                            callback,
                                                            'newday')
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
