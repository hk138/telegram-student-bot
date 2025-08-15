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

# آیدی عددی مشاور
ADVISOR_CHAT_ID = 7796471908

# ذخیره‌سازی اطلاعات کاربران
user_data = {}
questions = [
    "سلام ! نام و نام خانوادگی؟ ",
    "پایه تحصیلی‌ات چیه؟ (دهم، یازدهم، دوازدهم)",
    "چه رشته ای هستی؟",
    "چند ساعت در روز درس می‌خونی؟",
    "نقاط قوتت چیه؟",
    "نقاط ضعفت چیه؟",
    "چرا بعضی وقتا حس درس خوندن نداری؟",
    "آزمون خاصی شرکت می‌کنی؟ (قلمچی، گزینه دو...)",
    "آخرین نتیجه آزمونت چطور بود؟ (تراز، رتبه... اگه داشتی)",
    "آیا برنامه خاصی تا الآن استفاده میکردی؟ ( مثلا با برنامه آزمون هات پیش میرفتی)",
    "الان در چه موقعیتی هستی؟(مثلا دهم  یازدهم دوازدهم رو تا چه حد بلدی ، مرور کردی یا نه)",
    "چه روش یادگیری رو ترجیح می‌دی؟ (مطالعه، دیدن ویدیو...)",
    "به چه رشته‌ای علاقه‌مندی؟",
    "دوست داری کدوم دانشگاه قبول بشی؟",
    "صبح‌ها یا شب‌ها انرژی بیشتری برای درس داری؟",
    "منابعی که داری رو کامل بنویس (مثلاً برای ریاضی مهر و ماه، برای شیمی خیلی سبز...)"
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
    message = update.message.text
    logging.info(f"📨 پیام از {user_id}: {message}")

    if user_id not in user_data:
        await update.message.reply_text("لطفاً اول /start رو بزن 😊")
        return

    data = user_data[user_id]
    data["answers"].append(message)
    data["step"] += 1

    if data["step"] < len(questions):
        await update.message.reply_text(questions[data["step"]])
    else:
        summary = f"📥 پاسخ‌های جدید از کاربر {user_id}:\n"
        for i, answer in enumerate(data["answers"]):
            summary += f"{i+1}. {questions[i]}\nپاسخ: {answer}\n\n"
        await context.bot.send_message(chat_id=ADVISOR_CHAT_ID, text=summary)
        await update.message.reply_text("✅ پاسخ‌ها ثبت شد. لطفاً به آیدی @Daneshgosho پیام \"سلام\" بده تا مشاوره‌ت بررسی بشه. نتیجه پس از چند ساعت آماده خواهد بود 🌟")
        del user_data[user_id]

# هندل وبهوک
async def handle_webhook(request):
    data = await request.json()
    update = Update.de_json(data, application.bot)
    await application.initialize()
    await application.process_update(update)
    return web.Response()

# اجرای اصلی
async def main():
    global application

    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await application.initialize()
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
