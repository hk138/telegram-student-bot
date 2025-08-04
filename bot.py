import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler,
    MessageHandler, ContextTypes, filters, ConversationHandler
)
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

ASKING, = range(1)

QUESTIONS = [
    "در چه پایه‌ای تحصیل می‌کنی؟",
    "هدفت از کنکور چیه؟",
    "چند ساعت در روز مطالعه می‌کنی؟",
    "نقطه ضعفت چیه؟",
    "نقطه قوتت چیه؟",
    "علت اینکه بعضی اوقات حس درس خوندن نداری چیه؟",
    "آزمون خاصی شرکت می‌کنی؟",
    "آخرین نتیجه آزمونت چی بوده؟ تراز یا رتبه؟",
    "چه روش یادگیری رو ترجیح میدی؟ (مطالعه، دیدن ویدیو)",
    "چه رشته‌ای دوست داری قبول بشی؟",
    "چه دانشگاهی مد نظرت هست؟",
    "صبح‌ها بیشتر سرحالی یا شب‌ها؟",
    "چه منابعی برای هر درس داری؟"
]

user_answers = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_answers[user_id] = []
    context.user_data["q_index"] = 0
    await update.message.reply_text("سلام! وقت بخیر 👋\nقراره چند تا سؤال ازت بپرسم...")
    await update.message.reply_text(QUESTIONS[0])
    return ASKING

async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    answer = update.message.text
    user_answers[user_id].append(answer)
    q_index = context.user_data["q_index"] + 1
    context.user_data["q_index"] = q_index

    if q_index < len(QUESTIONS):
        await update.message.reply_text(QUESTIONS[q_index])
        return ASKING
    else:
        await update.message.reply_text("ممنون! اطلاعاتت ثبت شد. در حال تحلیل پاسخ‌هات هستم...")
        # اینجا میشه پاسخ‌ها رو برای تحلیل به API فرستاد
        return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مکالمه لغو شد.")
    return ConversationHandler.END

def main():
    token = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(token).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={ASKING: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)]},
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()

    return "Student Bot is running."

# اجرای اپلیکیشن Flask (برای اجرا در local یا debug لازم نیست)
if __name__ == "__main__":
    app.run()
