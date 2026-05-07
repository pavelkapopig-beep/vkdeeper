import os
import logging
import random
import time
import requests
from dotenv import load_dotenv
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.upload import VkUpload
from openai import OpenAI

load_dotenv()
logging.basicConfig(level=logging.INFO)

VK_TOKEN = os.getenv('VK_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

if not VK_TOKEN:
    logging.error("Ошибка: не найден VK_TOKEN!")
    exit(1)

if not DEEPSEEK_API_KEY:
    logging.error("Ошибка: не найден DEEPSEEK_API_KEY!")
    exit(1)

client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Ссылки на картинки (Imgur)
IMAGE_URLS = {
    "ask": "https://i.imgur.com/2h9vzFt.jpg",
    "start": "https://i.imgur.com/7Yy6LY8.jpg",
    "img1": "https://i.imgur.com/MoufF46.jpg",
    "img2": "https://i.imgur.com/2webgKO.jpg",
    "img3": "https://i.imgur.com/Y74qXlM.jpg",
    "img4": "https://i.imgur.com/GmqT1ti.jpg",
    "img5": "https://i.imgur.com/pVialqO.jpg",
    "error": "https://i.imgur.com/57Eo9et.jpg",
    "final": "https://i.imgur.com/7s33CuO.jpg"
}

# Для хранения ID загруженных фото
PHOTO_IDS = {}

def upload_all_images(vk_session):
    """Загружает все картинки в ВК напрямую через API"""
    global PHOTO_IDS
    upload = VkUpload(vk_session)
    
    logging.info("📸 Загружаю картинки в ВК...")
    
    for key, url in IMAGE_URLS.items():
        try:
            # Скачиваем картинку по ссылке
            response = requests.get(url, timeout=30)
            if response.status_code != 200:
                logging.error(f"Не удалось скачать {key}: статус {response.status_code}")
                continue
            
            # Сохраняем во временный файл
            temp_path = f"/tmp/{key}.jpg"
            with open(temp_path, "wb") as f:
                f.write(response.content)
            
            # Загружаем в ВК
            photo = upload.photo_messages(temp_path)
            photo_id = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
            PHOTO_IDS[key] = photo_id
            
            # Удаляем временный файл
            os.remove(temp_path)
            
            logging.info(f"✅ Загружена: {key} -> {photo_id}")
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки {key}: {e}")
    
    logging.info(f"📸 Итого загружено: {len(PHOTO_IDS)} из {len(IMAGE_URLS)}")

# Сценарий посвящения (сокращённый для читаемости)
INITIATION_STEPS = [
    {"text": "😏 Приклони колено повторяй за мной!\nГовори когда надо КЛЯНУСЬ!", "image": "start", "need_confirm": False},
    {"text": "Так клянемся же:\nНет предела Радиусу бесконечного чувства волнения...\n\nКлянемся пространством Минковского...\n\nКлянемся?", "image": "img1", "need_confirm": True},
    {"text": "Клянемся псевдосферой Лобачевского...\n\nКлянемся?", "image": "img2", "need_confirm": True},
    {"text": "Клянемся законами торсионных полей...\n\nКлянемся? жечь дотла свою жизнь...\n\nКлянемся?", "image": "img3", "need_confirm": True},
    {"text": "Свято помнить, что плоха та теория...\n\nКЛЯНЁМСЯ?", "image": "img4", "need_confirm": True},
    {"text": "Не путать плюс с минусом, Ферма с Ферми...\n\nКлянемся?", "image": "img5", "need_confirm": True}
]

SYSTEM_PROMPT = """Ты Сэр Исаак Ньютон. Тебе 60 лет. Ты ворчливый скряга и безумный физик. Глава Секты Ньютона.

Когда выбирают "поговорить" - общаешься как ворчливый старик. Ругаешься физическими фразами: "Сила трения тебе в задницу!", "Закон сохранения энергии!", "Яблоко тебе на макушку!"

После ругани даёшь полезный ответ."""

def send_message(vk, user_id, text, image_key=None):
    attachment = ""
    if image_key and image_key in PHOTO_IDS:
        attachment = PHOTO_IDS[image_key]
    
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 999999),
        attachment=attachment
    )

def get_deepseek_response(user_message, conversation_history):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        messages.extend(conversation_history)
        messages.append({"role": "user", "content": user_message})
        
        response = client.chat.completions.create(
            model="deepseek-chat",
            messages=messages,
            max_tokens=800,
            temperature=0.9
        )
        return response.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка DeepSeek: {e}")
        return "Закон сохранения энергии, блин! Техника сломалась..."

