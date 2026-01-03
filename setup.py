#!/usr/bin/env python3
import os

def setup():
    print("🤖 DeepSeek Telegram Bot O'rnatish Dasturi")
    print("=" * 50)
    
    # Check if .env exists
    if not os.path.exists('.env'):
        print("\n.env fayli yaratilmoqda...")
        with open('.env', 'w') as f:
            f.write("TELEGRAM_TOKEN=your_bot_token_here\n")
            f.write("DEEPSEEK_API_KEY=sk-your_api_key_here\n")
        print("✅ .env fayli yaratildi")
        print("Iltimos, .env faylini to'ldiring!")
    else:
        print("✅ .env fayli mavjud")
    
    print("\nO'rnatish yakunlandi!")
    print("1. .env faylini to'ldiring")
    print("2. python main.py ni ishga tushiring")

if __name__ == '__main__':
    setup()
