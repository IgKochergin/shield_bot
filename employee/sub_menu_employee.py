import telebot
import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from employee.employee import Employee
from datetime import date
from schedule.data_graf import GradForObject
import os

TOKEN = '7827964570:AAH2uEmeIlsFR1Z-Fe-41hXA9kj-7zlgJ1I'
bot = telebot.TeleBot(TOKEN)
DB_PATH = os.path.abspath("shield/employees.db")
DB_GRAF = os.path.abspath("shield/schedule.db")

#Клавиатуры

class EmployeeMenu:
    def __init__(self, bot, message):
        self.bot = bot
        self.employee_data = []
        self.message = message
        self.fio = ''
        self.phone = ''
        self.status = ''
        self.card = False
        self.current_id = 0
        self.graf = []
        self.employee_adding = Employee()

        # Регистрируем обработчики
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('emp_'))(self.handle_navigation)

    def start_keyboard(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton('Удалить', callback_data='emp_delete'),
            InlineKeyboardButton('Вперед', callback_data='emp_next'),
        )
        keyboard.add(InlineKeyboardButton('Показать свободных', callback_data='emp_free'))
        return keyboard

    def markup(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data='emp_prev'),
            InlineKeyboardButton('Удалить', callback_data='emp_delete'),
            InlineKeyboardButton('Вперед', callback_data='emp_next')
        )
        keyboard.add(InlineKeyboardButton('Показать свободных', callback_data='emp_free'))
        return keyboard

    def end_keyboard(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data='emp_prev'),
            InlineKeyboardButton('Удалить', callback_data='emp_delete')
        )
        keyboard.add(InlineKeyboardButton('Показать свободных', callback_data='emp_free'))
        return keyboard

    def free_keyboard(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton('Сегодня', callback_data='emp_today'),
            InlineKeyboardButton('Завтра', callback_data='emp_tomorrow'),
            InlineKeyboardButton('Через 2 дня', callback_data='emp_2_days'),
            InlineKeyboardButton('Через 3 дня', callback_data='emp_3_days'),
            InlineKeyboardButton('Через 4 дня', callback_data='emp_4_days'),
            InlineKeyboardButton('Через 5 дней', callback_data='emp_5_days'),
        )
        return keyboard

    # Загрузка карточек из базы данных
    def load_cards(self):
        if len(self.employee_data) != 0:
            self.employee_data.clear()
        conn = sqlite3.connect(DB_PATH)
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

    def show_status(self, status_bool):
        if status_bool == True:
            return 'Свободен'
        elif status_bool == False:
            return 'Занят'

    def show_card(self, card_bool):
        if card_bool == True:
            return 'Есть'
        elif card_bool == False:
            return 'Нет'

    def menu(self, call):
        if call==None:
            self.current_id = 0
            self.load_cards()
            if len(self.employee_data) == 0:
                keyboard_none = InlineKeyboardMarkup()
                keyboard_none.add(InlineKeyboardButton('Добавить', callback_data='emp_add'))
                bot.send_message(self.message.chat.id,
                                 "В базе нет сотрудников. Пожалуйста, сначала добавьте сотрудников.",
                                 reply_markup=keyboard_none)
            elif len(self.employee_data) != 0:
                text = f'{self.current_id+1}/{len(self.employee_data)} \n*ФИО*: {self.employee_data[self.current_id].fio} \n*Номер телефона:* {self.employee_data[self.current_id].phone_number} \n*Статус*{self.show_status(self.employee_data[self.current_id].status)} \nУдостоверение: *{self.show_card(self.employee_data[self.current_id].card)}*'
                if self.current_id == 0:
                    bot.send_message(self.message.chat.id, text, reply_markup=self.start_keyboard(), parse_mode="Markdown")
                elif self.current_id > 0 and self.current_id < len(self.employee_data)-1:
                    bot.send_message(self.message.chat.id, text, reply_markup=self.markup(), parse_mode="Markdown")
                elif self.current_id == len(self.employee_data)-1:
                    bot.send_message(self.message.chat.id, text, reply_markup=self.end_keyboard(), parse_mode="Markdown")
        else:
            if len(self.employee_data) == 0:
                keyboard_none = InlineKeyboardMarkup()
                keyboard_none.add(InlineKeyboardButton('Добавить', callback_data='emp_add'))
                bot.send_message(self.message.chat.id,
                                 "В базе нет сотрудников. Пожалуйста, сначала добавьте сотрудников.",
                                 reply_markup=keyboard_none)
            elif len(self.employee_data) != 0:
                text = f'{self.current_id + 1}/{len(self.employee_data)} ' \
                       f'\n*ФИО*: {self.employee_data[self.current_id].fio} ' \
                       f'\n*Номер телефона:* {self.employee_data[self.current_id].phone_number} ' \
                       f'\n*Статус*{self.show_status(self.employee_data[self.current_id].status)} ' \
                       f'\n*Удостоверение: *{self.show_card(self.employee_data[self.current_id].card)}'
                if self.current_id == 0:
                    bot.edit_message_text(text,
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=self.start_keyboard(),
                                          parse_mode="Markdown")
                elif self.current_id > 0 and self.current_id < len(self.employee_data) - 1:
                    bot.edit_message_text(text,
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=self.markup(),
                                          parse_mode="Markdown")
                elif self.current_id == len(self.employee_data) - 1:
                    bot.edit_message_text(text,
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=self.end_keyboard(),
                                          parse_mode="Markdown")

    def add(self):
        self.adding_in_progress = True
        self.bot.send_message(self.message.chat.id, 'Введите ФИО нового сотрудника:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_fio)

    def save_fio(self, message):
        self.employee_adding.fio = message.text
        self.request_phone()

    def request_phone(self):
        self.bot.send_message(self.message.chat.id, 'Введите номер телефон сотрудника:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.save_phone)

    def save_phone(self, message):
        self.employee_adding.phone_number = message.text
        self.request_card()

    def request_card(self):
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton('Есть', callback_data='emp_pos'),
            InlineKeyboardButton('Нет', callback_data='emp_neg')
        )
        self.bot.send_message(self.message.chat.id, 'У сотрудника есть удостоверение?', reply_markup=kb)

    def insert_db(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        cursor.execute("""
                    INSERT INTO employees (fio, phone, card)
                    VALUES (?, ?, ?)
                """, (self.employee_adding.fio, self.employee_adding.phone_number, self.employee_adding.card))

        conn.commit()
        conn.close()
        self.bot.send_message(self.message.chat.id, 'Сотрудник добавлен')
        self.load_cards()
        self.menu(None)

    def delete(self):
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        curr_id = self.employee_data[self.current_id].id
        cursor.execute("""
            DELETE FROM employees WHERE id = ?
        """, (curr_id,))

        conn.commit()
        conn.close()
        self.load_cards()

    def load_graf(self, i):
        conn = sqlite3.connect(DB_GRAF)
        cursor = conn.cursor()

        today = self.get_formatted_date(i)
        print(today)

        # Получаем данные из базы
        cursor.execute("SELECT date, employee_id FROM schedule WHERE date = ?",
                       (today,))
        cards = cursor.fetchall()
        conn.close()

        # Преобразуем данные в читаемый формат
        for dat, employee_id in cards:
            try:
                new = GradForObject()
                new.date = dat
                print(dat)
                new.emp_id = employee_id
                print(employee_id)
                self.graf.append(new)
            except json.JSONDecodeError:
                # Если ошибка в формате данных
                self.graf.append(
                    ("Ошибка данных", "Ошибка данных", "Ошибка данных"))
        self.print_graf()

    def print_graf(self):
        for i in self.graf:
            print(i.date, i.emp_id)

    def free(self, it):
        self.load_graf(it)
        for i in self.graf:
            for y in self.employee_data: #print(i.emp_id)
                if i.emp_id == y.id:
                    self.employee_data.remove(y)

    def get_formatted_date(self, i):
        self.start_day = date.today()
        day = self.start_day.day + i
        month = self.start_day.month
        year = self.start_day.year
        return f"{day}.{month}.{year}"

    def handle_navigation(self, call):
        if call.data == 'emp_delete':
            self.delete()
        elif call.data == 'emp_next':
            self.current_id = self.current_id + 1
            self.menu(call)
            print(f'вперед {self.current_id}')
        elif call.data == 'emp_prev':
            self.current_id = self.current_id - 1
            self.menu(call)
        elif call.data == 'emp_free':
            bot.edit_message_text("Когда вам нужно найти свободного сотрудника?",
                                  chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  reply_markup=self.free_keyboard())
        elif call.data == 'emp_today':
            self.free(0)
            self.current_id = 0
            self.menu(call)
        elif call.data == 'emp_tomorrow':
            self.free(1)
            self.current_id = 0
            self.menu(call)
        elif call.data == 'emp_2_days':
            self.free(2)
            self.current_id = 0
            self.menu(call)
        elif call.data == 'emp_3_days':
            self.free(3)
            self.current_id = 0
            self.menu(call)
        elif call.data == 'emp_4_days':
            self.free(4)
            self.current_id = 0
            self.menu(call)
        elif call.data == 'emp_5_days':
            self.free(5)
            self.current_id = 0
            self.menu(call)
        elif call.data == 'emp_pos':
            self.employee_adding.card = True
            self.insert_db()
        elif call.data == 'emp_neg':
            self.employee_adding.card = False
            self.insert_db()

    def start(self):
        self.employee_data = []
        self.current_id = 0
        self.menu(None)