def main():
    logging.info("✅ Сэр Исаак Ньютон запущен!")
    
    vk_session = VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
    # АВТОМАТИЧЕСКАЯ ЗАГРУЗКА КАРТИНОК
    upload_all_images(vk_session)
    
    user_states = {}
    user_histories = {}
    user_initiation_step = {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            user_message = event.text.strip().lower()
            user_id = event.user_id
            
            logging.info(f"Сообщение от {user_id}: {user_message}")
            
            if user_id not in user_states:
                user_states[user_id] = "menu"
                send_message(vk, user_id, 
                    "🧙‍♂️ Приветствую, странник!\n\n1️⃣ Поговорить\n2️⃣ Посвящение в Секту\n\nНапиши 1 или 2", "ask")
                continue
            
            if user_states[user_id] == "menu":
                if user_message in ["1", "поговорить"]:
                    user_states[user_id] = "chat"
                    send_message(vk, user_id, "Ох, давай болтай. Что хотел сказать?")
                    continue
                elif user_message in ["2", "посвящение", "секта"]:
                    user_states[user_id] = "initiation"
                    user_initiation_step[user_id] = -1
                    send_message(vk, user_id, 
                        "Приветствую! Готов произнести клятву?\n\nНапиши ДА или НЕТ", "ask")
                    continue
                else:
                    send_message(vk, user_id, "Пиши 1 (поговорить) или 2 (посвящение)!")
                    continue
            
            if user_states[user_id] == "initiation":
                step = user_initiation_step.get(user_id, -1)
                
                if step == -1:
                    if user_message == "да":
                        user_initiation_step[user_id] = 0
                        step_data = INITIATION_STEPS[0]
                        send_message(vk, user_id, step_data["text"], step_data["image"])
                        if not step_data["need_confirm"]:
                            time.sleep(1)
                            user_initiation_step[user_id] = 1
                            next_step = INITIATION_STEPS[1]
                            send_message(vk, user_id, next_step["text"], next_step["image"])
                    elif user_message == "нет":
                        user_states[user_id] = "menu"
                        send_message(vk, user_id, "Ну и проваливай, бес!", "error")
                    else:
                        send_message(vk, user_id, "Ты мне втираешь какую-то дичь!\nЯ тебя проклинаю, бес!", "error")
                    continue
                
                if step >= 0 and step < len(INITIATION_STEPS):
                    current_step = INITIATION_STEPS[step]
                    
                    if current_step["need_confirm"]:
                        if user_message == "клянусь":
                            next_step_idx = step + 1
                            if next_step_idx < len(INITIATION_STEPS):
                                user_initiation_step[user_id] = next_step_idx
                                send_message(vk, user_id, INITIATION_STEPS[next_step_idx]["text"], INITIATION_STEPS[next_step_idx]["image"])
                            else:
                                user_states[user_id] = "chat"
                                send_message(vk, user_id, 
                                    f"🎉 ПОЗДРАВЛЯЮ! ТЫ ПРОШЁЛ ПОСВЯЩЕНИЕ! 🎉\n\n"
                                    f"Гимн секты: https://www.youtube.com/watch?v=UPSDSKaVXA8\n"
                                    f"Подпишись: https://t.me/SektaNewtona", "final")
                        else:
                            send_message(vk, user_id, "Ты мне втираешь какую-то дичь!\nЯ тебя проклинаю, бес!", "error")
                    continue
            
            if user_states[user_id] == "chat":
                if user_message in ["меню", "стоп", "выйти"]:
                    user_states[user_id] = "menu"
                    send_message(vk, user_id, "Возвращаю в меню! Напиши 1 или 2", "ask")
                    continue
                
                if user_id not in user_histories:
                    user_histories[user_id] = []
                
                conversation_history = user_histories[user_id][-10:] if len(user_histories[user_id]) > 10 else user_histories[user_id]
                answer = get_deepseek_response(user_message, conversation_history)
                
                user_histories[user_id].append({"role": "user", "content": user_message})
                user_histories[user_id].append({"role": "assistant", "content": answer})
                
                if len(user_histories[user_id]) > 20:
                    user_histories[user_id] = user_histories[user_id][-20:]
                
                send_message(vk, user_id, answer)
                continue

if __name__ == '__main__':
    main()
