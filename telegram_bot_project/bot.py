from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
import db, config
import handlers

def start(update, context):
    user = update.message.from_user
    full_name = f"{user.first_name or ''} {user.last_name or ''}".strip()
    db.add_user(user.id, full_name)
    handlers.send_phone_request(update, context)

def main():
    db.init_db()

    updater = Updater(config.BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("admin", handlers.admin_panel))
    dp.add_handler(CallbackQueryHandler(handlers.callback_handler))
    dp.add_handler(CallbackQueryHandler(handlers.delete_post_callback, pattern=r"^del_\d+"))

    dp.add_handler(MessageHandler(Filters.all & Filters.user(user_id=config.ADMINS), handlers.broadcast_handler))

    dp.add_handler(MessageHandler(Filters.contact, handlers.contact_handler))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
