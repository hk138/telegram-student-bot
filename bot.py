import logging
from telegram import Update, ForceReply
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(level=logging.INFO)

# مرحله‌های گفت‌وگو
(
    STEP1, STEP2, STEP3, STEP5, STEP6, STEP8, STEP9, STEP10,
    STEP11, STEP12, STEP15, STEP16, STEP17, STEP18, STEP19,
    STEP20, STEP21, STEP22, STEP23, STEP24, STEP25
) = range(21)

answers = {}

questions = [
    ("برای شروع، پایه تحصیلی‌ات چیه؟ (دهم، یازدهم، دوازدهم)", STEP1),
    ("هدف اصلی‌ات از درس خوندن چیه؟ (رتبه، رشته خاص، دانشگاه، معدل و...)", STEP2),
    ("چه درس‌هایی رو بیشتر دوست داری و کدوم‌ها برات چالش‌برانگیزن؟", STEP3),
    ("چه منابع یا کتاب‌هایی برای هر درس استفاده می‌کنی؟ کامل بگو تا طبق اون پیش بریم", STEP5),
    ("چه زمانی از روز بیشتر مطالعه می‌کنی؟", STEP6),
    ("در حال حاضر چند ساعت در روز مطالعه می‌کنی؟", STEP8),
    ("بیشتر عادت داری چطور درس بخونی؟ (مثلاً خلاصه‌نویسی، تست‌زنی، بلندخوانی و...)", STEP9),
    ("از چه روش‌هایی برای مرور استفاده می‌کنی؟", STEP10),
    ("آیا در آزمون‌های آزمایشی شرکت می‌کنی؟ کدوم آزمون؟", STEP11),
    ("نتایج آزمون‌هات چطوره؟ از خودت راضی هستی؟", STEP12),
    ("عادت‌های بد یا نقاط ضعفی که توی مطالعه داری چیا هستن؟", STEP15),
    ("چه زمانی بیشترین انگیزه رو برای درس خوندن داری؟", STEP16),
    ("آیا برای درس خوندن برنامه‌ریزی خاصی داری؟ خودت می‌نویسی یا از کسی کمک می‌گیری؟", STEP17),
    ("اگه یه روز از برنامه عقب بیفتی، چیکار می‌کنی؟", STEP18),
    ("ترجیح می‌دی روزت رو چطوری شروع کنی؟", STEP19),
    ("چه چیزهایی باعث حواست‌پرتی در زمان مطالعه می‌شن؟", STEP20),
    ("ترجیح می‌دی با دوستی درس بخونی یا تنهایی؟ چرا؟", STEP21),
    ("توی خونه فضای مناسبی برای درس خوندن داری؟", STEP22),
    ("در طول هفته چند روز رو کامل درس می‌خونی؟", STEP23),
    ("چه زمانی از شبانه‌روز تمرکزت بیشتره؟", STEP24),
    ("آیا ورزش یا تفریح منظمی هم داری؟ چی و چند وقت یک‌بار؟", STEP25)
]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.chat_id
    context.user_data['answers'] = {}
    context.user_data['step'] = 0
    await update.message.reply_text("سلام! 😊 بیا با چند سؤال شروع کنیم تا بتونم یه برنامه‌ریزی دقیق برات بچینم.")
    await ask_next_question(update, context)
    return STEP1

async def ask_next_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step_index = context.user_data.get('step', 0)
    if step_index < len(questions):
        question_text, next_step = questions[step_index]
        await update.message.reply_text(question_text)
        return next_step
    else:
        # پایان سؤالات
        result = "\n\n✅ اطلاعات شما:\n"
        for i, (q, _) in enumerate(questions):
            a = context.user_data['answers'].get(i, "پاسخ داده نشده")
            result += f"{i+1}. {q}\n📝 {a}\n\n"
        await update.message.reply_text("ممنون از پاسخت! حالا براساس اطلاعاتت برنامه رو برات طراحی می‌کنم...")
        await update.message.reply_text(result)
        return ConversationHandler.END

async def handle_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    step_index = context.user_data.get('step', 0)
    context.user_data['answers'][step_index] = update.message.text
    context.user_data['step'] += 1
    return await ask_next_question(update, context)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مکالمه لغو شد.")
    return ConversationHandler.END

def main():
    import os
    TOKEN = os.environ.get("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={step: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_response)] for _, step in questions},
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()

if __name__ == "__main__":
    main()
