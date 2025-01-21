import telebot
import json
import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton


DB_PATH = "company.db"
TOKEN = '7827964570:AAH2uEmeIlsFR1Z-Fe-41hXA9kj-7zlgJ1I'
bot = telebot.TeleBot(TOKEN)

class Supervisor:
    def __init__(self, message, sbot):
        self.message = message
        self.bot = sbot
        self.code = 0
        self.user_data = []
        self.id = 0
        self.name = ''

    def menu_for_nach(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = KeyboardButton("Посмотреть объекты (нач. смены)")
        btn2 = KeyboardButton("Cотрудники (нач. смены)")
        markup.add(btn1)
        markup.add(btn2)
        return markup

    def load_sv(self):
        conn = sqlite3.connect(DB_PATH)
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
                else:
                    self.user_data = []  # Пустое значение, если данных нет
            except json.JSONDecodeError:
                self.user_data = []  # Обработка ошибки JSON
                print('Ошибка чтения данных')
        else:
            self.user_data = []

    def find_same(self, user_id):
        for i in self.user_data:
            if i['id'] == user_id:
                print('пользователь уже есть')
                bot.send_message(self.message.chat.id, ' Доступ открыт.',
                                  reply_markup=self.menu_for_nach())
                return True
            else:
                return False

    def save_users_to_db(self):
        """Сохранить данные пользователей в базу данных."""
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Преобразование списка словарей в JSON-строку
        users_json = json.dumps(self.user_data)

        # Проверка существования строки в таблице
        cursor.execute("UPDATE company SET super_v = ? WHERE code_for_emp = ?", (users_json, self.code))

        conn.commit()
        conn.close()

    def request_name(self):
        self.bot.send_message(self.message.chat.id, 'Введите свои имя и фамилию')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_name)

    def save_name(self, message):
        self.name = message.text
        self.add_user_data(self.message.from_user.id)

    def add_user_data(self, user_id):
        try:
            # Добавление данных в список словарей
            self.user_data.append({"id": user_id, "name": self.name})
            self.save_users_to_db()
            bot.send_message(self.message.chat.id, ' Доступ открыт.',
                             reply_markup=self.menu_for_nach())
            print(f"Пользователь добавлен: ID={user_id}, Имя/Никнейм={self.name}")
        except Exception as e:
            print(f"Ошибка при получении данных пользователя: {e}")

    def input_code(self):
        self.bot.send_message(self.message.chat.id, 'Введите код, который вам выдал администратор:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_code)

    def save_code(self, message):
        self.code = message.text
        self.check_code_emp()

    def check_code_emp(self):
        """
            Проверяет, существует ли данный код в базе данных.
            :param code: Код из 6 чисел для проверки.
            :return: True, если код найден, иначе False.
            """
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("SELECT 1 FROM company WHERE code_for_emp = ?", (self.code,))
        result = cursor.fetchone()

        conn.close()

        if result:
            self.load_sv()
            self.bot.send_message(self.message.chat.id, 'Код доступа найден.')
            if self.find_same(self.message.from_user.id):
                return
            else:
                self.request_name()
        else:
            self.bot.send_message(self.message.chat.id, 'Код доступа не найден. Обратитесь в администратору.')
