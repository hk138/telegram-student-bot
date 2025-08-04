from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from telegram import Update
import logging

# فعال‌سازی لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن بات تلگرام
TOKEN = "توکن_بات_تو"

# سوالات مرحله مشاوره
questions = [
    "۱. پایه تحصیلی شما؟",
    "۲. رشته شما چیه؟",
    "۳. هدفت چیه؟ (کنکور / نهایی / هر دو)",
    "۴. روزانه چقدر درس می‌خونی؟ (۱ تا ۳، ۳ تا ۵، ۵ تا ۷، ۷ تا ۹، ۹ تا ۱۱، بیشتر از ۱۱)",
    "۵. دنبال چی هستی؟ (برنامه‌ریزی درسی اختصاصی / صحبت با مشاور)",
    "۶. به نظرت نقطه قوتت چیه؟",
    "۷. به نظرت نقطه ضعفت چیه؟",
    "۸. چرا بعضی وقتا حس درس خوندن نداری؟",
    "۹. توی آزمونی شرکت می‌کنی؟ کدوم؟",
    "۱۰. آخرین نتیجه آزمونت (تراز / رتبه) چی بوده؟",
    "۱۱. چه روش یادگیری رو ترجیح می‌دی؟ (مطالعه / ویدیو)",
    "۱۲. چه رشته‌ای دوست داری قبول شی؟",
    "۱۳. کدوم دانشگاه رو دوست داری قبول شی؟",
    "۱۴. صبحا سرحال‌تری یا شب‌ها؟",
    "۱۵. منابعی که داری رو بنویس (مثلاً: شیمی خیلی سبز، ریاضی مهر و ماه و ...)"
]

# اطلاعات کاربران
user_states = {}
user_answers = {}

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_states[chat_id] = 0
    user_answers[chat_id] = []
    context.bot.send_message(chat_id=chat_id, text="سلام! بیاین مشاوره رو شروع کنیم 🙂\n\n" + questions[0])

def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = update.message.text

    if chat_id in user_states:
        q_index = user_states[chat_id]
        if q_index < len(questions):
            user_answers[chat_id].append(text)
            user_states[chat_id] += 1
            if user_states[chat_id] < len(questions):
                context.bot.send_message(chat_id=chat_id, text=questions[user_states[chat_id]])
            else:
                summary = "\n\n📋 پاسخ‌هات:\n" + "\n".join([
                    f"{questions[i]} \n➤ {user_answers[chat_id][i]}" for i in range(len(questions))
                ])
                context.bot.send_message(chat_id=chat_id, text="✅ گفت‌وگو تموم شد. " + summary)
        else:
            context.bot.send_message(chat_id=chat_id, text="✅ اطلاعات شما قبلاً ثبت شده.")
    else:
        context.bot.send_message(chat_id=chat_id, text="برای شروع، لطفاً /start رو بزنید.")

def main():
    updater = Updater(TOKEN)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
