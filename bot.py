import os
import asyncpg
import asyncio
from telegram import Update, Bot
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters
)

# --- تنظیمات ---
TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_FORUM_ID = os.getenv("ADMIN_FORUM_ID")
WEBHOOK_URL = "https://telegram-student-bot-production.up.railway.app"

user_data = {}

# --- سوالات ---
questions = [
    "۱. پایه تحصیلی‌ت چیه؟ (دهم / یازدهم / دوازدهم)",
    "۲. رشته‌ت چیه؟ (ریاضی / تجربی / انسانی / هنر / زبان)",
    # ... ادامه سوال‌ها ...
]

# --- هندلرها ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 0, "answers": []}
    await update.message.reply_text("سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟")
    await update.message.reply_text(questions[0])

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("لطفاً اول /start رو بزن 😊")
        return

    data = user_data[user_id]
    data["answers"].append(update.message.text)
    data["step"] += 1

    if data["step"] < len(questions):
        await update.message.reply_text(questions[data["step"]])
    else:
        await update.message.reply_text("✅ مشاوره ثبت شد! در حال ارسال اطلاعات به مشاور...")

        summary = "\n".join(
            f"{i + 1}. {questions[i]}\n➤ {ans}" for i, ans in enumerate(data["answers"])
        )

        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 مشاوره جدید:\n{summary}")
        await context.bot.send_message(chat_id=ADMIN_FORUM_ID, text=summary)

        del user_data[user_id]

# --- ساخت و اجرای اپلیکیشن ---
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    await app.bot.set_webhook(WEBHOOK_URL + "/webhook")

    print("✅ ربات فعال است و Webhook تنظیم شد...")

    await app.run_webhook(
        listen="0.0.0.0",
        port=5000,
        url_path="/webhook",
    )

# --- اجرای بدون استفاده از asyncio.run ---
if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.create_task(main())
    loop.run_forever()
