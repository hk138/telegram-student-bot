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

# تنظیم لاگ برای بررسی‌ها
logging.basicConfig(level=logging.INFO)

# متغیرهای محیطی
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = "https://telegram-student-bot-production.up.railway.app"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
ADMIN_CHAT_ID = 6899358433  # آیدی عددی مشاور

# اطلاعات کاربران
user_data = {}
questions = [
    "۱. پایه تحصیلی‌ت چیه؟ (دهم / یازدهم / دوازدهم)",
    "۲. رشته‌ت چیه؟ (ریاضی / تجربی / انسانی / هنر / زبان)",
    "۳. هدف‌ت برای کنکور چیه؟ (رتبه، رشته، دانشگاه)",
    "۴. در روز چند ساعت مطالعه می‌کنی؟",
    "۵. از چه منابعی استفاده می‌کنی؟",
    "۶. بیشتر در چه درس‌هایی ضعف داری؟",
    "۷. از چه روش‌هایی برای مرور استفاده می‌کنی؟",
    "۸. آزمون آزمایشی شرکت می‌کنی؟ (کدام؟)",
    "۹. چند ساعت در روز موبایل یا شبکه‌های اجتماعی استفاده می‌کنی؟",
    "۱۰. از نظر روحی چطور هستی؟ (انگیزه، استرس، خستگی)",
]

# شروع مشاوره
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 0, "answers": [], "done": False}
    await update.message.reply_text("سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟")
    await update.message.reply_text(questions[0])
    logging.info(f"✅ /start توسط کاربر {user_id}")

# هندل پیام‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    message = update.message.text
    logging.info(f"📨 پیام از {user_id}: {message}")

    if user_id not in user_data:
        await update.message.reply_text("لطفاً اول /start رو بزن 😊")
        return

    data = user_data[user_id]

    # اگر هنوز در حال پر کردن فرم هست
    if not data["done"]:
        data["answers"].append(message)
        data["step"] += 1

        if data["step"] < len(questions):
            await update.message.reply_text(questions[data["step"]])
        else:
            await update.message.reply_text("✅ مشاوره ثبت شد! منتظر پاسخ مشاور باش 🌟")
            answers_text = "\n".join(
                f"{i+1}. {q}\n➤ {a}" for i, (q, a) in enumerate(zip(questions, data["answers"]))
            )
            result = f"🆕 فرم جدید مشاوره:\n\n👤 آیدی کاربر: `{user_id}`\n\n{answers_text}"
            await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=result, parse_mode="Markdown")
            data["done"] = True
    else:
        # اگر فرم پر شده، پیام‌های بعدی رو برای مشاور بفرست
        msg = f"📩 پیام جدید از کاربر `{user_id}`:\n\n{message}"
        await context.bot.send_message(chat_id=ADMIN_CHAT_ID, text=msg, parse_mode="Markdown")

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

# اجرا
if __name__ == "__main__":
    asyncio.run(main())
