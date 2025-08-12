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

# تنظیم لاگ برای دیباگ
logging.basicConfig(level=logging.INFO)

# تنظیمات Webhook
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_HOST = "https://telegram-student-bot-production.up.railway.app"
WEBHOOK_PATH = "/webhook"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# سراسری
application = None
user_data = {}

# ✅ سوالات کامل
questions = [
    "۱. پایه تحصیلی‌ت چیه؟ (دهم / یازدهم / دوازدهم)",
    "۲. رشته‌ت چیه؟ (ریاضی / تجربی / انسانی / هنر / زبان)",
    "۳. معدل سال قبلت چقدر بود؟",
    "۴. مدرسه‌ت چه نوعیه؟ (دولتی / نمونه / تیزهوشان / غیرانتفاعی)",
    "۵. در چه دروسی قوی‌تر هستی؟",
    "۶. در چه دروسی ضعیف‌تری؟",
    "۷. هدفت برای کنکور چیه؟ (رشته و دانشگاه)",
    "۸. روزانه چند ساعت درس می‌خونی؟",
    "۹. تایم آزاد دیگه‌ت چقدر هست؟",
    "۱۰. از چه منابع کمک‌آموزشی استفاده می‌کنی؟",
    "۱۱. مشاور یا برنامه‌ریزی خاصی تا حالا داشتی؟",
    "۱۲. نقاط قوتت توی درس خوندن چیه؟",
    "۱۳. به نظرت بزرگترین چالش در مسیر درس خوندن‌ت چیه؟",
    "۱۴. آیا به کلاس‌های آنلاین یا حضوری علاقه داری؟",
    "۱۵. سبک یادگیری‌ت چطوریه؟ (دیداری / شنیداری / عملی)",
    "۱۶. می‌خوای چند ساعت در روز مشاوره یا پیگیری داشته باشی؟",
    "۱۷. آیا از اپلیکیشن یا دفتر برنامه‌ریزی استفاده می‌کنی؟",
    "۱۸. انتظارت از مشاور چیه؟",
    "۱۹. مورد خاص دیگه‌ای هست که دوست داری مشاور بدونه؟",
]

# شروع ربات
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 0, "answers": []}
    await update.message.reply_text("سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟")
    await update.message.reply_text(questions[0])
    logging.info(f"✅ /start توسط کاربر {user_id}")

# مدیریت پاسخ‌ها
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logging.info(f"📨 پیام از {user_id}: {update.message.text}")

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

# هندل Webhook
async def handle_webhook(request):
    try:
        data = await request.json()
        update = Update.de_json(data, application.bot)
        await application.process_update(update)
        return web.Response(text="OK")
    except Exception as e:
        logging.error(f"❌ خطا در Webhook: {e}")
        import traceback
        traceback.print_exc()
        return web.Response(status=500, text="Internal Server Error")

# تابع اصلی
async def main():
    global application

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.initialize()
    await application.bot.set_webhook(WEBHOOK_URL)
    print(f"📡 Webhook تنظیم شد: {WEBHOOK_URL}")

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
