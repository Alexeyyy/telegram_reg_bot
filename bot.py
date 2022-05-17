import telebot
import psycopg2

# Запуск
# python3 registrator_bot.py
# https://habr.com/ru/post/350648/
# Запуск бота
# heroku ps:scale bot=1
# heroku ps:scale bot=0
# Залезть на сервачок.
# heroku ps:exec --dyno=bot.1

# Название бота: @region_it_bot
# Боевой токен.
token = '<тут токен телеграм бота>'

bot = telebot.TeleBot(token)

messages = {}
contacts = {}
names = {}
companies = {}
regions = {}
ranks = {}

BTN_ENTER_TEXT = 'ВСТУПИТЬ'
FIRST_QUESTION = 'ФИО:'
SECOND_QUESTION = 'Укажите название Вашей компании (компаний):'
THIRD_QUESTION = 'Укажите должность:'
FOURTH_QUESTION = 'Укажите ваш регион:'
FINAL_RESPONSE = 'Благодарим за регистрацию! Перейдите по ссылке, чтобы вступить в чат: https://t.me/+nUC1Ga9hFBg1YTNi'

FILENAME = 'bot_contacts_data.txt'
SPLITTER = '============='

CONTACTS_PER_MESSAGE = 10

DATABASE_CONNECTION_STRING = '<полный connection string до POSTGRES базы>'

# База данных.
DB_NAME = '<Название базы>'
DB_HOST = '<Хост-домен>'
DB_PASSWORD = '<DB-пароль>'
DB_USER = '<DB-пользователь>'

# Наименование таблицы уникально для каждого бота по окончанию токена.
DB_BOT_TABLE = '<название таблицы>'

# При этом набор полей у ботом должен быть идентичен!
# Сделаем везде text, по-любому найдется умник с длинным именем.
# create table <название таблицы> (
#    name text,
#    contact text,
#    company text,
#    rank text,
#    region text,
#    created timestamp DEFAULT current_timestamp
#);

CONTACT_IS_HIDDEN = 'Данные контакта скрыты'
GET_PERSON_CMD = '/getperson'

@bot.message_handler(content_types=["text"])
def start(message):
    if message.text == '/start':
        show_init_state(message)
    elif message.text == '/cheatandgetfromfile':
       cheat_and_get(message.chat.id)
    elif message.text == '/cheatandget':
        get_registered_persons_from_db(message.chat.id)
    elif message.text == '/aboutthisbot':
        bot.send_message(message.chat.id, 'Hello from bot.py')
    elif GET_PERSON_CMD in message.text:
        find_persons(message.chat.id, message.text)
    else:
        show_init_state(message)


@bot.callback_query_handler(func=lambda call: 'cmd' in call.data)
def query_callback(call):
    if call.data.endswith('enter'):
        bot.send_message(call.message.chat.id, FIRST_QUESTION)
        bot.register_next_step_handler(call.message, get_name)


def get_name(message):
    contacts[message.chat.id] = message.from_user.username or CONTACT_IS_HIDDEN
    names[message.chat.id] = message.text
    bot.send_message(message.from_user.id, SECOND_QUESTION)
    bot.register_next_step_handler(message, get_company_name)


def get_company_name(message):
    companies[message.chat.id] = message.text or 'Пустое сообщение'
    bot.send_message(message.from_user.id, THIRD_QUESTION)
    bot.register_next_step_handler(message, get_rank)


def get_rank(message):
    ranks[message.chat.id] = message.text or 'Пустое сообщение'
    bot.send_message(message.from_user.id, FOURTH_QUESTION)
    bot.register_next_step_handler(message, share_link)


def share_link(message):
    chat_id = message.chat.id

    regions[chat_id] = message.text or 'Пустое сообщение'
    bot.send_message(message.from_user.id, FINAL_RESPONSE)

    print(create_data_str(chat_id) + ' зарегистрировался')

    save_to_file(chat_id)
    save_to_database(chat_id)

    clear_dictionaries(chat_id)


def save_to_file(chat_id):
    file_object = open(FILENAME, 'a')
    file_object.write(create_data_str(chat_id))
    file_object.close()


