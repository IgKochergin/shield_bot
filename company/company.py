import telebot
import sqlite3
import random

TOKEN = '7827964570:AAH2uEmeIlsFR1Z-Fe-41hXA9kj-7zlgJ1I'
bot = telebot.TeleBot(TOKEN)
DB_PATH = "company.db"
chat = -4640940993

class Company:
    def __init__(self, message, bot):
        self.message = message
        self.bot = bot
        self.name = ''
        self.code = ''
        self.code_for_emp = ''
        self.phone = ''

    def add(self):
        self.bot.send_message(self.message.chat.id, 'Введите название компании:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_name)

    def save_name(self, message):
        self.name = message.text
        self.request_phone()

    def request_phone(self):
        self.bot.send_message(self.message.chat.id, 'Введите номер телефона директора в формате: 79996665544:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_phone)

    def save_phone(self, message):
        self.phone = message.text
        self.code = self.create_code()
        self.code_for_emp = self.create_code_for_emp()
        self.insert_db()

    def create_code(self):
        while True:
            # Генерация случайного кода
            code = random.randint(1000000, 9999999)
            if not self.is_code_in_db(code):
                print(code)
                return code

    def create_code_for_emp(self):
        while True:
            # Генерация случайного кода
            code = random.randint(100000, 999999)
            if not self.is_code_in_db_emp(code):
                print(code)
                return code

    def is_code_in_db(self, code):
        """Проверяет наличие кода в базе данных.

        Args:
            code (str): Код для проверки.

        Returns:
            bool: True, если код существует, иначе False.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM company WHERE code = ?", (code,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except:
            return

    def is_code_in_db_emp(self, code):
        """Проверяет наличие кода в базе данных.

        Args:
            code (str): Код для проверки.

        Returns:
            bool: True, если код существует, иначе False.
        """
        try:
            conn = sqlite3.connect(DB_PATH)
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM company WHERE code_for_emp = ?", (code,))
            exists = cursor.fetchone() is not None
            conn.close()
            return exists
        except:
            return

    def insert_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        #нужно указывать id супервайзора для того, чтобы верно выводилось и отображалось все
        cursor.execute("""
                    INSERT INTO company (name, code, code_for_emp, phone)
                    VALUES (?, ?, ?, ?)
                """, (self.name, self.code, self.code_for_emp, self.phone))

        conn.commit()
        conn.close()
        bot.send_message(self.message.chat.id, 'Компания добавлена')
        bot.send_message(self.message.chat.id, f'Код для руководства: {self.code}')
        bot.send_message(self.message.chat.id, f'Код для начальников охраны: {self.code_for_emp}')

        bot.send_message(chat, f"Добавлена новая компания: \nНазвание: {self.name}, \nТелефона дира: {self.phone} "
                               f"\nКод доступа дира: {self.code} \nКода доступа начей смены: {self.code_for_emp}")

    def start(self):
        self.add()