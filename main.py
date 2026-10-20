import os
import yt_dlp
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

TOKEN = "8819942056:AAE8VFjGNV-IgMtGMQ22-_OiHsAldqUF78E"

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

user_states = {}

def get_buttons():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🎵 تنزيل تيك توك", callback_data='tiktok'),
         InlineKeyboardButton("▶️ تنزيل يوتيوب", callback_data='youtube')],
        [InlineKeyboardButton("📌 تنزيل بينترست", callback_data='pinterest'),
         InlineKeyboardButton("📘 تنزيل فيسبوك", callback_data='facebook')],
        [InlineKeyboardButton("📸 تنزيل إنستجرام", callback_data='instagram')]
    ])

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = "👋 أهلاً بك في بوت التحميلات الشامل!\n\nاختار المنصة اللي عايز تنزل منها، وابعتلي الرابط."
    await update.message.reply_text(text, reply_markup=get_buttons())

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    platform = q.data
    user_states[q.message.chat_id] = platform
    platform_names = {
        'tiktok': 'تيك توك', 'youtube': 'يوتيوب', 
        'pinterest': 'بينترست', 'facebook': 'فيسبوك', 'instagram': 'إنستجرام'
    }
    await q.edit_message_text(f"✅ تم اختيار: {platform_names[platform]}\n\n📥 ابعتلي الرابط دلوقتي.", parse_mode='Markdown')

async def download_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.message.chat_id
    url = update.message.text.strip()

    if chat_id not in user_states:
        await update.message.reply_text("⚠️ من فضلك اختار المنصة الأول.", reply_markup=get_buttons())
        return
    if not url.startswith("http"):
        await update.message.reply_text("❌ ابعتلي رابط صحيح.")
        return

    msg = await update.message.reply_text("⏳ جاري التحميل...")
    file_name = f"download_{chat_id}"
    ydl_opts = {'outtmpl': f'{file_name}.%(ext)s', 'format': 'best', 'quiet': True}

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)
            
            if os.path.exists(filename):
                await msg.edit_text("✅ جاري الإرسال...")
                if filename.endswith(('.jpg', '.jpeg', '.png', '.webp')):
                    await update.message.reply_photo(photo=open(filename, 'rb'))
                else:
                    await update.message.reply_video(video=open(filename, 'rb'), supports_streaming=True)
                os.remove(filename)
                await msg.delete()
                await update.message.reply_text("تحب تنزل حاجة تانية؟", reply_markup=get_buttons())
                del user_states[chat_id]
            else:
                await msg.edit_text("❌ فشل التحميل.")
    except Exception as e:
        await msg.edit_text("⚠️ حصل خطأ.")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_media))
    app.run_polling()

if __name__ == "__main__":
    main()