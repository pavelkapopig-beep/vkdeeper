from flask import Flask, request, jsonify
import requests
import os

app = Flask(__name__)

# Получаем токен из переменных окружения
VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
VK_CONFIRMATION_TOKEN = '56d9cc7e'  # Токен подтверждения из настроек ВК

@app.route('/', methods=['GET', 'POST'])
def vk_callback():
    if request.method == 'GET':
        return 'VK Bot is running and ready to receive messages', 200

    # Обработка POST‑запроса от VK Callback API
    data = request.json
    print(f"Received data: {data}")  # Отладочная печать — поможет увидеть входящие данные


    # Обработка запроса на подтверждение сервера
    if data.get('type') == 'confirmation':
        print("Confirmation request received")
        return VK_CONFIRMATION_TOKEN, 200

    # Обработка нового сообщения
    if data.get('type') == 'message_new':
        print("Message_new event detected")

        # Безопасное извлечение данных
        if 'object' in data and 'message' in data['object']:
            message_data = data['object']['message']
            user_id = message_data['from_id']
            text = message_data.get('text', '').lower()
            print(f"User {user_id} sent: {text}")

            # Отправляем ответ «Привет!» на ЛЮБОЕ сообщение
            send_message(user_id, 'Привет!')
            return 'ok', 200
        else:
            print("Invalid message structure")
            return 'error', 400

    return 'ok', 200

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
        print(f"VK API response: {response.status_code}, {response.text}")  # Логирование ответа VK API

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
