from django.core.management.base import BaseCommand
from django.conf import settings
from telegram import Bot, Update
from telegram.ext import (CallbackContext, CallbackQueryHandler, Updater,
                        MessageHandler, CommandHandler, ConversationHandler,
                        Filters)
from telegram.utils.request import Request
from tgbot.models import Profile
from tgbot.tele_handlers import (start_buttons_handler,new_handler,
                                newday_handler, newweek_handler,
                                profile_handler,  profile_edit_handler,
                                profile_delete_handler,
                                title_handler, title_choose_handler,
                                salary_handler, fleet_handler,
                                fleet_choose_handler, contract_handler,
                                crew_handler, date_handler, newsletter_handler,
                                email_question_handler, email_confirmer_handler,
                                email_handler, success_handler, filter_handler,
                                detail_handler, searchfilter_handler,
                                searchsubscription_handler)
from loguru import logger


CALENDAR, CALENDAR_SELECTOR, EDIT, FILTER, EMAIL_CONFIRM = range(5)
logger.add('info.log', format='{time} {level} {message}',
            level='INFO', rotation="1 MB", compression='zip')


class Command(BaseCommand):
    help = 'Телеграм-бот'

    def handle(self, *args, **options):
        # 1 -- правильное подключение
        req = Request(
            connect_timeout=30.0,
            read_timeout=15.0,
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
                CommandHandler('menu', start_buttons_handler),
                CallbackQueryHandler(start_buttons_handler,
                                        pattern=r'^start$',
                                        pass_user_data=True),
                CallbackQueryHandler(searchfilter_handler,
                                        pattern=r'^searchfilter',
                                        pass_user_data=True),
                CallbackQueryHandler(searchsubscription_handler,
                                        pattern=r'^searchsubscription',
                                        pass_user_data=True),
                CallbackQueryHandler(detail_handler,
                                        pattern=r'^detail',
                                        pass_user_data=True),
                CallbackQueryHandler(new_handler,
                                        pattern=r'^new$',
                                        pass_user_data=True),
                CallbackQueryHandler(newsletter_handler,
                                        pattern=r'^newsletter',
                                        pass_user_data=True),
                CallbackQueryHandler(filter_handler,
                                        pattern=r'^filter',
                                        pass_user_data=True),
                CallbackQueryHandler(profile_handler,
                                        pattern=r'^profile$',
                                        pass_user_data=True),
                CallbackQueryHandler(profile_edit_handler,
                                        pattern=r'^profileedit',
                                        pass_user_data=True),
                CallbackQueryHandler(profile_delete_handler,
                                        pattern=r'^profiledelete$',
                                        pass_user_data=True),
                CallbackQueryHandler(newweek_handler,
                                        pattern=r'^newweek',
                                        pass_user_data=True),
                CallbackQueryHandler(newday_handler,
                                        pattern=r'^newday',
                                        pass_user_data=True),
                CallbackQueryHandler(title_handler,
                                        pattern=r'^title',
                                        pass_user_data=True),
                CallbackQueryHandler(title_choose_handler,
                                        pattern=r'^choicetitle',
                                        pass_user_data=True),
                CallbackQueryHandler(salary_handler,
                                        pattern=r'^salary',
                                        pass_user_data=True),
                CallbackQueryHandler(fleet_handler,
                                        pattern=r'^fleet',
                                        pass_user_data=True),
                CallbackQueryHandler(vessel_handler,
                                        pattern=r'^vessel',
                                        pass_user_data=True),
                CallbackQueryHandler(fleet_choose_handler,
                                        pattern=r'^choicefleet',
                                        pass_user_data=True),
                CallbackQueryHandler(contract_handler,
                                        pattern=r'^contract',
                                        pass_user_data=True),
                CallbackQueryHandler(crew_handler,
                                        pattern=r'^crew',
                                        pass_user_data=True),
                CallbackQueryHandler(date_handler,
                                        pattern=r'^date',
                                        pass_user_data=True),
                CallbackQueryHandler(email_handler,
                                        pattern=r'^email$',
                                        pass_user_data=True),
                CallbackQueryHandler(success_handler,
                                        pattern=r'^success_registration$',
                                        pass_user_data=True),
            ],
            states={
                CALENDAR_SELECTOR: [CallbackQueryHandler(date_handler,
                                        pass_user_data=True)],
                CALENDAR: [CallbackQueryHandler(email_question_handler,
                                        pass_user_data=True)],
                EDIT: [CallbackQueryHandler(profile_edit_handler,
                                        pass_user_data=True)],
                EMAIL_CONFIRM: [MessageHandler(Filters.all, email_confirmer_handler,
                                        pass_user_data=True),],
                FILTER: [CallbackQueryHandler(filter_handler,
                                        pass_user_data=True)],
            },
            fallbacks=[
                CommandHandler('cancel', start_buttons_handler),
            ],
        )
        updater.dispatcher.add_handler(conv_handler)
        updater.dispatcher.add_handler(MessageHandler(Filters.all, start_buttons_handler))

        # 3 -- запустить бесконечную обработку входящих сообщений
        updater.start_polling()
        updater.idle()
