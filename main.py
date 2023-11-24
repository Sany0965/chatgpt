import telebot
from telebot import types
import openai

# Ваш токен от BotFather
TOKEN = 'Ваштокен'

# Ваш API-ключ от OpenAI
OPENAI_API_KEY = 'ключOpenAI'
openai.api_key = OPENAI_API_KEY

# Словарь для хранения данных о профиле пользователя
user_profiles = {}

# Создаем объект бота
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    user_profiles[user_id] = {'name': message.from_user.first_name,
                               'id': user_id,
                               'username': message.from_user.username,
                               'questions_asked': 0,
                               'remaining_daily_queries': 3}

    keyboard = types.InlineKeyboardMarkup()
    keyboard.row(types.InlineKeyboardButton("🔵 Задать вопрос", callback_data='ask_question'),
                 types.InlineKeyboardButton("🔴 Профиль", callback_data='show_profile'))
    keyboard.row(types.InlineKeyboardButton("⚫️ Исходный код", callback_data='source_code'),
                 types.InlineKeyboardButton("🟠 Связаться с админом", callback_data='contact_admin'))

    bot.send_message(user_id, 'Привет! Я бот, подключенный к ChatGPT 🤖', reply_markup=keyboard)

@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    user_id = call.message.chat.id

    if call.data == 'ask_question':
        # Предложим пользователю ввести свой запрос
        bot.send_message(user_id, "Введите ваш запрос:")
        # Установим следующий шаг для этого пользователя
        bot.register_next_step_handler(call.message, process_user_input)
    elif call.data == 'show_profile':
        show_profile(user_id)
    elif call.data == 'source_code':
        send_github_link(user_id)
    elif call.data == 'contact_admin':
        contact_admin(user_id)

def process_user_input(message):
    user_id = message.chat.id

    # Получаем текст вопроса от пользователя
    user_query = message.text

    # Добавляем информацию о вопросе в профиль пользователя
    user_profiles[user_id]['questions_asked'] += 1
    user_profiles[user_id]['remaining_daily_queries'] -= 1

    # Отправляем пользователю сообщение о том, что бот думает
    bot.send_message(user_id, "Думаю🧠...")

    # Отправляем запрос к GPT-3
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=user_query,
        max_tokens=150
    )

    # Извлекаем ответ от GPT-3
    answer = response.choices[0].text.strip()

    # Отправляем ответ пользователю
    bot.send_message(user_id, answer)

def show_profile(user_id):
    profile_data = user_profiles[user_id]

    profile_text = (
        f"Имя: {profile_data['name']}\n"
        f"ID: {profile_data['id']}\n"
        f"Имя пользователя: {profile_data['username']}\n"
        f"Количество вопросов: {profile_data['questions_asked']}\n"
        f"Осталось запросов за день: {profile_data['remaining_daily_queries']}"
    )

    bot.send_message(user_id, profile_text)

def send_github_link(user_id):
    bot.send_message(user_id, "Исходный код бота доступен на GitHub: https://github.com/your_username/your_repository")

def contact_admin(user_id):
    bot.send_message(user_id, "Произошла ошибка? Пиши сюда https://t.me/pizzaway")

@bot.callback_query_handler(func=lambda call: call.data == 'back_to_menu')
def back_to_menu_callback(call):
    user_id = call.message.chat.id
    start(user_id)

if __name__ == "__main__":
    bot.polling(none_stop=True)

