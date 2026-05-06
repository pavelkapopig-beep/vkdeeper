from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Получаем токены из переменных окружения
VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
VK_SECRET_KEY = os.getenv('VK_SECRET_KEY')

@app.route('/', methods=['GET', 'POST'])
def vk_callback():
    if request.method == 'GET':
        # Ответ для мониторинга Render и проверки работоспособности
        return 'VK Bot is running and ready to receive messages', 200

    # Обработка POST‑запроса от VK Callback API
    data = request.json

    # Проверка секретного ключа для безопасности
    if data.get('secret') != VK_SECRET_KEY:
        print("Invalid secret key")
        return 'error', 400

    # Обработка события нового сообщения
    if data.get('type') == 'message_new':
        object_data = data['object']['message']
        user_id = object_data['from_id']
        text = object_data.get('text', '').lower()

        # Проверка на ключевые слова приветствия
        greetings = ['привет', 'здравствуйте', 'добрый день', 'хай', 'hello']
        if any(greeting in text for greeting in greetings):
            send_message(user_id, 'Здравствуйте! Чем могу помочь?')

        return 'ok'

    return 'ok'

def send_message(user_id, message):
    """Отправка сообщения через VK API с обработкой ошибок"""
    try:
        url = 'https://api.vk.com/method/messages.send'
        params = {
            'user_id': user_id,
            'message': message,
            'access_token': VK_GROUP_TOKEN,
            'v': '5.131'
        }
        response = requests.post(url, params=params, timeout=10)

        if response.status_code != 200:
            print(f"Error sending message: {response.text}")
            return False

        response_data = response.json()
        if 'error' in response_data:
            print(f"VK API error: {response_data['error']}")
            return False

        return True

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    """Endpoint для проверки здоровья сервиса"""
    return jsonify({'status': 'ok', 'service': 'vk-bot'})

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Тестовый endpoint — можно проверить в браузере"""
    return jsonify({
        'status': 'test ok',
        'message': 'Бот успешно запущен и готов к работе'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"Starting VK bot on port {port}")
    app.run(host='0.0.0.0', port=port)
