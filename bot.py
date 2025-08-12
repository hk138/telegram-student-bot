import os
import asyncio
import logging
from aiohttp import web
from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# لاگ برای دیباگ
logging.basicConfig(level=logging.INFO)

# متغیرهای محیطی
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = "https://telegram-student-bot-production.up.railway.app"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# ذخیره‌سازی اطلاعات کاربران
user_data = {}
questions = [
    "۱. پایه تحصیلی‌ت چیه؟ (دهم / یازدهم / دوازدهم)",
    "۲. رشته‌ت چیه؟ (ریاضی / تجربی / انسانی / هنر / زبان)",
    # می‌تونی سوالات بیشتر اضافه کنی
]

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 0, "answers": []}
    await update.message.reply_text("سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟")
    await update.message.reply_text(questions[0])
    logging.info(f"✅ /start توسط کاربر {user_id}")

# دریافت پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"📨 پیام دریافت شد از {user_id}: {update.message.text}")

    if user_id not in user_data:
        await update.message.reply_text("لطفاً اول /start رو بزن 😊")
        return

    data = user_data[user_id]
    data["answers"].append(update.message.text)
    data["step"] += 1

    if data["step"] < len(questions):
        await update.message.reply_text(questions[data["step"]])
    else:
        await update.message.reply_text("✅ مشاوره ثبت شد! منتظر پاسخ مشاور باش 🌟")
        logging.info(f"📋 پاسخ‌های {user_id}: {data['answers']}")
        del user_data[user_id]

# هندل وبهوک
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response()

# اجرای اصلی
async def main():
    global application

    application = ApplicationBuilder().token(TOKEN).build()

    # هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # تنظیم وبهوک
    await application.bot.set_webhook(WEBHOOK_URL)

    # سرور aiohttp برای Railway
    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5000)
    await site.start()

    print("✅ ربات فعال است و در حال دریافت پیام از Webhook...")

    # منتظر بمان
    await asyncio.Event().wait()

# اجرای برنامه
if __name__ == "__main__":
    asyncio.run(main())
