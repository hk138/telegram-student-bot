import os
import openai
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler, ContextTypes
from openai import AsyncOpenAI
import os

client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# گرفتن توکن‌ها از متغیرهای محیطی
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-3.5-turbo")

if not TELEGRAM_BOT_TOKEN or not OPENAI_API_KEY:
    raise ValueError("توکن تلگرام یا کلید OpenAI وارد نشده‌اند.")

openai.api_key = OPENAI_API_KEY

# مراحل مکالمه
(
    GRADE, GOAL, STUDY_HOURS, STRENGTHS, WEAKNESSES,
    LEARNING_STYLE, TESTS, SOURCES, CONFIRM
) = range(9)

user_data = {}

# شروع مکالمه
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! من ربات مشاور کنکور هستم 🎓\n خوبی عزیزم! 🤍 خوشحالم که تصمیم گرفتی برای کنکورت برنامه‌ریزی هوشمندانه داشته باشی. من اینجا هستم تا کمکت کنم\n\n  حالا چند تا سوال میپرسم تا بیشتر باهات آشنا بشم\n\nابتدا بگو پایه تحصیلی‌ات چیست؟ (دهم / یازدهم / دوازدهم)")
    return GRADE

async def handle_grade(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["پایه"] = update.message.text
    await update.message.reply_text("هدفت در کنکور چیست؟ (رشته، دانشگاه، رتبه و...)")
    return GOAL

async def handle_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["هدف"] = update.message.text
    await update.message.reply_text("روزانه چند ساعت درس می‌خوانی؟")
    return STUDY_HOURS

async def handle_study_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["ساعات مطالعه"] = update.message.text
    await update.message.reply_text("برای شروع، بگو چه درس‌هایی رو بیشتر دوست داری و کدوم‌ها برات چالش‌انگیزترن؟ (مثلاً ریاضی، زیست، ادبیات...)")
    return STRENGTHS

async def handle_strengths(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["نقاط قوت"] = update.message.text
    await update.message.reply_text("استرس یا نگرانی خاصی داری که بخوای راجع بهش حرف بزنی؟ (مثلاً وقت کم میاری، تمرکز نداری، یا منابعت نامشخصه؟)")
    return WEAKNESSES

async def handle_weaknesses(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["نقاط ضعف"] = update.message.text
    await update.message.reply_text("روش یادگیری‌ات چطوریه؟ (خواندن، دیدن ویدیو، خلاصه‌نویسی و...)")
    return LEARNING_STYLE

async def handle_learning_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["روش یادگیری"] = update.message.text
    await update.message.reply_text("آیا در آزمون آزمایشی شرکت می‌کنی؟ اگر آره کدام؟")
    return TESTS

async def handle_tests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["آزمون"] = update.message.text
    await update.message.reply_text("چه منابعی استفاده می‌کنی؟ (کتاب‌ها، معلم‌ها، ویدیوها و...)")
    return SOURCES

async def handle_sources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data["منابع"] = update.message.text
    await update.message.reply_text("✅ اطلاعات دریافت شد. دارم برات یه مشاوره دقیق آماده می‌کنم...")
    
    prompt = "یک مشاور کنکور هوشمند هستی. با اطلاعات زیر یک برنامه و مشاوره کوتاه بده:\n\n"
    for key, value in user_data.items():
        prompt += f"{key}: {value}\n"
    
    response = await client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {"role": "system", "content": "تو یک مشاور کنکور هستی"},
        {"role": "user", "content": "سوالات کاربر..."}
    ]
)

await update.message.reply_text(response.choices[0].message.content)

    
    reply = response.choices[0].message.content.strip()
    await update.message.reply_text("📌 مشاوره شما:\n\n" + reply)

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مکالمه لغو شد.")
    return ConversationHandler.END

# راه‌اندازی برنامه
def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_grade)],
            GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_goal)],
            STUDY_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_study_hours)],
            STRENGTHS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_strengths)],
            WEAKNESSES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_weaknesses)],
            LEARNING_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_learning_style)],
            TESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tests)],
            SOURCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_sources)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
