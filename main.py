import os
import threading
from flask import Flask
from vk_api import VkApi
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id

# --- 1. ВЕБ-СЕРВЕР ДЛЯ RENDER (ЭТО НОВЫЙ БЛОК) ---
app = Flask(__name__)

@app.route('/')
def hello():
    return "VK Bot is running!"

def run_web():
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 10000)))

# --- 2. ОСНОВНАЯ ЛОГИКА БОТА (ПОЧТИ БЕЗ ИЗМЕНЕНИЙ) ---
def run_bot():
    VK_TOKEN = os.getenv("VK_TOKEN")
    GROUP_ID = int(os.getenv("GROUP_ID", 0))

    vk_session = vk_api.VkApi(token=VK_TOKEN)
    longpoll = VkBotLongPoll(vk_session, GROUP_ID)
    vk = vk_session.get_api()

    print("✅ Бот запущен и ждёт сообщений...")
    print("На любое сообщение отвечает: Привет!")

    for event in longpoll.listen():
        if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
            try:
                user_id = event.obj.message['from_id']
                user_text = event.obj.message['text']
                print(f"Сообщение от {user_id}: {user_text}")
                vk.messages.send(
                    user_id=user_id,
                    message="Привет! 🤖",
                    random_id=get_random_id()
                )
                print("Ответ: Привет! 🤖")
            except Exception as e:
                print(f"Ошибка: {e}")

# --- 3. ЗАПУСКАЕМ ОБА ПРОЦЕССА ОДНОВРЕМЕННО ---
if __name__ == '__main__':
    # Запускаем веб-сервер в отдельном потоке
    web_thread = threading.Thread(target=run_web)
    web_thread.start()
    # Запускаем бота в основном потоке
    run_bot()
