import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
import os

DB_PATH = os.path.abspath("shield/company.db")

class Director:
    def __init__(self, message, sbot):
        self.message = message
        self.bot = sbot
        self.code = 0
        self.user_data = []
        self.id = 0
        self.name = ''

    def menu_for_dir(self):
        markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
        btn1 = KeyboardButton("Объекты")
        btn3 = KeyboardButton("Сотрудники (директор)")
        markup.add(btn1)
        markup.add(btn3)
        return markup

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

        cursor.execute("SELECT 1 FROM company WHERE code = ?", (self.code,))
        result = cursor.fetchone()

        conn.close()

        if result:
            self.bot.send_message(self.message.chat.id, 'Код доступа найден. Доступ открыт.', reply_markup=self.menu_for_dir())
        else:
            self.bot.send_message(self.message.chat.id, 'Код доступа не найден. Обратитесь в администратору.')
