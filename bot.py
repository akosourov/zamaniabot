import logging


import telegram as tg
from telegram import ext as tg_ext
import config
import models


logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('zamaniabot')


bot = tg.Bot(token=config.bot_token)


def process_update(update_raw):
    update = tg.Update.de_json(update_raw, bot)
    dispatcher.process_update(update)


def error_handler(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))


def message_handler(bot, update):
    user_id = update.message.from_user.id
    incomplete_feedback = models.FeedBack.query.filter_by(user_id=user_id,
                                                          is_incomplete=True).first()
    if incomplete_feedback:
        feedback_text = update.message.text
        incomplete_feedback.text = feedback_text
        incomplete_feedback.is_incomplete = False
        models.db.session.add(incomplete_feedback)
        models.db.session.commit()
        update.message.reply_text('Ваш отзыв `{}` отправлен'.format(feedback_text))
    else:
        start_cmd(bot, update)


def start_cmd(bot, update):
    tg_user = update.message.from_user
    app_user = models.User.query.get(tg_user.id)
    if not app_user:
        is_admin = tg_user.username in config.admin_username_list
        app_user = models.User(id=tg_user.id, first_name=tg_user.first_name,
                               last_name=tg_user.last_name, username=tg_user.username,
                               is_admin=is_admin)
        models.db.session.add(app_user)
        models.db.session.commit()

    reply_markup = tg.InlineKeyboardMarkup([
        [tg.InlineKeyboardButton('Оставить отзыв', callback_data='feedback')]
    ])
    update.message.reply_text('Добро пожаловать!', reply_markup=reply_markup)


def callback_handler(bot, update):
    callback_query = update.callback_query
    callback_data = callback_query.data
    if callback_data == 'feedback':
        user_id = callback_query.from_user.id
        feedback = models.FeedBack(user_id=user_id, is_incomplete=True)
        models.db.session.add(feedback)
        models.db.session.commit()
        update.callback_query.message.reply_text('Напишите сообщением ваш отзыв...')
    update.callback_query.answer()


def registry_handlers(dispatcher):
    dispatcher.add_handler(tg_ext.CommandHandler('start', start_cmd))
    dispatcher.add_handler(tg_ext.MessageHandler(tg_ext.Filters.text, message_handler))
    dispatcher.add_handler(tg_ext.CallbackQueryHandler(callback_handler))
    dispatcher.add_error_handler(error_handler)


if config.polling_debug:
    updater = tg_ext.Updater(token=config.bot_token)
    registry_handlers(updater.dispatcher)
    updater.start_polling()
    # updater.idle()
else:
    dispatcher = tg_ext.Dispatcher(bot, None, workers=0)
    registry_handlers(dispatcher)

