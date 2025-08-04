from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# وضعیت‌ها
ASK_GRADE, ASK_GOAL, ASK_HOURS, ASK_STRENGTH, ASK_WEAKNESS, ASK_MOOD, ASK_TESTS, ASK_RESULTS, ASK_LEARNING_STYLE, ASK_MAJOR, ASK_UNIVERSITY, ASK_TIME_OF_DAY, ASK_RESOURCES = range(13)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "سلام! به ربات مشاور کنکور خوش اومدی 🌟\n\nبرای شروع مشاوره، پایه تحصیلی خودتو بگو (دهم، یازدهم، دوازدهم):"
    )
    return ASK_GRADE

async def ask_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("هدفت از درس خوندن چیه؟ (مثلاً قبولی در رشته خاص، پیشرفت نمره‌ها و...)")
    return ASK_GOAL

async def ask_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text
    await update.message.reply_text("روزی چند ساعت مطالعه می‌کنی؟")
    return ASK_HOURS

async def ask_strength(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hours"] = update.message.text
    await update.message.reply_text("به نظرت نقطه قوتت در درس‌ها چیه؟")
    return ASK_STRENGTH

async def ask_weakness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["strength"] = update.message.text
    await update.message.reply_text("به نظرت نقطه ضعفت چیه؟")
    return ASK_WEAKNESS

async def ask_mood(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weakness"] = update.message.text
    await update.message.reply_text("علت اینکه بعضی وقتا حس درس خوندن نداری چیه؟")
    return ASK_MOOD

async def ask_tests(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["mood"] = update.message.text
    await update.message.reply_text("تو آزمون خاصی شرکت می‌کنی؟ اگر آره، بگو کدوم.")
    return ASK_TESTS

async def ask_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["tests"] = update.message.text
    await update.message.reply_text("آخرین نتیجه آزمونی که دادی رو بفرست (تراز یا رتبه).")
    return ASK_RESULTS

async def ask_learning_style(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["results"] = update.message.text
    await update.message.reply_text("چه روش یادگیری رو ترجیح میدی؟ (مطالعه، ویدیو دیدن و...)")
    return ASK_LEARNING_STYLE

async def ask_major(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["learning_style"] = update.message.text
    await update.message.reply_text("چه رشته‌ای دوست داری قبول بشی؟")
    return ASK_MAJOR

async def ask_university(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["major"] = update.message.text
    await update.message.reply_text("چه دانشگاهی دوست داری بری؟")
    return ASK_UNIVERSITY

async def ask_time_of_day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["university"] = update.message.text
    await update.message.reply_text("صبح‌ها سرحال‌تری یا شب‌ها؟")
    return ASK_TIME_OF_DAY

async def ask_resources(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["time_of_day"] = update.message.text
    await update.message.reply_text("منابعی که داری رو بگو (مثلاً شیمی خیلی سبز، ریاضی نشر الگو و...)")
    return ASK_RESOURCES

async def done(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["resources"] = update.message.text
    await update.message.reply_text("✅ اطلاعاتت ثبت شد! تا چند لحظه دیگه مشاوره‌ات آماده میشه.")
    # در این مرحله می‌تونی اتصال به ChatGPT یا تحلیل رو اضافه کنی
    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مشاوره لغو شد.")
    return ConversationHandler.END

if __name__ == "__main__":
    app = ApplicationBuilder().token("8117664156:AAFdfRxZ-7t0qXdQ_FUrcBbC7dY23Xs5BFw").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_goal)],
            ASK_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_hours)],
            ASK_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_strength)],
            ASK_STRENGTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weakness)],
            ASK_WEAKNESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_mood)],
            ASK_MOOD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_tests)],
            ASK_TESTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_results)],
            ASK_RESULTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_learning_style)],
            ASK_LEARNING_STYLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_major)],
            ASK_MAJOR: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_university)],
            ASK_UNIVERSITY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_time_of_day)],
            ASK_TIME_OF_DAY: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_resources)],
            ASK_RESOURCES: [MessageHandler(filters.TEXT & ~filters.COMMAND, done)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

    return "Student Bot is running."

# اجرای اپلیکیشن Flask (برای اجرا در local یا debug لازم نیست)
if __name__ == "__main__":
    app.run()
