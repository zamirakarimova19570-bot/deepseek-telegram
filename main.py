import os
import logging
from datetime import datetime
from typing import Optional
from dotenv import load_dotenv
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
from deepseek import DeepSeek

# Logging sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Environment variables
load_dotenv()
DEEPSEEK_API_KEY = os.getenv("sk-627cf0ee87414295992cb081ee3512da")
TELEGRAM_TOKEN = os.getenv("8566384804:AAFpCbo92jD2FOC5t9GqJm2dqPpDmF4Bcg0")

# DeepSeek klientini yaratish
deepseek_client = DeepSeek(api_key=DEEPSEEK_API_KEY)

# User sessiyalari
user_sessions = {}

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("🆕 Yangi suhbat", callback_data='new_chat')],
        [InlineKeyboardButton("❓ Yordam", callback_data='help')],
        [InlineKeyboardButton("📊 Mening statistikam", callback_data='stats')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = f"""
    🤖 *Xush kelibsiz, {user.first_name}!*
    
    *Men DeepSeek AI yordamchisining Telegram versiyasiman*
    
    ⚡ *Mening imkoniyatlarim:*
    • Bepul sun'iy intellekt yordamchisi
    • Kod yozishda yordam
    • Matn tahrirlash va tarjima
    • Savollarga javob berish
    
    🆓 *Bu xizmut mutlaqo BEPUL!*
    
    Faqat xabar yuboring va men javob beraman!
    """
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Yangi suhbat boshlash
async def new_chat(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    user_sessions[user_id] = []
    
    await query.edit_message_text(
        "🆕 *Yangi suhbat boshlandi!*\n\nEndi savolingizni yozishingiz mumkin.",
        parse_mode='Markdown'
    )

# DeepSeek dan javob olish
async def get_deepseek_response(user_message: str, user_id: int) -> str:
    try:
        # Sessiya tarixini saqlash
        if user_id not in user_sessions:
            user_sessions[user_id] = []
        
        # Foydalanuvchi xabarini qo'shish
        user_sessions[user_id].append({"role": "user", "content": user_message})
        
        # Tarixni cheklash (oxirgi 10 ta xabar)
        if len(user_sessions[user_id]) > 10:
            user_sessions[user_id] = user_sessions[user_id][-10:]
        
        # DeepSeek ga so'rov yuborish
        response = deepseek_client.chat.completions.create(
            model="deepseek-chat",
            messages=user_sessions[user_id],
            max_tokens=1024,
            temperature=0.7
        )
        
        # Javobni olish
        ai_response = response.choices[0].message.content
        
        # AI javobini sessiyaga qo'shish
        user_sessions[user_id].append({"role": "assistant", "content": ai_response})
        
        return ai_response
        
    except Exception as e:
        logger.error(f"DeepSeek xatosi: {e}")
        return "❌ Kechirasiz, javob olishda xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring."

# Xabarlarni qayta ishlash
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_message = update.message.text
    
    # "Kutish" xabarini yuborish
    wait_msg = await update.message.reply_text("⚡ *Javob tayyorlanmoqda...*", parse_mode='Markdown')
    
    # DeepSeek dan javob olish
    response = await get_deepseek_response(user_message, user_id)
    
    # Kutish xabarini o'chirish
    await wait_msg.delete()
    
    # Javobni yuborish
    await update.message.reply_text(
        response,
        parse_mode='Markdown',
        reply_to_message_id=update.message.message_id
    )

# Statistikani ko'rsatish
async def show_stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.from_user.id
    session_count = len(user_sessions.get(user_id, [])) // 2
    
    stats_text = f"""
    📊 *Sizning statistikangiz:*
    
    • 📝 Sessiyalar: {session_count} ta
    • 🤖 Model: DeepSeek Chat
    • ⏰ Vaqt: {datetime.now().strftime('%H:%M')}
    • 🆓 Holat: BEPUL
    
    *API Limitlari:*
    • 📅 Kunlik: 100 so'rov
    • ⚡ Soatlik: 10 so'rov
    • 🎯 Token: 4096/sorrov
    """
    
    await query.edit_message_text(stats_text, parse_mode='Markdown')

# Yordam
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = """
    *🤖 DeepSeek Telegram Bot Yordami*
    
    *🔹 Buyruqlar:*
    /start - Botni ishga tushirish
    /new - Yangi suhbat boshlash
    /help - Yordam ko'rsatish
    /stats - Statistikani ko'rsatish
    
    *🔹 Qanday ishlatish:*
    1. Faqat matn yozing va jo'nating
    2. Men tezda javob beraman
    3. Kod yozishda yordam bera olaman
    4. Tarjima qila olaman
    
    *🔹 Limitlar:*
    • Xizmat mutlaqo BEPUL
    • Kuniga 100 ta so'rov
    • Har bir javob 4096 token gacha
    
    *👨‍💻 Yaratuvchi:* Isoqova Mironshoh
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

# Asosiy funksiya
def main():
    # Botni yaratish
    application = Application.builder().token(TELEGRAM_TOKEN).build()
    
    # Handlerlarni qo'shish
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("new", new_chat))
    application.add_handler(CommandHandler("stats", show_stats))
    application.add_handler(CallbackQueryHandler(new_chat, pattern='new_chat'))
    application.add_handler(CallbackQueryHandler(show_stats, pattern='stats'))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Botni ishga tushirish
    logger.info("Bot ishga tushmoqda...")
    application.run_polling(allowed_updates=Update.ALL_UPDATES)

if __name__ == '__main__':
    main()
