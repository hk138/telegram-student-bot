import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

import openai
import os

# ست کردن توکن‌های مورد نیاز
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "توکن رباتت اینجا")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "توکن OpenAI اینجا")
openai.api_key = OPENAI_API_KEY

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# پیام شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! به ربات مشاور کنکور خوش اومدی. سوالاتت رو بپرس یا شروع کن تا راهنمایی‌ات کنم.")

# پیام متنی از کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    await update.message.reply_text("در حال فکر کردن روی پاسخ...")

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "تو یک مشاور کنکور دلسوز و دقیق هستی که به دانش‌آموزان کمک می‌کنی تا بهترین نتیجه را بگیرند."},
                {"role": "user", "content": user_message}
            ]
        )
        reply = response.choices[0].message.content.strip()
        await update.message.reply_text(reply)
    except Exception as e:
        logger.error(f"خطا در دریافت پاسخ از OpenAI: {e}")
        await update.message.reply_text("متأسفم، مشکلی در ارتباط با ChatGPT پیش اومد.")

# اجرا
if __name__ == "__main__":
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات اجرا شد.")
    app.run_polling()