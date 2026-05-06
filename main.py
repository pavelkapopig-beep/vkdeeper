from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Получаем токены из переменных окружения
VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
VK_SECRET_KEY = os.getenv('VK_SECRET_KEY')

@app.route('/', methods=['POST'])
def vk_callback():
    data = request.json

    # Проверка секретного ключа
    if data.get('secret') != VK_SECRET_KEY:
        return 'error', 400

    # Обработка нового сообщения
    if data.get('type') == 'message_new':
        object_data = data['object']['message']
        user_id = object_data['from_id']
        text = object_data.get('text', '').lower()

        # Ответ на «привет»
        if 'привет' in text:
            send_message(user_id, 'Здравствуйте! Чем могу помочь?')

        return 'ok'

    return 'ok'

def send_message(user_id, message):
    url = 'https://api.vk.com/method/messages.send'
    params = {
        'user_id': user_id,
        'message': message,
        'access_token': VK_GROUP_TOKEN,
        'v': '5.131'
    }
    requests.post(url, params=params)

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.getenv('PORT', 5000)))
