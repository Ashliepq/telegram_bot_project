from telegram import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton, Update
)
from telegram.ext import CallbackContext
import db, config


def send_phone_request(update: Update, context: CallbackContext):
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton("📱 ارسال شماره من", request_contact=True)]],
        resize_keyboard=True, one_time_keyboard=True
    )
    update.message.reply_text("لطفاً شماره موبایل‌تون رو ارسال کنید:", reply_markup=kb)


def contact_handler(update: Update, context: CallbackContext):
    contact = update.message.contact
    if contact:
        db.update_user_phone(contact.user_id, contact.phone_number)
        update.message.reply_text("✅ شماره شما ثبت شد. منتظر پیام‌های ادمین باشید.", reply_markup=None)


def admin_panel(update: Update, context: CallbackContext):
    buttons = [
        [InlineKeyboardButton("📤 ارسال پیام همگانی", callback_data="broadcast")],
        [InlineKeyboardButton("🗑️ حذف پست‌ها", callback_data="delete_post")],
        [InlineKeyboardButton("📋 لیست کاربران", callback_data="list_users")]
    ]
    kb = InlineKeyboardMarkup(buttons)
    update.message.reply_text("🔧 پنل مدیریت:", reply_markup=kb)


def callback_handler(update: Update, context: CallbackContext):
    query = update.callback_query
    user_id = query.from_user.id

    if not db.is_admin(user_id):
        query.answer("شما ادمین نیستید.")
        return

    if query.data == "broadcast":
        context.bot.send_message(chat_id=user_id, text="پیام متنی یا مدیای خود را بفرستید.")
        context.user_data["awaiting_broadcast"] = True

    elif query.data == "delete_post":
        posts = db.get_all_posts()
        for post in posts:
            btn = InlineKeyboardMarkup(
                [[InlineKeyboardButton("❌ حذف", callback_data=f"del_{post[0]}")]]
            )
            context.bot.send_message(chat_id=user_id, text=post[3] or "بدون متن", reply_markup=btn)

    elif query.data == "list_users":
        users = db.get_all_users()
        context.bot.send_message(chat_id=user_id, text=f"📌 تعداد کاربران ثبت‌شده: {len(users)}")


def broadcast_handler(update: Update, context: CallbackContext):
    if context.user_data.get("awaiting_broadcast"):
        context.user_data["awaiting_broadcast"] = False

        all_users = db.get_all_users()

        post_type = None
        file_id = None
        caption = update.message.caption or update.message.text

        if update.message.text:
            post_type = "text"
        elif update.message.photo:
            post_type = "photo"
            file_id = update.message.photo[-1].file_id
        elif update.message.video:
            post_type = "video"
            file_id = update.message.video.file_id
        elif update.message.document:
            post_type = "document"
            file_id = update.message.document.file_id
        else:
            update.message.reply_text("❌ فرمت پشتیبانی‌نشده است.")
            return

        db.save_post(post_type, file_id, caption)

        for uid in all_users:
            try:
                if post_type == "text":
                    context.bot.send_message(chat_id=uid, text=caption)
                elif post_type == "photo":
                    context.bot.send_photo(chat_id=uid, photo=file_id, caption=caption)
                elif post_type == "video":
                    context.bot.send_video(chat_id=uid, video=file_id, caption=caption)
                elif post_type == "document":
                    context.bot.send_document(chat_id=uid, document=file_id, caption=caption)
            except:
                pass

        update.message.reply_text("✅ پیام همگانی با موفقیت ارسال شد.")


def delete_post_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    if query.data.startswith("del_"):
        post_id = int(query.data.split("_")[1])
        db.delete_post(post_id)
        query.edit_message_text("✅ پست حذف شد.")
