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


    data = request.json
    print(f"=== ПОЛУЧЕН НОВЫЙ ЗАПРОС ===")
    print(f"Тип запроса: {data.get('type')}")

    # Логируем всю структуру данных для отладки
    print(f"Полная структура данных: {data}")

    # Обработка запроса на подтверждение сервера
    if data.get('type') == 'confirmation':
        print("✅ Подтверждение сервера: возвращаем токен")
        return VK_CONFIRMATION_TOKEN, 200

    # Обработка нового сообщения
    if data.get('type') == 'message_new':
        print("📩 ПОЛУЧЕНО НОВОЕ СООБЩЕНИЕ")

        # Безопасное извлечение данных
        if 'object' in data and 'message' in data['object']:
            message_data = data['object']['message']
            user_id = message_data['from_id']
            peer_id = message_data['peer_id']
            text = message_data.get('text', '')
            date = message_data.get('date', 'N/A')

            # Подробная информация о сообщении в логах
            print(f"  👤 ID пользователя: {user_id}")
            print(f"  💬 Peer ID (куда отвечать): {peer_id}")
            print(f"  📝 Текст сообщения: '{text}'")
            print(f"  ⏰ Время получения: {date}")
            print(f"  🔢 ID сообщения: {message_data.get('id', 'N/A')}")
            print(f"  🆔 Out (исходящее): {message_data.get('out', 'N/A')}")

            # Отправляем ответ «Привет!» на ЛЮБОЕ сообщение
            print("  🚀 Отправляем ответ: 'Привет!'")
            send_message(peer_id, 'Привет!')
            print("  ✅ Ответ успешно отправлен")
            return 'ok', 200
        else:
            print("❌ Ошибка: неверная структура данных в сообщении")
            return 'error', 400

    print("⚠️ Неизвестный тип запроса, возвращаем 'ok'")
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
        response = requests.post(url, params=params, timeout=10)
        print(f"  🌐 VK API response: {response.status_code}")
        print(f"  📄 Полный ответ VK API: {response.text}")

        if response.status_code != 200:
            print(f"❌ Ошибка отправки сообщения: {response.text}")
            return False

        response_data = response.json()
        if 'error' in response_data:
            print(f"❌ VK API error: {response_data['error']}")
            return False

        print(f"✅ Сообщение успешно отправлено (ID: {response_data.get('response', 'N/A')})")
        return True

    except requests.exceptions.RequestException as e:
        print(f"❌ Ошибка сети: {e}")
        return False
    except Exception as e:
        print(f"❌ Неожиданная ошибка: {e}")
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
    print(f"🚀 Запуск VK бота на порту {port}")
    app.run(host='0.0.0.0', port=port)
