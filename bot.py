import os
import asyncpg
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# تنظیمات
user_data = {}
ADMIN_ID = int(os.getenv("ADMIN_ID"))
ADMIN_FORUM_ID = os.getenv("ADMIN_FORUM_ID")
TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")
WEBHOOK_URL = "https://telegram-student-bot-production.up.railway.app"  # URL جدید Webhook

# پرسش‌ها
questions = [
    "۱. پایه تحصیلی‌ت چیه؟ (دهم / یازدهم / دوازدهم)",
    "۲. رشته‌ت چیه؟ (ریاضی / تجربی / انسانی / هنر / زبان)",
    "۳. جنسیتت؟ (دختر / پسر)",
    "۴. ساکن کجایی؟ (شهر / روستا و استان)",
    "۵. روزانه به‌طور میانگین چند ساعت مطالعه می‌کنی؟",
    "۶. کدوم درس‌ها رو بهتر می‌فهمی یا نمره خوبی داری؟",
    "۷. کدوم درس‌ها برات سخته یا نمی‌تونی بخونی؟",
    "۸. از ۱۰ نمره، وضعیت کلی درس‌هات چند می‌دی به خودت؟",
    "۹. با کدوم روش راحت‌تری یاد می‌گیری؟ (کتاب خوندن / دیدن ویدیو / نوشتن خلاصه / تست‌زنی / توضیح دادن برای دیگران)",
    "۱۰. تمام کتاب‌ها یا منابعی که برای هر درس استفاده می‌کنی رو دقیق و کامل بگو (مثلاً ریاضی → تست جامع خیلی سبز، فیزیک → آبی قلمچی، زیست → فاگو، و ...)",
    "۱۱. در آزمون خاصی شرکت می‌کنی؟ (قلم‌چی / گاج / گزینه ۲ / بدون آزمون)",
    "۱۲. تراز یا رتبه‌ت در آزمون چقدره؟",
    "۱۳. آیا برنامه آزمون رو دنبال می‌کنی؟ (دقیق / نصفه نیمه / نه)",
    "۱۴. با تحلیل آزمون‌هات چه‌کار می‌کنی؟ (بررسی دقیق / فقط نگاه / هیچی)",
    "۱۵. هدفت از کنکور چیه؟ (مثلاً قبولی پزشکی تهران، رتبه زیر ۵۰۰، یا صرفاً قبولی دانشگاه دولتی)",
    "۱۶. انگیزه‌ت رو از ۱۰ چند می‌دونی؟",
    "۱۷. بزرگترین دلیلت برای درس خوندن چیه؟ (خانواده / علاقه / فرار از شرایط فعلی / درآمد خوب / ...)",
    "۱۸. آیا سر کار یا مسئولیت دیگه‌ای داری؟ (اگر بله: چقدر وقتتو می‌گیره؟)",
    "۱۹. محیط خونه‌ت برای مطالعه مناسبه؟ (آرومه یا شلوغ؟)",
    "۲۰. کسی هست که تشویقت کنه یا کمک‌ت کنه؟ (بله / نه)",
    "۲۱. به‌نظرت چه چیزهایی باعث می‌شن درس نخونی یا ناامید شی؟",
    "۲۲. ترجیح می‌دی برنامه‌ت روزانه باشه یا هفتگی؟",
    "۲۳. دوست داری اول صبح درس بخونی یا شب؟",
    "۲۴. چند روز در هفته دوست داری مرخصی داشته باشی؟",
    "۲۵. آیا ترجیح می‌دی برنامه‌ریزی دقیق دقیقه‌ای باشه یا فقط کلی؟"
]

# اتصال به دیتابیس PostgreSQL با asyncpg
async def get_db_connection():
    conn = await asyncpg.connect(DATABASE_URL)
    return conn

# ساخت جداول در دیتابیس
async def create_tables():
    conn = await get_db_connection()
    await conn.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id BIGINT PRIMARY KEY,
            username TEXT,
            first_name TEXT,
            topic_id BIGINT,
            created_at TIMESTAMP DEFAULT NOW()
        );
        CREATE TABLE IF NOT EXISTS messages(
            id SERIAL PRIMARY KEY,
            user_id BIGINT REFERENCES users(user_id),
            direction TEXT, -- 'IN' از سمت کاربر، 'OUT' از سمت شما/بات
            text TEXT,
            ts TIMESTAMP DEFAULT NOW()
        );
    """)
    await conn.close()

# ذخیره اطلاعات کاربران در حافظه
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data[user_id] = {"step": 0, "answers": []}
    await update.message.reply_text("سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟")
    await update.message.reply_text(questions[0])

# هندل کردن پیام‌های کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in user_data:
        await update.message.reply_text("لطفاً اول /start رو بزن 😊")
        return

    data = user_data[user_id]
    step = data["step"]
    data["answers"].append(update.message.text)
    step += 1

    if step < len(questions):
        data["step"] = step
        await update.message.reply_text(questions[step])
    else:
        await update.message.reply_text(
            "✅ مشاوره ثبت شد!\n"
            f"🧑‍🎓 اطلاعات مربوط به آیدی کاربر: {user_id}\n"
            "✳️ در حال پردازش برنامه‌ریزی هستیم، تا چند دقیقه دیگه برنامه اختصاصی‌ت آماده می‌شه."
        )

        # ارسال اطلاعات به ادمین
        answer_text = "\n".join([f"{i+1}. {questions[i]} \n➤ {ans}" for i, ans in enumerate(data["answers"])])
        await context.bot.send_message(chat_id=ADMIN_ID, text=f"📥 مشاوره جدید از کاربر {user_id}:\n\n{answer_text}")

        # ارسال به گروه فوروم
        topic_id = await ensure_topic_for_user(user_id)
        await send_message_to_forum(user_id, answer_text, topic_id)

        del user_data[user_id]

# بررسی یا ایجاد topic برای هر کاربر در گروه فوروم
async def ensure_topic_for_user(user_id):
    # اینجا کد برای گرفتن یا ایجاد topic_id مربوط به کاربر قرار می‌گیره
    return user_id  # برای مثال برگشت دادن همان user_id به عنوان topic_id

# ارسال پیام به گروه فوروم
async def send_message_to_forum(user_id, text, topic_id):
    bot = Bot(token=TOKEN)
    message = f"👤 {user_id} :\n{text}"
    await bot.telegram.send_message(
        chat_id=ADMIN_FORUM_ID,
        text=message,
        message_thread_id=topic_id
    )

# تابع تنظیم Webhook
async def set_webhook_async(app):
    await app.bot.set_webhook(WEBHOOK_URL + "/webhook")

# شروع ربات
async def main():
    app = ApplicationBuilder().token(TOKEN).build()

    # اجرای تابع تنظیم Webhook به صورت غیرهمزمان
    await set_webhook_async(app)  # اجرای تابع تنظیم Webhook به صورت غیرهمزمان

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات فعال است و Webhook تنظیم شد...")

    # اجرای ربات به صورت Webhook
    await app.run_webhook(listen="0.0.0.0", port=5000, url_path="/webhook")

# اجرای برنامه
if __name__ == "__main__":
    import asyncio
    asyncio.get_event_loop().run_until_complete(main())  # استفاده از حلقهٔ رویداد موجود
