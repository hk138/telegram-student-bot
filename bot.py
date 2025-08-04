import logging
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

questions = [
    "سلام! پایه تحصیلی‌ات چیه؟ (دهم، یازدهم، دوازدهم)",
    "هدفت از درس خوندن چیه؟",
    "چند ساعت در روز درس می‌خونی؟",
    "نقاط قوتت چیه؟",
    "نقاط ضعفت چیه؟",
    "چرا بعضی وقتا حس درس خوندن نداری؟",
    "آزمون خاصی شرکت می‌کنی؟ (قلمچی، گزینه دو...)",
    "آخرین نتیجه آزمونت چطور بود؟ (تراز، رتبه... اگه داشتی)",
    "چه روش یادگیری رو ترجیح می‌دی؟ (مطالعه، دیدن ویدیو...)",
    "به چه رشته‌ای علاقه‌مندی؟",
    "دوست داری کدوم دانشگاه قبول بشی؟",
    "صبح‌ها یا شب‌ها انرژی بیشتری برای درس داری؟",
    "منابعی که داری رو کامل بنویس (مثلاً برای ریاضی مهر و ماه، برای شیمی خیلی سبز...)"
]

user_states = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    user_states[user_id] = {"step": 0, "answers": []}
    await update.message.reply_text(questions[0])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    if user_id not in user_states:
        await update.message.reply_text("لطفاً اول دستور /start رو بزن.")
        return

    state = user_states[user_id]
    state["answers"].append(update.message.text)
    state["step"] += 1

    if state["step"] < len(questions):
        await update.message.reply_text(questions[state["step"]])
    else:
        summary = "\n".join(f"{i+1}. {a}" for i, a in enumerate(state["answers"]))
        await update.message.reply_text("✅ ممنون! پاسخ‌هات ثبت شد:\n\n" + summary)
        del user_states[user_id]

async def health_check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Student Bot is running.")

def main():
    application = ApplicationBuilder().token("8117664156:AAFdfRxZ-7t0qXdQ_FUrcBbC7dY23Xs5BFw").build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("ping", health_check))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    application.run_polling()

if __name__ == "__main__":
    main()
