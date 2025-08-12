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

# تنظیم لاگ‌ها
logging.basicConfig(level=logging.INFO)

# توکن و وبهوک
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = "https://telegram-student-bot-production.up.railway.app"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# آیدی عددی مشاور (سوپرگروه یا چت خصوصی)
ADVISOR_CHAT_ID = 6899358433

# دیتای کاربران و سوال‌ها
user_data = {}
questions = [
    "۱. پایه تحصیلی‌ت چیه؟ (دهم / یازدهم / دوازدهم)",
    "۲. رشته‌ت چیه؟ (ریاضی / تجربی / انسانی / هنر / زبان)",
    "۳. معدل سال قبلت چنده؟",
    "۴. روزی چند ساعت درس می‌خونی؟",
    "۵. چه درس‌هایی برات سخته؟",
    "۶. چه درس‌هایی رو دوست داری؟",
    "۷. مشاوره قبلاً داشتی؟ (بله / خیر)",
    "۸. منبع درسی خاصی استفاده می‌کنی؟",
    "۹. برنامه خاصی برای کنکور داری؟",
    "۱۰. دوست داری چجوری راهنمایی‌ت کنیم؟",
]

# شروع گفتگو
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    full_name = update.effective_user.full_name
    user_data[user_id] = {"step": 0, "answers": [], "name": full_name}
    await update.message.reply_text("سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟")
    await update.message.reply_text(questions[0])
    logging.info(f"✅ /start توسط کاربر {user_id} ({full_name})")

# پاسخ‌دهی به سوال‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text

    if user_id not in user_data:
        await update.message.reply_text("لطفاً اول /start رو بزن 😊")
        return

    data = user_data[user_id]
    data["answers"].append(message)
    data["step"] += 1

    if data["step"] < len(questions):
        await update.message.reply_text(questions[data["step"]])
    else:
        await update.message.reply_text("✅ مشاوره ثبت شد! منتظر پاسخ مشاور باش 🌟")

        # ارسال پیام به مشاور
        full_name = data["name"]
        answers = data["answers"]
        msg = f"📥 مشاوره جدید از {full_name} (ID: {user_id}):\n\n"
        for i, q in enumerate(questions):
            msg += f"{q}\n📝 {answers[i]}\n\n"
        await context.bot.send_message(chat_id=ADVISOR_CHAT_ID, text=msg)

        logging.info(f"📋 پاسخ‌های {user_id}: {answers}")
        del user_data[user_id]

# هندل وبهوک
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()  # نیاز به initialize در ورژن جدید
    await application.process_update(update)
    return web.Response()

# تابع اصلی
async def main():
    global application
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.bot.set_webhook(WEBHOOK_URL)

    app = web.Application()
    app.router.add_post(WEBHOOK_PATH, handle_webhook)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", 5000)
    await site.start()

    print("✅ ربات فعال است و در حال دریافت پیام از Webhook...")
    await asyncio.Event().wait()

if __name__ == "__main__":
    asyncio.run(main())
