import telebot
from telebot import types
from config import TOKEN_TELEGRAM
from crud import get_or_create_user, get_random_word, generate_options, add_word_to_user, delete_word_from_user
from db_session import get_session

bot = telebot.TeleBot(TOKEN_TELEGRAM)
user_states = {}

@bot.message_handler(commands=['start'])
def start(message):
    welcome_text = f"""
    Привет, <b>{message.from_user.username}</b>👋

    Давай попрактикуемся в английском языке. Тренировки можешь проходить в удобном для себя темпе.\n
    У тебя есть возможность использовать тренажёр, как конструктор, и собирать свою собственную базу 
    для обучения. Для этого воспользуйся инструментами:\n
    ➕ добавить слово,\n
    🗑️ удалить слово.\n
    Ну что, начнём? ⬇️
    """
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    btn_study = types.KeyboardButton('📚 Учить слова')
    btn_add = types.KeyboardButton('➕ Добавить слово')
    btn_delete = types.KeyboardButton('🗑️ Удалить слово')
    keyboard.add(btn_study, btn_add, btn_delete)

    bot.send_message(message.chat.id, welcome_text, parse_mode='html', reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == '📚 Учить слова')
def learn_word(message):
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    with get_session() as session:
        user = get_or_create_user(session, message.from_user.id, message.from_user.username)
        word = get_random_word(session, user.id)

        if word:
            options = generate_options(session, word)
            btn_add = types.KeyboardButton('➕ Добавить слово')
            btn_del = types.KeyboardButton('🗑️ Удалить слово')
            btn_next = types.KeyboardButton('⏭ Дальше')
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add(*options, btn_add, btn_del, btn_next)
            question = f'Как переводится слово <b>"{word.word}"</b>?'
            bot.send_message(message.chat.id, question, parse_mode='html', reply_markup=markup)

            user_states[message.from_user.id]= {
                'action': 'learning',
                'correct_answer': word.translation,
                'word_id': word.id,
                'word_text': word.word,
                'options': options
            }

        else:
            bot.send_message(message.chat.id, 'У вас нет слов для изучения!')

@bot.message_handler(func=lambda message: message.text == '➕ Добавить слово')
def add_word(message):
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]

    msg = bot.send_message(message.chat.id, 'Введите слово на английском и его перевод через дефис:\nНапример: apple-яблоко')

    user_states[message.from_user.id] = {'action': 'adding_word'}

    bot.register_next_step_handler(msg, process_add_word)

def process_add_word(message):
    user_id = message.from_user.id

    try:
        if '-' not in message.text:
            bot.send_message(message.chat.id, 'Неверный формат. Используйте дефис для разделения.')
            if user_id in user_states:
                del user_states[user_id]
            return

        parts = message.text.split('-', 1)
        en_word = parts[0].strip()
        ru_word = parts[1].strip()

        if not en_word or not ru_word:
            bot.send_message(message.chat.id, 'Слово и перевод не могут быть пустыми.')
            if user_id in user_states:
                del user_states[user_id]
            return

        with get_session() as session:
            user = get_or_create_user(session, user_id, message.from_user.username)
            add_word_to_user(session, user.id, en_word, ru_word)
            bot.send_message(message.chat.id, f'Слово {en_word} успешно добавлено')
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка при добавлении слова')
        print(f'Error: {e}')
    finally:
        if user_id in user_states:
            del user_states[user_id]

@bot.message_handler(func=lambda message: message.text == '🗑️ Удалить слово')
def delete_word(message):
    if message.from_user.id in user_states:
        del user_states[message.from_user.id]
    msg = bot.send_message(message.chat.id, 'Введите слово на английском и его перевод через дефис:\nНапример: apple-яблоко')

    user_states[message.from_user.id] = {'action': 'deleting_word'}

    bot.register_next_step_handler(msg, process_delete_word)

def process_delete_word(message):
    user_id = message.from_user.id

    try:
        if '-' not in message.text:
            bot.send_message(message.chat.id, 'Неверный формат. Используйте дефис для разделения.')
            if user_id in user_states:
                del user_states[user_id]
            return

        parts = message.text.split('-', 1)
        en_word = parts[0].strip()
        ru_word = parts[1].strip()

        if not en_word or not ru_word:
            bot.send_message(message.chat.id, 'Слово и перевод не могут быть пустыми.')
            if user_id in user_states:
                del user_states[user_id]
            return
        with get_session() as session:
            user = get_or_create_user(session, user_id, message.from_user.username)
            deleted = delete_word_from_user(session, user.id, en_word, ru_word)
            if not deleted:
                bot.send_message(message.chat.id,f'Слово "{en_word}" не найдено в вашем словаре или является общим словом')
                if user_id in user_states:
                    del user_states[user_id]
                return
            bot.send_message(message.chat.id, f'Слово "{en_word}" успешно удалено')
    except Exception as e:
        bot.send_message(message.chat.id, 'Произошла ошибка при удалении слова')
        print(f'Error: {e}')
    finally:
        if user_id in user_states:
            del user_states[user_id]

@bot.message_handler(func=lambda message: message.text == '⏭ Дальше')
def next_word(message):
    learn_word(message)

@bot.message_handler(func=lambda message: True)
def check_answer(message):
    user_id = message.from_user.id

    if user_id in user_states and user_states[user_id].get('action') == 'learning':
        correct_answer = user_states[user_id].get('correct_answer')
        word_text = user_states[user_id].get('word_text')
        options = user_states[user_id].get('options')

        if message.text == correct_answer:
            bot.send_message(message.chat.id, 'Правильно! ✅')
            learn_word(message)
        else:
            bot.send_message(message.chat.id, 'Неправильно. Попробуй еще раз')
            markup = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
            markup.add(*options)
            question = f'Как переводится слово <b>"{word_text}"</b>?'
            bot.send_message(message.chat.id, question, parse_mode='html', reply_markup=markup)

if __name__ == '__main__':
    bot.polling()