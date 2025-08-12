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

# تنظیمات لاگ
logging.basicConfig(level=logging.INFO)

# توکن ربات و اطلاعات Webhook
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = "https://telegram-student-bot-production.up.railway.app"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# آیدی عددی گروه مشاور
ADVISOR_CHAT_ID = 6899358433

# اطلاعات کاربران و سوالات
user_data = {}
questions = [
    "۱. پایه تحصیلی‌ت چیه؟ (دهم / یازدهم / دوازدهم)",
    "۲. رشته‌ت چیه؟ (ریاضی / تجربی / انسانی / هنر / زبان)",
    "۳. سطح درس‌هات در حال حاضر چطوره؟ (ضعیف / متوسط / قوی)",
    "۴. روزی چند ساعت مطالعه می‌کنی؟",
    "۵. بیشتر با چه درسی مشکل داری؟",
    "۶. هدف اصلی‌ت از مشاوره چیه؟",
    "۷. چند ساعت گوشی استفاده می‌کنی در روز؟",
    "۸. آزمون خاصی شرکت می‌کنی؟ (قلمچی / گزینه۲ / بدون آزمون)",
    "۹. آیا کلاس یا معلم خصوصی هم داری؟",
    "۱۰. چند ساعت وقت آزاد واقعی در روز داری برای درس خوندن؟",
]

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 0, "answers": []}
    await update.message.reply_text("سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟")
    await update.message.reply_text(questions[0])
    logging.info(f"✅ /start توسط کاربر {user_id}")

# هندل پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    text = update.message.text
    logging.info(f"📨 پیام از {user_id}: {text}")

    if user_id not in user_data:
        await update.message.reply_text("لطفاً اول /start رو بزن 😊")
        return

    data = user_data[user_id]
    data["answers"].append(text)
    data["step"] += 1

    if data["step"] < len(questions):
        await update.message.reply_text(questions[data["step"]])
    else:
        await update.message.reply_text("✅ مشاوره ثبت شد! منتظر پاسخ مشاور باش 🌟")

        # ارسال پاسخ‌ها برای مشاور
        message = f"📋 پاسخ‌های کاربر {user_id}:\n\n"
        for i, q in enumerate(questions):
            message += f"{q}\n➖ {data['answers'][i]}\n\n"

        await context.bot.send_message(chat_id=ADVISOR_CHAT_ID, text=message)
        user_data[user_id] = {"step": len(questions), "answers": data["answers"]}

# بعد از اتمام فرم، هر پیام جدید هم برای مشاور ارسال می‌شود
async def forward_to_advisor(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id in user_data and user_data[user_id]["step"] == len(questions):
        msg = f"📨 پیام جدید از {user_id}:\n{update.message.text}"
        await context.bot.send_message(chat_id=ADVISOR_CHAT_ID, text=msg)

# هندل Webhook
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.process_update(update)
    return web.Response()

# اجرای برنامه
async def main():
    global application

    application = ApplicationBuilder().token(TOKEN).build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, forward_to_advisor))

    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)

    # راه‌اندازی سرور aiohttp
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
