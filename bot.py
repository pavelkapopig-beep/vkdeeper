import os
import time
import logging
from dotenv import load_dotenv
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType

load_dotenv()
logging.basicConfig(level=logging.INFO)

VK_TOKEN = os.getenv('VK_TOKEN')
if not VK_TOKEN:
    logging.error("Ошибка: не найден VK_TOKEN в переменных окружения!")
    exit(1)

def main():
    logging.info("✅ Бот запущен и подключается к Long Poll API...")
    try:
        vk_session = VkApi(token=VK_TOKEN)
        longpoll = VkLongPoll(vk_session)

        for event in longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
                user_message = event.text.lower()
                user_id = event.user_id

                logging.info(f"Сообщение от {user_id}: {user_message}")

                if user_message == "привет":
                    answer = "Привет! Я бот, работающий на Long Poll API!"
                elif user_message == "как дела?":
                    answer = "Отлично! Жду твоих сообщений :)"
                elif user_message == "пока":
                    answer = "До свидания! Напиши 'привет' в любой момент."
                else:
                    answer = "Извини, я понимаю только команды: 'привет', 'как дела?', 'пока'."

                vk_session.method('messages.send', {
                    'user_id': event.user_id,
                    'message': answer,
                    'random_id': 0
                })

    except Exception as e:
        logging.error(f"❌ Произошла ошибка: {e}")

if __name__ == '__main__':
    main()
