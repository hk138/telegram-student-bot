from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

user_data = {}

import os
ADMIN_ID = int(os.getenv("ADMIN_ID"))

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

        del user_data[user_id]

if __name__ == "__main__":
    import os
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("ربات اجرا شد...")
    app.run_polling()
import pkg from 'pg';
const { Pool } = pkg;

// متصل شدن به دیتابیس
const pool = new Pool({
  connectionString: process.env.DATABASE_URL, // این متغیر رو از Railway یا فایل محیطی بردار
});

// کد ساخت جداول
async function createTables() {
  await pool.query(`
    CREATE TABLE IF NOT EXISTS users(
      user_id BIGINT PRIMARY KEY,
      username TEXT,
      first_name TEXT,
      topic_id BIGINT,
      created_at TIMESTAMP DEFAULT NOW()
    );
    CREATE TABLE IF NOT EXISTS messages(
      id BIGSERIAL PRIMARY KEY,
      user_id BIGINT REFERENCES users(user_id),
      direction TEXT,
      text TEXT,
      ts TIMESTAMP DEFAULT NOW()
    );
  `);
}

createTables().then(() => {
  console.log("Tables created!");
}).catch(e => console.error('Error creating tables:', e));
