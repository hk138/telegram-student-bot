import logging
import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Filters, CallbackContext
import openai

# راه‌اندازی لاگ
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# گرفتن توکن‌ها از متغیر محیطی
BOT_TOKEN = os.getenv("BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# مقداردهی اولیه
bot = Bot(token=BOT_TOKEN)
app = Flask(__name__)
dispatcher = Dispatcher(bot, None, workers=0)

# اتصال به OpenAI
openai.api_key = OPENAI_API_KEY

# سوالات مشاوره‌ای مرحله‌ای
questions = [
    "در چه پایه‌ای هستی؟ (دهم / یازدهم / دوازدهم)",
    "هدفت از درس خوندن چیه؟",
    "چند ساعت در روز درس می‌خونی؟",
    "قوی‌ترین درس‌هات کدوما هستن؟",
    "ضعیف‌ترین درس‌هات کدوما هستن؟",
    "به نظرت نقطه قوتت چیه؟",
    "به نظرت نقطه ضعفت چیه؟",
    "چرا بعضی وقتا حس درس خوندن نداری؟",
    "آزمون خاصی شرکت می‌کنی؟ اگه آره، اسمش؟",
    "آخرین رتبه یا تراز آزمونت چی بوده؟",
    "چه روش یادگیری رو ترجیح می‌دی؟ (مطالعه، ویدیو، خلاصه‌نویسی و ...)",
    "دوست داری چه رشته‌ای قبول بشی؟",
    "چه دانشگاهی مد نظرت هست؟",
    "صبح‌ها بهتر درس می‌خونی یا شب‌ها؟",
    "منابعی که داری رو بگو (برای هر درس چی داری؟)"
]

# نگهداری وضعیت گفتگو
user_states = {}

def start(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    user_states[chat_id] = {
        "step": 0,
        "answers": []
    }
    update.message.reply_text("سلام! من ربات مشاور کنکور هستم. بیا با چند سوال شروع کنیم 😊")
    update.message.reply_text(questions[0])

def handle_message(update: Update, context: CallbackContext):
    chat_id = update.effective_chat.id
    text = update.message.text

    if chat_id not in user_states:
        update.message.reply_text("لطفاً /start رو بزن تا شروع کنیم.")
        return

    state = user_states[chat_id]
    step = state["step"]

    # ذخیره پاسخ
    state["answers"].append(text)
    state["step"] += 1

    # ادامه سوالات
    if state["step"] < len(questions):
        update.message.reply_text(questions[state["step"]])
    else:
        update.message.reply_text("مرسی! در حال تحلیل پاسخ‌هات هستم...")

        # ارسال به OpenAI
        prompt = "\n".join(
            f"{i+1}. {q}\nپاسخ: {a}"
            for i, (q, a) in enumerate(zip(questions, state["answers"]))
        )
        prompt += "\n\nبر اساس این پاسخ‌ها، یک برنامه‌ریزی مشاوره‌ای و انگیزشی مناسب ارائه بده."

        try:
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}]
            )
            reply = response.choices[0].message["content"]
            update.message.reply_text(reply)
        except Exception as e:
            logger.error(e)
            update.message.reply_text("مشکلی در ارتباط با GPT پیش اومد. لطفاً دوباره تلاش کن.")

        # پاک‌سازی وضعیت کاربر
        del user_states[chat_id]

# هندلرها
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

# مسیر Webhook برای Render
@app.route("/", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot)
    dispatcher.process_update(update)
    return "ok"

# صفحه اصلی برای تست سریع
@app.route("/", methods=["GET"])
def index():
    return "Student Bot is running."

# اجرای اپلیکیشن Flask (برای اجرا در local یا debug لازم نیست)
if __name__ == "__main__":
    app.run()
