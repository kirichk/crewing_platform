from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler, Updater,
                        MessageHandler, CommandHandler, ConversationHandler,
                        Filters)
from telegram.utils.request import Request
from tgbot.models import Profile
from tgbot.tele_handlers import (start_buttons_handler,phone_handler,
                                title_handler, clear_title_handler,
                                min_salary_handler, range_salary_handler,
                                reg_end, menu_handler, title_edit,
                                add_title_handler, remove_title_handler)
from loguru import logger


PHONE, SALARY_RANGE = range(2)
logger.add('info.log', format='{time} {level} {message}',
            level='DEBUG', rotation="1 MB", compression='zip')


@logger.catch
def do_echo(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    text = update.message.text

    p, _ = Profile.objects.get_or_create(
        external_id=chat_id,
        defaults={
            'name': update.message.from_user.username,
        }
    )
    p.save()

    reply_text = f'Ваш ID = {chat_id}\n{text}'
    update.message.reply_text(
        text=reply_text,
    )


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        # 1 -- правильное подключение
        req = Request(
            connect_timeout=30.0,
            read_timeout=1.0,
            con_pool_size=8,
        )
        bot = Bot(
            token=settings.TELE_TOKEN,
            request=req,
        )
        updater = Updater(
            bot=bot,
            use_context=True,
        )

        conv_handler = ConversationHandler(
            entry_points=[
                CommandHandler('start', start_buttons_handler),
                CommandHandler('menu', menu_handler),
                CallbackQueryHandler(title_handler,
                                        pattern=r'(title)',
                                        pass_user_data=True),
                CallbackQueryHandler(phone_handler,
                                        pattern=r'(tconfirm-add)',
                                        pass_user_data=True),
                CallbackQueryHandler(clear_title_handler,
                                        pattern=r'(tconfirm-rmv)',
                                        pass_user_data=True),
                CallbackQueryHandler(min_salary_handler,
                                        pattern=r'(tconfirm-next)',
                                        pass_user_data=True),
                CallbackQueryHandler(min_salary_handler,
                                        pattern=r'(srconfirm-edit)',
                                        pass_user_data=True),
                CallbackQueryHandler(reg_end,
                                        pattern=r'(srconfirm-next)',
                                        pass_user_data=True),
                CallbackQueryHandler(title_edit,
                                        pattern=r'(editt)',
                                        pass_user_data=True),
                CallbackQueryHandler(add_title_handler,
                                        pattern=r'(addt)',
                                        pass_user_data=True),
                CallbackQueryHandler(remove_title_handler,
                                        pattern=r'(rmvt)',
                                        pass_user_data=True),
            ],
            states={
                PHONE: [MessageHandler(Filters.all, phone_handler,
                                        pass_user_data=True),],
                SALARY_RANGE: [MessageHandler(Filters.all, range_salary_handler,
                                        pass_user_data=True),],
            },
            fallbacks=[
                CommandHandler('cancel', phone_handler),
            ],
        )
        updater.dispatcher.add_handler(conv_handler)
        updater.dispatcher.add_handler(MessageHandler(Filters.all, do_echo))

        # 3 -- запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()
