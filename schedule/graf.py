import telebot
import sqlite3
import json
from employee.employee import Employee
from datetime import datetime
import pandas as pd
import os

# Создание экземпляра бота с вашим токеном
bot = telebot.TeleBot('7827964570:AAH2uEmeIlsFR1Z-Fe-41hXA9kj-7zlgJ1I')
DB_EMP = "employees.db"
DB_GRAF = "schedule.db"

# Словарь для хранения текущего состояния пользователей
user_state = {}

class Graf:
    def __init__(self, message, bot, object_data, days, date):
        self.message = message
        self.bot = bot
        self.employee_data = []
        self.employee_data2 = []
        self.object_data = object_data
        self.duty = ''
        self.iteration = 0
        self.days = days-1
        self.start_day = self.change_date(date)

    def _set_handlers(self):
        """Метод для настройки обработчиков бота."""
        @self.bot.message_handler(content_types=['document'])
        def handle_file(message):
            try:
                # Получение и обработка файла
                file_info = self.bot.get_file(message.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)
                file_path = f"temp_{message.document.file_name}"
                with open(file_path, 'wb') as file:
                    file.write(downloaded_file)

                # Обработка файла
                self.process_excel(file_path, message.chat.id)

                # Уведомление пользователя
                self.bot.reply_to(message, "Файл обработан и данные занесены в базу!")
            except Exception as e:
                self.bot.reply_to(message, f"Произошла ошибка при обработке файла: {e}")

    def process_excel(self, file_path, chat_id):
        """Обработка Excel-файла."""
        try:
            # Чтение файла Excel
            df = pd.read_excel(file_path)
            df = df.fillna('')  # Заполняем пустые ячейки пустой строкой

            # Преобразование данных в список записей
            duty_records = []
            for _, row in df.iterrows():
                name = row['ФИО']
                phone = row['Телефон']
                for day in range(1, 32):  # Столбцы с числами от 1 до 31
                    if str(day) in row and row[str(day)] == 'Д':
                        duty_records.append((name, phone, f'2025-01-{day:02d}'))

            # Занесение данных в базу
            self.cursor.executemany('''
            INSERT INTO duty_schedule (name, phone, date)
            VALUES (?, ?, ?)
            ''', duty_records)
            self.conn.commit()

        finally:
            # Удаление временного файла
            os.remove(file_path)

    def change_date(self, date):
        try:
            start_day = datetime.strptime(date, "%d.%m.%Y")
        except:
            start_day = date
        return start_day

    def change_duty(self):
        self.load_bd_emp()
        self.request_name_ch()

    def request_name_ch(self):
        self.bot.send_message(self.message.chat.id,
                              f'Введите ФИО дежурного на {self.get_formatted_date(self.iteration)} число:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.update_duty)

    def update_duty(self, message):
        date_slov = {}
        date_slov['date'] = self.get_formatted_date(self.iteration)
        self.duty = message.text
        date_slov['duty'] = self.find_employee(message.text)
        """Сохранить данные пользователей в базу данных."""
        conn = sqlite3.connect(DB_GRAF)
        cursor = conn.cursor()

        # Преобразование списка словарей в JSON-строку

        # Проверка существования строки в таблице
        cursor.execute("UPDATE schedule SET employee_id = ? WHERE date = ? AND object_id = ?",
                       (date_slov['duty'], date_slov['date'], self.object_data.id,))

        conn.commit()
        conn.close()
        self.bot.send_message(self.message.chat.id, 'Дежурный изменен')

    def load_bd_emp(self):
        if len(self.employee_data) != 0:
            self.employee_data.clear()
        conn = sqlite3.connect(DB_EMP)
        cursor = conn.cursor()

        # Получаем данные из базы
        cursor.execute("SELECT id, fio, phone, card, is_free_today FROM employees")
        cards = cursor.fetchall()
        conn.close()

        # Преобразуем данные в читаемый формат
        for card_id, fio, phone, card, free in cards:
            try:
                new_data = Employee()
                new_data.id = card_id
                new_data.fio = fio
                new_data.phone_number = phone
                new_data.status = free
                new_data.card = card
                self.employee_data.append(new_data)
            except json.JSONDecodeError:
                # Если ошибка в формате данных
                self.employee_data.append((card_id, "Ошибка данных", "Ошибка данных", "Ошибка данных", "Ошибка данных"))

    def start(self):
        self.load_bd_emp()
        self.request_name()

    def request_name(self):
        self.bot.send_message(self.message.chat.id, f'Введите ФИО дежурного на {self.get_formatted_date(self.iteration)} число:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_name)

    def save_name(self, message):
        date_slov = {}
        date_slov['date'] = self.get_formatted_date(self.iteration)
        self.duty = message.text
        date_slov['duty'] = self.find_employee(message.text)
        if self.iteration < self.days:
            self.iteration += 1
            self.employee_data2.append(date_slov)
            self.request_name()
        else:
            self.employee_data2.append(date_slov)
            self.insert_db()

    def find_employee(self, fio):
        for emp in self.employee_data:
            if emp.fio == fio:
                return emp.id

    def insert_db(self):
        conn = sqlite3.connect(DB_GRAF)
        cursor = conn.cursor()
        for emp in self.employee_data2:
            cursor.execute("""
                                INSERT INTO schedule (date, object_id, employee_id)
                                VALUES (?, ?, ?)
                            """, (emp['date'], self.object_data.id, emp['duty']))

        conn.commit()
        conn.close()
        self.bot.send_message(self.message.chat.id, 'График составлен')

    def get_formatted_date(self, i):
        day = self.start_day.day + i
        month = self.start_day.month
        year = self.start_day.year
        return f"{day}.{month}.{year}"



