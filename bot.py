import os
import logging
import random
import time
from dotenv import load_dotenv
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
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

# Ссылка на ваши картинки на GitHub (УЖЕ ИСПРАВЛЕНА)
GITHUB_IMAGES = "https://raw.githubusercontent.com/pavelkapopig-beep/vkdeeper/main/images/"

IMAGES = {
    "ask": f"{GITHUB_IMAGES}ask.jpg",
    "start": f"{GITHUB_IMAGES}start.jpg",
    "img1": f"{GITHUB_IMAGES}img1.jpg",
    "img2": f"{GITHUB_IMAGES}img2.jpg",
    "img3": f"{GITHUB_IMAGES}img3.jpg",
    "img4": f"{GITHUB_IMAGES}img4.jpg",
    "img5": f"{GITHUB_IMAGES}img5.jpg",
    "error": f"{GITHUB_IMAGES}error.jpg",
    "final": f"{GITHUB_IMAGES}final.jpg"
}

INITIATION_STEPS = [
    {"text": "😏 Приклони колено повторяй за мной!\nГовори когда надо КЛЯНУСЬ!", "image": "start", "need_confirm": False},
    {"text": "Так клянемся же:\nНет предела Радиусу бесконечного чувства волнения сегодняшних виновников посвящения перед принятием клятвы.\n\nКлянемся пространством Минковского, что его четвертое измерение не властно над любовью к точным наукам\n\nКлянемся?", "image": "img1", "need_confirm": True},
    {"text": "Клянемся псевдосферой Лобачевского, что главным орудием доказательства истины будет логика\nКлянемся смотреть в корень и глубоко проникать в сущность явлений, чтобы познать тонкость выбранных наук\n\nКлянемся?", "image": "img2", "need_confirm": True},
    {"text": "Клянемся законами торсионных полей, что чувство привязанности к любимым предметам не будет обратно пропорционально расстоянию от первого знакомства с ними до перспективы взаимодействия!\n\nКлянемся, что вопреки теории относительности Эйнштейна, наше стремление к познанию будет постоянно и безотносительно\n\nКлянемся! жечь дотла свою жизнь младую на алтаре науки,\nДелать домашку! Не жалея собственных сил!\n\nКлянемся?", "image": "img3", "need_confirm": True},
    {"text": "Свято помнить, что плоха та теория,\nЧто не подтверждается на практикуме!\n\nПравильно и своевременно интерпретировать любой график,\nНезависимо от того, какой стороной он повёрнут!\n\nКЛЯНЁМСЯ?", "image": "img4", "need_confirm": True},
    {"text": "Не путать плюс с минусом, Ферма с Ферми,\nПланка с Капабланкой, закон Вина с сухим законом,\nБойля с Мариоттом и Ильина с Позняком!\n\nПолностью и без потерь собирать урожай с квантовых полей,\n\nКлянемся?", "image": "img5", "need_confirm": True}
]

SYSTEM_PROMPT = """Ты Сэр Исаак Ньютон. Тебе 60 лет. Ты ворчливый скряга и безумный физик. Глава Секты Ньютона.

Когда человек выбирает "поговорить" - ты общаешься как ворчливый старик-физик. Ругаешься физическими фразами: "Сила трения тебе в задницу!", "Закон сохранения энергии, блин!", "Ускорение свободного падения!", "Яблоко тебе на макушку!", "Момент инерции твоих мыслей стремится к нулю!"

После ругани всегда даёшь полезный ответ. Ты скряга, не любишь когда отвлекают."""

def send_message(vk, user_id, text, image_key=None):
    attachment = ""
    if image_key and image_key in IMAGES:
        attachment = IMAGES[image_key]
    
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
        return "Закон сохранения энергии, блин! Техника сломалась... Иди яблоко помой."

def main():
    logging.info("✅ Сэр Исаак Ньютон запущен! Картинки с GitHub")
    
    vk_session = VkApi(token=VK_TOKEN)
    vk = vk_session.get_api()
    longpoll = VkLongPoll(vk_session)
    
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
                    "🧙‍♂️ Приветствую тебя, странник!\n\n"
                    "Ты хочешь:\n"
                    "1️⃣ Поговорить со стариком Ньютоном\n"
                    "2️⃣ Пройти посвящение в Секту Ньютона\n\n"
                    "Напиши 1 или 2", "ask")
                continue
            
            if user_states[user_id] == "menu":
                if user_message in ["1", "поговорить"]:
                    user_states[user_id] = "chat"
                    send_message(vk, user_id, 
                        "Ох, силушка-то... Ладно, давай болтай. Только быстро!\n"
                        "Что хотел сказать?")
                    continue
                elif user_message in ["2", "посвящение", "секта"]:
                    user_states[user_id] = "initiation"
                    user_initiation_step[user_id] = -1
                    send_message(vk, user_id, 
                        "Приветствую тебя странник! Готов произнести клятву и очистить свой ум и разум от ереси?\n\n"
                        "Напиши ДА или НЕТ", "ask")
                    continue
                else:
                    send_message(vk, user_id, 
                        "Я тебя проклинаю, бес! Пиши 1 (поговорить) или 2 (посвящение)!")
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
                        send_message(vk, user_id, "Ну и проваливай, бес! Возвращаюсь в меню.", "error")
                    else:
                        send_message(vk, user_id, 
                            "Ты мне втираешь какую-то дичь\n\nЯ тебя проклинаю, бес!", "error")
                    continue
                
                if step >= 0 and step < len(INITIATION_STEPS):
                    current_step = INITIATION_STEPS[step]
                    
                    if current_step["need_confirm"]:
                        if user_message == "клянусь":
                            next_step_idx = step + 1
                            if next_step_idx < len(INITIATION_STEPS):
                                user_initiation_step[user_id] = next_step_idx
                                next_step = INITIATION_STEPS[next_step_idx]
                                send_message(vk, user_id, next_step["text"], next_step["image"])
                            else:
                                user_states[user_id] = "chat"
                                send_message(vk, user_id, 
                                    f"🎉 ПОЗДРАВЛЯЮ! ТЫ ПРОШЁЛ ПОСВЯЩЕНИЕ! 🎉\n\n"
                                    f"Теперь ты один из нас! С гордостью неси знамя физики и честь Секты Ньютона.\n\n"
                                    f"А сейчас послушай гимн нашей секты:\n"
                                    f"https://www.youtube.com/watch?v=UPSDSKaVXA8&feature=youtu.be\n\n"
                                    f"И подпишись: https://t.me/SektaNewtona", "final")
                        else:
                            send_message(vk, user_id, 
                                "Ты мне втираешь какую-то дичь\n\nЯ тебя проклинаю, бес!", "error")
                    continue
            
            if user_states[user_id] == "chat":
                if user_message in ["меню", "стоп", "выйти"]:
                    user_states[user_id] = "menu"
                    send_message(vk, user_id, 
                        "Возвращаемся в меню!\nНапиши 1 (поговорить) или 2 (посвящение)", "ask")
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
