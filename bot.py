import os
import json
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler
from config import BOT_TOKEN, ADMIN_ID

DATA_FOLDER = "data"
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

ASK_GRADE, ASK_GOAL, ASK_WEAKNESS, ASK_HOURS = range(4)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("سلام! به ربات مشاور کنکور خوش اومدی. پایه تحصیلی‌ات چیه؟ (دهم / یازدهم / دوازدهم)")
    return ASK_GRADE

async def ask_goal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["grade"] = update.message.text
    await update.message.reply_text("هدفت چیه؟ (مثلاً قبولی در پزشکی، مهندسی، حقوق...)")
    return ASK_GOAL

async def ask_weakness(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["goal"] = update.message.text
    await update.message.reply_text("بگو چه درس‌هایی برات چالشه؟")
    return ASK_WEAKNESS

async def ask_hours(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["weakness"] = update.message.text
    await update.message.reply_text("روزی چند ساعت می‌تونی درس بخونی؟")
    return ASK_HOURS

async def finish(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["hours"] = update.message.text
    user_id = update.message.from_user.id
    username = update.message.from_user.username or "بدون نام کاربری"
    file_path = os.path.join(DATA_FOLDER, f"{user_id}.json")

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(context.user_data, f, ensure_ascii=False, indent=2)

    await update.message.reply_text("ممنون! اطلاعاتت ثبت شد. به‌زودی مشاوره‌ات رو دریافت می‌کنی.")

    # اطلاع به ادمین
    msg = f"""📥 مشاوره جدید دریافت شد:
👤 کاربر: @{username}
🧑‍🎓 پایه: {context.user_data["grade"]}
🎯 هدف: {context.user_data["goal"]}
❗ ضعف‌ها: {context.user_data["weakness"]}
⏱ ساعات مطالعه: {context.user_data["hours"]}
"""
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)
    return ConversationHandler.END

async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("دستور نامعتبره. لطفاً از /start استفاده کن.")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            ASK_GRADE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_goal)],
            ASK_GOAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weakness)],
            ASK_WEAKNESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_hours)],
            ASK_HOURS: [MessageHandler(filters.TEXT & ~filters.COMMAND, finish)],
        },
        fallbacks=[MessageHandler(filters.COMMAND, unknown)],
    )

    app.add_handler(conv_handler)
    app.run_polling()
