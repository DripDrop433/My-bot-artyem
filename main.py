import telebot
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

API_TOKEN = '9239617756:AAETXGXXJmGJ8DHEkwOdWO33PS36mfc08WU'

logging.basicConfig(level=logging.INFO)
bot = telebot.TeleBot(API_TOKEN)
activity_data = {}

@bot.message_handler(func=lambda message: True)
def count_messages(message):
    if message.chat.type not in ['group', 'supergroup']:
        return
    if message.from_user.is_bot:
        return

    user_id = message.from_user.id
    
    # Исправленное получение имени
    first_name = message.from_user.first_name or ""
    last_name = message.from_user.last_name or ""
    full_name = f"{first_name} {last_name}".strip() or "Пользователь"
    
    username = f"@{message.from_user.username}" if message.from_user.username else full_name

    if user_id not in activity_data:
        activity_data[user_id] = {"name": username, "count": 0, "chat_id": message.chat.id}
    
    activity_data[user_id]["count"] += 1

    if message.text and message.text.startswith('/top'):
        show_top(message)

def show_top(message):
    if not activity_data:
        bot.reply_to(message, "Сегодня еще никто не писал!")
        return

    sorted_users = sorted(activity_data.items(), key=lambda x: x[1]["count"], reverse=True)[:5]
    text = "📈 *Текущий топ активности на этот час:*\n\n"
    for i, (user_id, data) in enumerate(sorted_users):
        text += f"{i+1}. {data['name']} — {data['count']} сообщ.\n"
    
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

def send_daily_results():
    if not activity_data:
        return

    sorted_users = sorted(activity_data.items(), key=lambda x: x[1]["count"], reverse=True)
    top_users = sorted_users[:3]
    target_chat_id = list(activity_data.values())["chat_id"]

    text = "📊 *Итоги активности за сегодня!*\n\n"
    placeholders = ["🥇", "🥈", "🥉"]

    for i, (user_id, data) in enumerate(top_users):
        text += f"{placeholders[i]} {data['name']} — {data['count']} сообщ.\n"
    
    text += f"\nПоздравляем победителей! Администратор свяжется с вами для вручения подарков ⭐️"

    try:
        bot.send_message(chat_id=target_chat_id, text=text, parse_mode="Markdown")
    except Exception as e:
        logging.error(f"Ошибка при отправке итогов: {e}")

    activity_data.clear()

if __name__ == '__main__':
    scheduler = BackgroundScheduler()
    scheduler.add_job(send_daily_results, CronTrigger(hour=23, minute=59))
    scheduler.start()
    
    print("Бот успешно запущен и считает сообщения...")
    bot.infinity_polling()
