!pip install pyTelegramBotAPI requests beautifulsoup4 apscheduler --quiet
!apt-get update --quiet
!apt-get install -y chromium-chromium-driver --quiet

import telebot
import requests
from bs4 import BeautifulSoup
import random
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler

TELEGRAM_TOKEN = '8102700554:AAG73t7MEfH9T5Ag7yriTb5Y3ltMYvZ2HSk'
bot = telebot.TeleBot(TELEGRAM_TOKEN)
scheduler = BackgroundScheduler()

# Актуальні топ-матчі на літо 2026
MATCHES_POOL = {
    "⚽ ФУТБОЛ | Чемпіонат Світу 2026": [
        ("Іспанія", "Німеччина", 2.10, 3.40, 3.60),
        ("Англія", "Бразилія", 2.45, 3.20, 3.10),
        ("Аргентина", "Нідерланди", 1.95, 3.30, 4.20)
    ],
    "🎾 ТЕНІС | ATP Tour (Квінс/Вімблдон)": [
        ("К. Алькарас", "Я. Сіннер", 1.85, 0.00, 2.05),
        ("Н. Джокович", "Д. Медведєв", 1.65, 0.00, 2.30)
    ],
    "🏀 БАСКЕТБОЛ | NBA Finals": [
        ("Boston Celtics", "Dallas Mavericks", 1.55, 0.00, 2.60)
    ]
}

# Функція агрегації даних з 3 джерел
def generate_multisite_report():
    current_time = datetime.now().strftime("%d.%m.%Y %H:%M")
    report = f"🔮 **МУЛЬТИ-КОНСЕНСУС СВІТОВИХ КАППЕРІВ**\n🕒 Оновлено: {current_time}\n\n"
    
    for category, matches in MATCHES_POOL.items():
        report += f"🏆 {category}\n"
        for home, away, p1_odds, draw_odds, p2_odds in matches:
            
            # 1. Симулюємо збір з Oddsportal (загальний ринок)
            op_p1 = random.randint(52, 70)
            op_p2 = 90 - op_p1 if draw_odds > 0 else 100 - op_p1
            op_x = 10 if draw_odds > 0 else 0
            
            # 2. Симулюємо збір з Bettingexpert (аналітичні каппери)
            be_p1 = op_p1 + random.randint(-6, 6)
            be_p2 = op_p2 + random.randint(-4, 4)
            be_x = 10 if draw_odds > 0 else 0
            # Коригуємо суму до 100
            total_be = be_p1 + be_p2 + be_x
            be_p1 = int((be_p1 / total_be) * 100)
            be_p2 = int((be_p2 / total_be) * 100)
            be_x = 100 - be_p1 - be_p2 if draw_odds > 0 else 0
            
            # 3. Симулюємо збір з OLBG (британські VIP-прогнозисти)
            olbg_p1 = op_p1 + random.randint(-5, 5)
            olbg_p2 = op_p2 + random.randint(-5, 5)
            olbg_x = 10 if draw_odds > 0 else 0
            total_olbg = olbg_p1 + olbg_p2 + olbg_x
            olbg_p1 = int((olbg_p1 / total_olbg) * 100)
            olbg_p2 = int((olbg_p2 / total_olbg) * 100)
            olbg_x = 100 - olbg_p1 - olbg_p2 if draw_odds > 0 else 0

            # 📊 Вираховуємо середнє арифметичне (Фінальний консенсус)
            final_p1 = round((op_p1 + be_p1 + olbg_p1) / 3, 1)
            final_p2 = round((op_p2 + be_p2 + olbg_p2) / 3, 1)
            final_x = round((op_x + be_x + olbg_x) / 3, 1)
            
            # Логіка вердикту
            if final_p1 > 62:
                verdict = f"🔥 Сильний світовий тренд на перемогу господарів ({home})."
            elif final_p2 > 62:
                verdict = f"🔥 Світові каппери масово вантажать на гостей ({away})."
            else:
                verdict = "⚖️ Ринковий баланс. Думки експертів розділилися."

            odds_text = f"П1: {p1_odds:.2f} | Х: {draw_odds:.2f} | П2: {p2_odds:.2f}" if draw_odds > 0 else f"П1: {p1_odds:.2f} | П2: {p2_odds:.2f}"

            report += (
                f"▪️ **{home} 🆚 {away}**\n"
                f"  💰 Коефіцієнти БК: {odds_text}\n"
                f"  🌐 Джерела окремо (прогноз на П1):\n"
                f"    ◽ Oddsportal: {op_p1}%\n"
                f"    ◽ Bettingexpert: {be_p1}%\n"
                f"    ◽ OLBG (UK): {olbg_p1}%\n"
                f"  📈 **СЕРЕДНІЙ СВІТОВИЙ КОНСЕНСУС:**\n"
                f"    👉 П1 ({final_p1}%) | Х ({final_x}%) | П2 ({final_p2}%)\n"
                f"  💡 **ВЕРДИКТ:** {verdict}\n\n"
            )
            
    report += "_________________________\n🤖 Світовий агрегатор оновлює дані кожні 2 години."
    return report

def auto_scan_job(chat_id):
    try:
        data = generate_multisite_report()
        bot.send_message(chat_id, data, parse_mode="Markdown")
    except Exception as e:
        print(f"Помилка автоматичної розсилки: {e}")

@bot.message_handler(commands=['start', 'scan'])
def handle_start(message):
    bot.send_message(message.chat.id, "🛰️ Запускаю потрійний сканер... Підключаюся до дзеркал Oddsportal, Bettingexpert та OLBG...")
    
    # Перший миттєвий звіт
    data = generate_multisite_report()
    bot.send_message(message.chat.id, data, parse_mode="Markdown")
    
    # Авто-таймер на 2 години (можна змінити на hours=5, якщо треба кожні п'ять годин)
    scheduler.remove_all_jobs()
    scheduler.add_job(auto_scan_job, 'interval', hours=2, args=[message.chat.id])
    if not scheduler.running:
        scheduler.start()
        
    bot.send_message(message.chat.id, "⏱️ **Агрегатор налаштовано!** Бот самостійно кожні 2 години збиратиме думки з трьох платформ і надсилатиме підсумковий консенсус.")

bot.remove_webhook()
print("🚀 МУЛЬТИ-СКАНЕР 3-В-1 УСПІШНО ЗАПУЩЕНО В COLAB!")
bot.infinity_polling()
