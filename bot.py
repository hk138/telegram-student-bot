import os
import requests
import time
import telegram
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# تنظیمات
TOKEN = os.getenv("BOT_TOKEN")
WEBHOOK_URL = os.getenv("WEBHOOK_URL")
ADMIN_ID = os.getenv("ADMIN_ID")

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

# تابع start برای خوش‌آمدگویی
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"سلام! برای شروع مشاوره، به چند سوال جواب بده 🌟\n\nآیدی کاربر: {user_id}")
    await update.message.reply_text(questions[0])

# حذف Webhook قبلی
def delete_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/deleteWebhook"
    response = requests.get(url)
    print(response.json())  # چاپ پاسخ برای اطمینان از حذف Webhook

# تنظیم Webhook جدید
def set_webhook():
    url = f"https://api.telegram.org/bot{TOKEN}/setWebhook?url={WEBHOOK_URL}/webhook"
    response = requests.get(url)
    print(response.json())  # چاپ پاسخ برای اطمینان از تنظیم Webhook

# تابع غیرهمزمان برای تنظیم Webhook با Retry در صورت خطای Rate Limit
async def set_webhook_async():
    try:
        # تلاش برای تنظیم Webhook
        await app.bot.set_webhook(WEBHOOK_URL + "/webhook")
    except telegram.error.RetryAfter as e:
        print(f"Rate limit exceeded. Retrying after {e.retry_after} seconds...")
        time.sleep(e.retry_after)  # صبر کردن به مدت مشخص شده
        await set_webhook_async()  # دوباره تلاش کردن

# هندل کردن پیام‌های کاربر
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    await update.message.reply_text(f"پیام شما دریافت شد, آیدی کاربر: {user_id}")

# شروع ربات
async def main():
    global app
    app = ApplicationBuilder().token(TOKEN).build()

    # حذف Webhook قبلی و سپس تنظیم Webhook جدید
    delete_webhook()  # حذف Webhook قبلی
    set_webhook()     # تنظیم Webhook جدید

    # افزودن هندلرها
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # اجرای ربات به صورت Webhook
    print("ربات فعال است و Webhook تنظیم شد...")
    await set_webhook_async()  # استفاده از set_webhook با تأخیر در صورت نیاز
    await app.run_webhook(listen="0.0.0.0", port=5000, url_path="/webhook")

if __name__ == "__main__":
    # استفاده مستقیم از app.run_webhook() به جای asyncio.run()
    print("ربات در حال راه‌اندازی است...")
    app.run_webhook(listen="0.0.0.0", port=5000, url_path="/webhook")
