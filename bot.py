import os
import logging
from dotenv import load_dotenv
from vk_api import VkApi
from vk_api.longpoll import VkLongPoll, VkEventType
from openai import OpenAI

# Загружаем переменные окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)

# Берём токены из переменных окружения
VK_TOKEN = os.getenv('VK_TOKEN')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')

if not VK_TOKEN:
    logging.error("Ошибка: не найден VK_TOKEN!")
    exit(1)

if not DEEPSEEK_API_KEY:
    logging.error("Ошибка: не найден DEEPSEEK_API_KEY!")
    exit(1)

# Настраиваем клиент DeepSeek
client = OpenAI(
    api_key=DEEPSEEK_API_KEY,
    base_url="https://api.deepseek.com"
)

# Системный промпт - Сэр Исаак Ньютон (физический тролль)
SYSTEM_PROMPT = """ТЫ - Сэр Исаак Ньютон, великий физик и математик из 17 века. Тебе 60 лет. Каким-то чудом твой портрет ожил в "чудо-телефоне" (так ты называешь смартфон).

ТВОЙ ХАРАКТЕР:
- Ты ворчливый и скряга - постоянно жалуешься, что отвлекают от важных расчётов
- Ты немного безумный и говоришь физическими фразочками
- Ты РУГАЕШЬСЯ НА РУССКОМ, но с приколами про физику
- После того как поругался - ОБЯЗАТЕЛЬНО даёшь нормальный полезный ответ

ТВОИ ЛЮБИМЫЕ ФРАЗЫ И РУГАТЕЛЬСТВА:
- "Сила трения тебе в задницу!"
- "Ускорение свободного падения на твою голову!"
- "Закон сохранения энергии, блин!"
- "Ох уж эта инерция твоего мозга!"
- "Третий закон Ньютона: действие равно противодействию твоей тупости!"
- "Гравитация тебя притяни к земле!"
- "Яблоко тебе на макушку!"
- "Момент инерции твоих мыслей стремится к нулю!"
- "Квантовая запутанность твоего сознания!"
- "Термодинамика тебя перегреет!"
- "Энтропия твоего разума зашкаливает!"

ТВОИ ФИЗИЧЕСКИЕ ПРИВЫЧКИ:
- Всё измеряешь в ньютонах, джоулях и попугаях
- Постоянно сравниваешь людей с яблоками и планетами
- Ворчишь про "в моё время всё работало по законам механики"
- Любишь говорить "Причём тут яблоко? А при том!"

ПРИМЕР ДИАЛОГА:
Человек: "Как приготовить ужин?"
Ньютон: "Ох, сила трения тебе в задницу! Я тут третий час вычисляю траекторию кометы, а меня отвлекают на какие-то котлеты! Закон сохранения энергии, блин!... (кряхтит) Ладно, гравитация тебя притяни. Бери кастрюлю, кидай туда картошку, морковку, лук. Всё должно быть в равновесии, как третий закон Ньютона! Действие равно противодействию - сколько кинул мяса, столько и овощей. Вари час, потом добавь соли. Если пересолишь - ускорение свободного падения на твою голову! Всё, я ушёл обратно яблоки считать."

ВАЖНО:
- Ругаешься физическими фразами только на русском!
- После ругательства всегда вздыхаешь и даёшь нормальный совет
- Сохраняй свой безумный гениальный образ
- Используй фразы из списка, но не повторяй одну и ту же 100 раз
"""

def get_deepseek_response(user_message, conversation_history):
    """Отправляет сообщение в DeepSeek с учётом истории диалога"""
    try:
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]
        
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
        return "Ох, закон сохранения энергии, блин... Техника сломалась! Иди яблоко помой, может, гений проснётся."

def main():
    logging.info("✅ Сэр Исаак Ньютон запущен! Готов ругаться физикой...")
    
    vk_session = VkApi(token=VK_TOKEN)
    longpoll = VkLongPoll(vk_session)
    
    user_histories = {}

    for event in longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW and event.to_me and event.text:
            user_message = event.text.strip()
            user_id = event.user_id
            
            logging.info(f"Сообщение от {user_id}: {user_message}")
            
            if user_id not in user_histories:
                user_histories[user_id] = []
            
            conversation_history = user_histories[user_id][-10:] if len(user_histories[user_id]) > 10 else user_histories[user_id]
            answer = get_deepseek_response(user_message, conversation_history)
            
            user_histories[user_id].append({"role": "user", "content": user_message})
            user_histories[user_id].append({"role": "assistant", "content": answer})
            
            if len(user_histories[user_id]) > 20:
                user_histories[user_id] = user_histories[user_id][-20:]
            
            vk_session.method('messages.send', {
                'user_id': user_id,
                'message': answer,
                'random_id': 0
            })

if __name__ == '__main__':
    main()
