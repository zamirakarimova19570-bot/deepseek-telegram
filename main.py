import os
import logging
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from deepseek import DeepSeek

# Logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Load environment
load_dotenv()
TOKEN = os.getenv("8566384804:AAFpCbo92jD2FOC5t9GqJm2dqPpDmF4Bcg0")
DEEPSEEK_KEY = os.getenv("sk-627cf0ee87414295992cb081ee3512da")

# Initialize DeepSeek
deepseek = DeepSeek(api_key=DEEPSEEK_KEY)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    welcome = f"""🤖 *Assalomu alaykum {user.first_name}!*

Men DeepSeek AI yordamchisiman. Sizga qanday yordam bera olaman?

*Mening qobiliyatlarim:*
• 📚 Bilim berish
• 💻 Kod yozishda yordam
• 🌍 Tarjima qilish
• 📝 Matn tahrirlash

Faqat savolingizni yozing!"""
    
    await update.message.reply_text(welcome, parse_mode='Markdown')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_msg = update.message.text
        
        # Show typing action
        await update.message.chat.send_action(action="typing")
        
        # Get response from DeepSeek
        response = deepseek.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": user_msg}],
            max_tokens=1024
        )
        
        ai_response = response.choices[0].message.content
        
        # Send response
        await update.message.reply_text(ai_response)
        
    except Exception as e:
        logger.error(f"Xato: {e}")
        await update.message.reply_text("❌ Kechirasiz, xatolik yuz berdi. Iltimos, keyinroq urinib ko'ring.")

def main():
    if not TOKEN or not DEEPSEEK_KEY:
        logger.error("TELEGRAM_TOKEN yoki DEEPSEEK_API_KEY topilmadi!")
        return
    
    # Create application
    app = Application.builder().token(TOKEN).build()
    
    # Add handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start bot
    logger.info("Bot ishga tushmoqda...")
    app.run_polling()

if __name__ == '__main__':
    main()
