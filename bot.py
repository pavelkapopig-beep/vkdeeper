import os
import logging
import random
import time
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

# Папка с картинками на Bothost (укажите правильный путь)
IMAGES_FOLDER = "/app/images/"  # ← ЭТОТ ПУТЬ МОЖЕТ ОТЛИЧАТЬСЯ

# ID загруженных картинок
PHOTO_IDS = {}

def upload_all_images(vk_session):
    """Загружает все картинки из папки images в ВК"""
    global PHOTO_IDS
    upload = VkUpload(vk_session)
    
    # Список файлов для загрузки
    images = {
        "ask": "ask.jpg",
        "start": "start.jpg",
        "img1": "img1.jpg",
        "img2": "img2.jpg",
        "img3": "img3.jpg",
        "img4": "img4.jpg",
        "img5": "img5.jpg",
        "error": "error.jpg",
        "final": "final.jpg"
    }
    
    logging.info("📸 Загружаю картинки в ВК...")
    
    for key, filename in images.items():
        filepath = os.path.join(IMAGES_FOLDER, filename)
        try:
            if os.path.exists(filepath):
                photo = upload.photo_messages(filepath)
                photo_id = f"photo{photo[0]['owner_id']}_{photo[0]['id']}"
                PHOTO_IDS[key] = photo_id
                logging.info(f"✅ Загружена {key}: {photo_id}")
            else:
                logging.warning(f"⚠️ Файл не найден: {filepath}")
        except Exception as e:
            logging.error(f"❌ Ошибка загрузки {key}: {e}")
    
    logging.info(f"📸 Загружено {len(PHOTO_IDS)} из {len(images)} картинок")

INITIATION_STEPS = [
    {"text": "😏 Приклони колено повторяй за мной!\nГовори когда надо КЛЯНУСЬ!", "image": "start", "need_confirm": False},
    {"text": "Так клянемся же:\nНет предела Радиусу...\n\nКлянемся пространством Минковского...\n\nКлянемся?", "image": "img1", "need_confirm": True},
    {"text": "Клянемся псевдосферой Лобачевского...\n\nКлянемся?", "image": "img2", "need_confirm": True},
    {"text": "Клянемся законами торсионных полей...\n\nКлянемся? жечь дотла...\n\nКлянемся?", "image": "img3", "need_confirm": True},
    {"text": "Свято помнить, что плоха та теория...\n\nКЛЯНЁМСЯ?", "image": "img4", "need_confirm": True},
    {"text": "Не путать плюс с минусом...\n\nКлянемся?", "image": "img5", "need_confirm": True}
]

SYSTEM_PROMPT = """Ты Сэр Исаак Ньютон. Ворчливый скряга, безумный физик. Ругаешься: "Сила трения тебе в задницу!", "Закон сохранения энергии!", "Яблоко тебе на макушку!" После ругани даёшь ответ."""

def send_message(vk, user_id, text, image_key=None):
    attachment = PHOTO_IDS.get(image_key, "") if image_key else ""
    vk.messages.send(
        user_id=user_id,
        message=text,
        random_id=random.randint(1, 999999),
        attachment=attachment
    )

def get_deepseek_response(user_message, history):
    try:
        messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history + [{"role": "user", "content": user_message}]
        resp = client.chat.completions.create(model="deepseek-chat", messages=messages, max_tokens=800, temperature=0.9)
        return resp.choices[0].message.content
    except Exception as e:
        logging.error(f"Ошибка DeepSeek: {e}")
        return "Закон сохранения энергии, блин! Техника сломалась..."

def main():
    logging.info("✅ Сэр Исаак Ньютон запущен!")
    
    vk_session = VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
    # ЗАГРУЖАЕМ КАРТИНКИ ИЗ ПАПКИ
    upload_all_images(vk_session)
    
    states, histories, init_step = {}, {}, {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me:
            msg = event.text.strip().lower()
            uid = event.user_id
            logging.info(f"Сообщение от {uid}: {msg}")
            
            if uid not in states:
                states[uid] = "menu"
                send_message(vk, uid, "🧙‍♂️ Приветствую!\n\n1️⃣ Поговорить\n2️⃣ Посвящение\n\nНапиши 1 или 2", "ask")
                continue
            
            if states[uid] == "menu":
                if msg in ["1", "поговорить"]:
                    states[uid] = "chat"
                    send_message(vk, uid, "Ох, давай болтай. Что хотел сказать?")
                elif msg in ["2", "посвящение", "секта"]:
                    states[uid] = "initiation"
                    init_step[uid] = -1
                    send_message(vk, uid, "Готов произнести клятву?\n\nНапиши ДА или НЕТ", "ask")
                else:
                    send_message(vk, uid, "Пиши 1 или 2!")
                continue
            
            if states[uid] == "initiation":
                step = init_step.get(uid, -1)
                if step == -1:
                    if msg == "да":
                        init_step[uid] = 0
                        step_data = INITIATION_STEPS[0]
                        send_message(vk, uid, step_data["text"], step_data["image"])
                        if not step_data["need_confirm"]:
                            time.sleep(1)
                            init_step[uid] = 1
                            send_message(vk, uid, INITIATION_STEPS[1]["text"], INITIATION_STEPS[1]["image"])
                    elif msg == "нет":
                        states[uid] = "menu"
                        send_message(vk, uid, "Ну и проваливай, бес!", "error")
                    else:
                        send_message(vk, uid, "Ты мне втираешь какую-то дичь!\nЯ тебя проклинаю, бес!", "error")
                    continue
                
                if 0 <= step < len(INITIATION_STEPS):
                    if INITIATION_STEPS[step]["need_confirm"]:
                        if msg == "клянусь":
                            nxt = step + 1
                            if nxt < len(INITIATION_STEPS):
                                init_step[uid] = nxt
                                send_message(vk, uid, INITIATION_STEPS[nxt]["text"], INITIATION_STEPS[nxt]["image"])
                            else:
                                states[uid] = "chat"
                                send_message(vk, uid, "🎉 ПОЗДРАВЛЯЮ! ТЫ ПРОШЁЛ ПОСВЯЩЕНИЕ! 🎉\n\nГимн: https://www.youtube.com/watch?v=UPSDSKaVXA8\nПодпишись: https://t.me/SektaNewtona", "final")
                        else:
                            send_message(vk, uid, "Ты мне втираешь какую-то дичь!\nЯ тебя проклинаю, бес!", "error")
                    continue
            
            if states[uid] == "chat":
                if msg in ["меню", "стоп", "выйти"]:
                    states[uid] = "menu"
                    send_message(vk, uid, "Возвращаю в меню! Напиши 1 или 2", "ask")
                    continue
                
                if uid not in histories:
                    histories[uid] = []
                hist = histories[uid][-10:] if len(histories[uid]) > 10 else histories[uid]
                answer = get_deepseek_response(msg, hist)
                histories[uid].append({"role": "user", "content": msg})
                histories[uid].append({"role": "assistant", "content": answer})
                if len(histories[uid]) > 20:
                    histories[uid] = histories[uid][-20:]
                send_message(vk, uid, answer)

if __name__ == '__main__':
    main()