def save_to_database(chat_id):
    connection = psycopg2.connect(
        dbname = DB_NAME, user = DB_USER,
        password = DB_PASSWORD, host = DB_HOST
    )
    cursor = connection.cursor()
    
    cursor.execute('insert into ' + DB_BOT_TABLE + ' (name, contact, company, rank, region) values (\'' + names[chat_id] + '\', \'' + '@' + contacts[chat_id] + '\', \'' + companies[chat_id] + '\', \'' + ranks[chat_id] + '\', \'' + regions[chat_id] + '\');')
    connection.commit()

    cursor.close()
    connection.close()


def clear_dictionaries(chat_id):
    del contacts[chat_id]
    del names[chat_id]
    del companies[chat_id]
    del ranks[chat_id]
    del regions[chat_id]


def create_data_str(chat_id):
    return 'Контакт: ' + '@' + contacts[chat_id] + '\nФИО: ' + names[chat_id] + '\nКомпания: ' + companies[chat_id] + '\nДолжность: ' + ranks[chat_id] + '\nРегион: ' + regions[chat_id] + '\n' + SPLITTER + '\n'


def cheat_and_get(chat_id):
    file_object = open(FILENAME, "r")
    lines = file_object.readlines()
    file_object.close()

    buffer = []
    person = ''
    for line in lines:
        if SPLITTER in line:
            buffer.append(person)
            person = ''
        else:
            person += line
        
        if len(buffer) == CONTACTS_PER_MESSAGE:
            bot.send_message(chat_id, '\n'.join(buffer))
            buffer.clear()
    
    if len(buffer) > 0:
        bot.send_message(chat_id, '\n'.join(buffer))
    
    buffer.clear()


def get_registered_persons_from_db(chat_id):
    connection = psycopg2.connect(
        dbname = DB_NAME, user = DB_USER,
        password = DB_PASSWORD, host = DB_HOST
    )
    cursor = connection.cursor()

    cursor.execute('SELECT * FROM ' + DB_BOT_TABLE)
    out_str = ''
    counter = 0

    for row in cursor:
        name = row[0]
        contact = row[1]
        company = row[2]
        rank = row[3]
        region = row[4]
        registered = row[5]
        
        out_str += ('Контакт: ' + contact + '\n')
        out_str += ('ФИО: ' + name + '\n')
        out_str += ('Компания: ' + company + '\n')
        out_str += ('Должность: ' + rank + '\n')
        out_str += ('Регион: ' + region + '\n')
        out_str += ('Дата регистрации: ' + str(registered) + '\n')
        out_str += '\n'

        counter += 1

        if counter % 10 == 0:
            bot.send_message(chat_id, out_str)
            out_str = ''

    if counter == 0:
        bot.send_message(chat_id, 'Никто пока не зарегистрировался')        
    else: # тупо дослать, что осталось.
        bot.send_message(chat_id, out_str)

    cursor.close()
    connection.close()


def find_persons(chat_id, message):
    search_str = message.replace(GET_PERSON_CMD, '').strip().lower()

    connection = psycopg2.connect(
        dbname = DB_NAME, user = DB_USER,
        password = DB_PASSWORD, host = DB_HOST
    )
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM " + DB_BOT_TABLE + " WHERE LOWER(name) LIKE '" + "%" + search_str + "%" + "'")
    out_str = ''
    counter = 0

    for row in cursor:
        name = row[0]
        contact = row[1]
        company = row[2]
        rank = row[3]
        region = row[4]
        registered = row[5]
        
        out_str += ('#' + region.replace(' ', '_') + '\n')
        if not (CONTACT_IS_HIDDEN in contact):
            out_str += (contact + '\n')
        out_str += (name + '\n')
        out_str += (rank + '\n')
        out_str += (company + '\n')
        out_str += '\n'

        counter += 1

        if counter % 10 == 0:
            bot.send_message(chat_id, out_str)
            out_str = ''

    if counter == 0:
        bot.send_message(chat_id, 'Нет данных удовлетворяющих поиску')        
    else: # тупо дослать, что осталось.
        bot.send_message(chat_id, out_str)

    cursor.close()
    connection.close()


def show_init_state(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(BTN_ENTER_TEXT, callback_data='cmd_enter'),
    )
    bot.send_message(
        message.chat.id,
        'Добрый день!\n\n Вы вступаете в чат руководителей и учредителей региональных IT-компаний. Если Вы являетесь таковым, нажмите ВСТУПИТЬ.',
        reply_markup=keyboard
    )


if __name__ == '__main__':
    bot.infinity_polling()
