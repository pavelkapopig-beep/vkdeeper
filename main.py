from flask import Flask, request, jsonify
import requests
import os
import json

app = Flask(__name__)

# Получаем токен из переменных окружения
VK_GROUP_TOKEN = os.getenv('VK_GROUP_TOKEN')
VK_CONFIRMATION_TOKEN = '56d9cc7e'  # Токен подтверждения из настроек ВК

@app.route('/', methods=['GET', 'POST'])
def vk_callback():
    print("=== ПОЛУЧЕН НОВЫЙ ЗАПРОС ===")

    if request.method == 'GET':
        print("GET-запрос получен (мониторинг Render)")
        return 'VK Bot is running and ready to receive messages', 200

    # Парсим JSON
    try:
        data = request.json
        print(f"RAW данные запроса: {json.dumps(data, ensure_ascii=False, indent=2)}")
    except Exception as e:
        print(f"Ошибка парсинга JSON: {e}")
        return 'error', 400

    # Логируем тип запроса
    event_type = data.get('type')
    print(f"Тип события: {event_type}")

    # Обработка подтверждения сервера
    if event_type == 'confirmation':
        print("✅ Получен запрос на подтверждение сервера")
        return VK_CONFIRMATION_TOKEN, 200

    # Обработка нового сообщения
    elif event_type == 'message_new':
        print("📩 ПОЛУЧЕНО НОВОЕ СООБЩЕНИЕ")

        # Безопасное извлечение данных
        if 'object' not in data:
            print("❌ В данных нет поля 'object'")
            return 'error', 400
        if 'message' not in data['object']:
            print("❌ В 'object' нет поля 'message'")
            return 'error', 400

        message_data = data['object']['message']
        user_id = message_data.get('from_id')
        peer_id = message_data.get('peer_id')
        text = message_data.get('text', '')

        print(f"  👤 ID пользователя: {user_id}")
        print(f"  💬 Peer ID: {peer_id}")
        print(f"  📝 Текст сообщения: '{text}'")

        # Проверка, что peer_id существует
        if not peer_id:
            print("❌ Peer ID не найден — невозможно отправить ответ")
            return 'error', 400

        # Отправляем ответ
        print("  🚀 Пытаемся отправить ответ: 'Привет!'")
        success = send_message(peer_id, 'Привет!')
        if success:
            print("  ✅ Ответ успешно отправлен")
        else:
            print("  ❌ Ошибка отправки ответа")
        return 'ok', 200

    else:
        print(f"⚠️ Неизвестный тип события: {event_type}")
        return 'ok', 200

def send_message(peer_id, message):
    """Отправка сообщения через VK API с обработкой ошибок"""
    try:
        url = 'https://api.vk.com/method/messages.send'
        params = {
            'peer_id': peer_id,
            'message': message,
            'access_token': VK_GROUP_TOKEN,
            'v': '5.131'
        }
        print(f"  🌐 Отправляем запрос к VK API: {params}")
        response = requests.post(url, params=params, timeout=10)
        print(f"  🌐 VK API response: {response.status_code}")
        print(f"  📄 Полный ответ VK API: {response.text}")

        if response.status_code != 200:
            print(f"❌ Ошибка HTTP: {response.status_code}")
            return False

        response_data = response.json()
        if 'error' in response_data:
            error_code = response_data['error'].get('error_code')
            error_msg = response_data['error'].get('error_msg')
            print(f"❌ VK API error {error_code}: {error_msg}")
            return False

        print(f"✅ Сообщение отправлено (ID: {response_data.get('response')})")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
        return False

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({'status': 'ok', 'service': 'vk-bot'})

@app.route('/test', methods=['GET'])
def test_endpoint():
    return jsonify({
        'status': 'test ok',
        'message': 'Бот успешно запущен и готов к работе'
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    print(f"🚀 Запуск VK бота на порту {port}")
    app.run(host='0.0.0.0', port=port)
