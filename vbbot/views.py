from django.shortcuts import HttpResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from viberbot import Api
from viberbot.api.bot_configuration import BotConfiguration
from viberbot.api.messages.text_message import TextMessage
from viberbot.api.viber_requests import (ViberFailedRequest,
                                         ViberConversationStartedRequest,
                                         ViberMessageRequest,
                                         ViberSubscribedRequest)
from .handlers import user_message_handler
from .resources import texts
from .resources import keyboards_content as kb
from loguru import logger


logger.add('info.log', format='{time} {level} {message}',
            level='INFO', rotation="1 MB", compression='zip')

viber = Api(BotConfiguration(
    name='TopCrew',
    avatar='https://i.imgur.com/xVxrShr.jpg',
    auth_token=settings.VIBER_TOKEN
))

@csrf_exempt
def viber_app(request):
    """Catching all requests to bot and defining the request type."""
    if not viber.verify_signature(
                        request.body,
                        request.headers.get('X-Viber-Content-Signature')):
        return HttpResponse(status=403)
    viber_request = viber.parse_request(request.body)
    # Defining type of the request and replying to it
    if isinstance(viber_request, ViberMessageRequest):
        # Passing any message from user to message handler in handlers.py
        user_message_handler(viber, viber_request)
    elif isinstance(viber_request, ViberSubscribedRequest):
        viber.send_messages(viber_request.user.id, [
            TextMessage(text="Спасибо за подписку!")
        ])
    elif isinstance(viber_request, ViberFailedRequest):
        logger.warn("client failed receiving message. failure: {0}"
                    .format(viber_request))
    elif isinstance(viber_request, ViberConversationStartedRequest):
        # First touch, sending to user keyboard with phone sharing button
        keyboard = kb.GO_TO_MENU_KEYBOARD
        viber.send_messages(viber_request.user.id, [
            TextMessage(
                text=texts.GREETING,
                keyboard=keyboard,
                min_api_version=3)]
        )
    return HttpResponse(status=200)
