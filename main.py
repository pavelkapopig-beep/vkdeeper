import vk_api
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.utils import get_random_id
import os

# Берём токен из переменной окружения на Render
VK_TOKEN = os.getenv("VK_TOKEN")
GROUP_ID = int(os.getenv("GROUP_ID", 0))

# Подключаемся к ВК
vk_session = vk_api.VkApi(token=VK_TOKEN)
longpoll = VkBotLongPoll(vk_session, GROUP_ID)
vk = vk_session.get_api()

print("✅ Бот запущен и ждёт сообщений...")
print("На любое сообщение отвечает: Привет!")

# Главный цикл — слушаем сообщения
for event in longpoll.listen():
    if event.type == VkBotEventType.MESSAGE_NEW and event.from_user:
        try:
            user_id = event.obj.message['from_id']
            user_text = event.obj.message['text']

            print(f"Сообщение от {user_id}: {user_text}")

            # Отправляем простой ответ
            vk.messages.send(
                user_id=user_id,
                message="Привет! 🤖",
                random_id=get_random_id()
            )
            print("Ответ: Привет! 🤖")

        except Exception as e:
            print(f"Ошибка: {e}")
