import telebot
import sqlite3
import json
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from objects.object import Object

DB_PATH = 'objects.db'
DB_COMP = 'company.db'
TOKEN = '7827964570:AAH2uEmeIlsFR1Z-Fe-41hXA9kj-7zlgJ1I'
bot = telebot.TeleBot(TOKEN)

user_state = {}

class Object_adding:
    def __init__(self, message, sbot):
        self.message = message
        self.bot = sbot
        self.name = ''
        self.address = ''
        self.chat_id = message.chat.id
        self.user_name = []
        user_state[self.chat_id] = {'name': '', 'address': '', 'supervisor': 0}
        self.id = 0
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('obj_menu_add'))(self.select_object)

    def load_bd_obj(self):
        conn = sqlite3.connect(DB_COMP)
        cursor = conn.cursor()

        # Получаем данные из базы
        cursor.execute("SELECT id, super_v FROM company")
        row = cursor.fetchone()

        conn.close()
        if row:
            card_id, data = row  # Распаковываем кортеж
            self.id = card_id
            try:
                if data:  # Проверяем, что data не None
                    self.user_data = json.loads(data)  # Преобразуем JSON-строку обратно в список словарей
                    for i in self.user_data:
                        self.user_name.append(i['name'])
                else:
                    self.user_data = []  # Пустое значение, если данных нет
            except json.JSONDecodeError:
                self.user_data = []  # Обработка ошибки JSON
                print('Ошибка чтения данных')
        else:
            self.user_data = []

    def start(self):
        print(self.name)
        #self.reset_object()
        self.request_name()

    """def reset_object(self):
        self.name = ''
        self.address = ''
        self.supervisor = 0"""

    def request_name(self):
        mesg = self.bot.send_message(self.message.chat.id, 'Введите название объекта:')
        self.bot.register_next_step_handler(mesg, self.save_name)
        #self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_name)

    def save_name(self, message):
        user_state[self.chat_id]['name'] = message.text
        print(self.name)
        self.request_address()

    def request_address(self):
        mesg = self.bot.send_message(self.message.chat.id, 'Введите адрес объекта:')
        self.bot.register_next_step_handler(mesg, self.save_address)
        #self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_address)

    def save_address(self, message):
        user_state[self.chat_id]['address'] = message.text
        self.request_sv()

    def request_sv(self):
        self.load_bd_obj()
        markup = InlineKeyboardMarkup()
        for i, sv in enumerate(self.user_name, start=0):
            button = InlineKeyboardButton(text=sv,
                                          callback_data=f"obj_menu_add_select_supervis_{i}")
            markup.add(button)
        self.bot.send_message(self.message.chat.id, "Выберите ответственного за объект:",
                              reply_markup=markup)

    def insert_db(self, user_id):
        data = user_state[user_id]
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(self.name)
        cursor.execute("""
                    INSERT INTO objects (name, address, supervisor_id)
                    VALUES (?, ?, ?)
                """, (data['name'], data['address'], data['supervisor']))

        conn.commit()
        conn.close()
        self.bot.send_message(self.message.chat.id, 'Объект добавлен')
        #self.reset_object()

    def select_object(self, call):
        user_id = call.message.chat.id
        if call.data == 'obj_menu_add_yes':
            self.insert_db(user_id)
        elif call.data == 'obj_menu_add_no':
            self.bot.send_message(self.message.chat.id, 'Отмена')
        else:
            id = int(call.data.split('_')[-1])
            keyboard = InlineKeyboardMarkup()
            keyboard.add(
                InlineKeyboardButton('Да', callback_data='obj_menu_add_yes'),
                InlineKeyboardButton('Нет', callback_data='obj_menu_add_no')
            )
            user_state[user_id]['supervisor'] = self.user_data[id]['id']
            self.bot.send_message(call.message.chat.id,
                                        f'Назначить за объект по адресу {user_state[user_id]["address"]} ответственным: {self.user_name[id]}?',
                                        reply_markup=keyboard)
