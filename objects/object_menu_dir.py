import sqlite3
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import json
from objects.object import Object
from schedule.graf import Graf
from datetime import date
from schedule.data_graf import GradForObject
from datetime import datetime
import datetime

#в классе выводятся ВСЕ объекты компании

DB_PATH = "objects.db"
DB_COMP = "company.db"
DB_EMP = "employees.db"
DB_GRAF = "schedule.db"
user_menus = {}

class ObjectMenuDir:
    def __init__(self, message, bot):
        self.name = ''
        self.message = message
        self.bot = bot
        self.current_id = 0
        self.current_id_graf = 0
        self.object_adding = Object()
        self.object_data = []
        self.graf_data = []
        self.dat = None
        user_menus[self.message.chat.id] = self
        self.bot.callback_query_handler(func=lambda call: call.data.startswith('obj_menu_dir'))(self.handle_navigation)

    def start_keyboard(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton('Вперед', callback_data='obj_menu_dir_next'),
        )
        keyboard.add(InlineKeyboardButton('Составить график', callback_data='obj_menu_dir_create_graf'))
        keyboard.add(InlineKeyboardButton('Посмотреть расписание', callback_data='obj_menu_dir_watch_graf'))
        return  keyboard

    def keyboard(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data='obj_menu_dir_prev'),
            InlineKeyboardButton('Вперед', callback_data='obj_menu_dir_next')
        )
        keyboard.add(InlineKeyboardButton('Составить график', callback_data='obj_menu_dir_create_graf'))
        keyboard.add(InlineKeyboardButton('Посмотреть расписание', callback_data='obj_menu_dir_watch_graf'))
        return keyboard

    def end_keyboard(self):
        keyboard = InlineKeyboardMarkup()
        keyboard.add(
            InlineKeyboardButton('Назад', callback_data='obj_menu_dir_prev'),
        )
        keyboard.add(InlineKeyboardButton('Составить график', callback_data='obj_menu_dir_create_graf'))
        keyboard.add(InlineKeyboardButton('Посмотреть расписание', callback_data='obj_menu_dir_watch_graf'))
        return keyboard

    def keyboard_graf(self):
        markup = InlineKeyboardMarkup()
        if self.current_id == 0:
            btn1 = InlineKeyboardButton('Далее', callback_data='obj_menu_dir_next_graf')
            btn2 = InlineKeyboardButton('Изменить дежурного', callback_data='obj_menu_dir_change_duty')
            markup.add(btn1)
            markup.add(btn2)
        elif self.current_id > 0 and self.current_id < len(self.object_data)-1:
            btn1 = InlineKeyboardButton('Назад', callback_data='obj_menu_dir_prev_graf')
            btn2 = InlineKeyboardButton('Далее', callback_data='obj_menu_dir_next_graf')
            btn3 = InlineKeyboardButton('Изменить дежурного', callback_data='obj_menu_dir_change_duty')
            markup.add(btn1)
            markup.add(btn2)
            markup.add(btn3)
        elif self.current_id == len(self.object_data) - 1:
            btn1 = InlineKeyboardButton('Назад', callback_data='obj_menu_dir_prev_graf')
            btn2 = InlineKeyboardButton('Изменить дежурного', callback_data='obj_menu_dir_change_duty')
            markup.add(btn1)
            markup.add(btn2)
        return markup

    def load_graf(self, object_id):
        conn = sqlite3.connect(DB_GRAF)
        cursor = conn.cursor()

        today = self.get_formatted_date()

        # Получаем данные из базы
        cursor.execute("SELECT date, object_id, employee_id FROM schedule WHERE object_id=?",
                       (object_id,))
        cards = cursor.fetchall()
        conn.close()

        # Преобразуем данные в читаемый формат
        for dat, object_id, employee_id in cards:
            try:
                obj = GradForObject()
                obj.date = dat
                self.load_emp(obj, employee_id)
                self.graf_data.append(obj)
            except json.JSONDecodeError:
                # Если ошибка в формате данных
                self.graf_data.append(
                    ("Ошибка данных", "Ошибка данных", "Ошибка данных"))
        self.delete_other()

    def delete_other(self):
        today = date.today().day-1
        for i in self.graf_data:
            day = i.date.split('.')
            if int(day[0]) < int(today):
                self.graf_data.remove(i)
                self.delete_other()

    def get_formatted_date(self):
        start_day = date.today()
        day = start_day.day
        month = start_day.month
        year = start_day.year
        return f"{day}.{month}.{year}"

    # Загрузка карточек из базы данных
    def load_obj(self):
        if len(self.object_data) != 0:
            self.object_data.clear()
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # Получаем данные из базы
        cursor.execute("SELECT id, name, address, supervisor_id FROM objects")
        cards = cursor.fetchall()
        conn.close()

        # Преобразуем данные в читаемый формат
        for card_id, name, address, supervisor in cards:
            try:
                new_data = Object()
                new_data.id = card_id
                new_data.name = name
                new_data.address = address
                new_data.supervisor = supervisor
                self.object_data.append(new_data)
            except json.JSONDecodeError:
                # Если ошибка в формате данных
                self.object_data.append(
                    (card_id, "Ошибка данных", "Ошибка данных", "Ошибка данных", "Ошибка данных"))

    def load_emp(self, obj, employee_id):
        conn = sqlite3.connect(DB_EMP)
        cursor = conn.cursor()

        # Получаем данные из базы
        cursor.execute("SELECT id, fio, phone, card FROM employees WHERE id = ?", (employee_id,))
        cards = cursor.fetchall()
        conn.close()

        # Преобразуем данные в читаемый формат
        for card, fio, phone, card in cards:
            try:
                obj.emp_fio = fio
                obj.emp_phone = phone
                obj.emp_card = card
            except json.JSONDecodeError:
                # Если ошибка в формате данных
                self.graf_data.append(("Ошибка данных", "Ошибка данных", "Ошибка данных", "Ошибка данных"))

    def show_card(self, card_bool):
        if card_bool == True:
            return 'Есть'
        elif card_bool == False:
            return 'Нет'

    def show_graf(self, call):
        self.graf_data = []
        self.load_graf(self.object_data[self.current_id].id)
        text = ""
        text += f'*Объект: {self.object_data[self.current_id].name}* \n'
        today = date.today().day-1

        value = True
        while value == True:
            text += f'\n*{today}.{date.today().month}.{date.today().year}*'
            for i in self.graf_data:
                day = i.date.split('.')
                if int(today) == int(day[0]):
                    text += f'\nДежурный: {i.emp_fio}' \
                        f'\nТелефон дежурного: {i.emp_phone}' \
                        f'\nУдостоверение: {self.show_card(i.emp_card)}\n'
            if today == 31:
                value = False
            today += 1
        self.bot.edit_message_text(text,
                              chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              reply_markup=self.keyboard_graf(),
                              parse_mode="Markdown")

    def input_date_change(self):
        self.bot.send_message(self.message.chat.id, 'Введите в формате: "дд.м.гггг" дату, в которой нужно поменять дату:')
        self.bot.register_next_step_handler_by_chat_id(self.message.chat.id, self.input_change)

    def input_change(self, message):
        self.dat = message.text
        graf = Graf(self.message, self.bot, self.object_data[self.current_id], 0, self.dat)
        graf.change_duty()

    def menu(self, call):
        if call == None:
            if len(self.object_data) == 0:
                keyboard_none = InlineKeyboardMarkup()
                keyboard_none.add(InlineKeyboardButton('Добавить', callback_data='obj_menu_dir_add'))
                self.bot.send_message(self.message.chat.id,
                                 "В базе нет объектов. Пожалуйста, сначала добавьте объекты.",
                                 reply_markup=keyboard_none)
            elif len(self.object_data) != 0:
                text = f'{self.current_id+1}/{len(self.object_data)} \n*Название*: {self.object_data[self.current_id].name} \n*Адрес:* {self.object_data[self.current_id].address} \n*Ответственный*{self.object_data[self.current_id].supervisor}'
                if self.current_id == 0:
                    self.bot.send_message(self.message.chat.id,
                                     text,
                                     reply_markup=self.start_keyboard(),
                                     parse_mode="Markdown")
                elif self.current_id > 0 and self.current_id < len(self.object_data)-1:
                    self.bot.send_message(self.message.chat.id,
                                     text,
                                     reply_markup=self.keyboard(),
                                     parse_mode="Markdown")
                elif self.current_id == len(self.object_data)-1:
                    self.bot.send_message(self.message.chat.id,
                                     text,
                                     reply_markup=self.end_keyboard(),
                                     parse_mode="Markdown")
        else:
            if len(self.object_data) == 0:
                keyboard_none = InlineKeyboardMarkup()
                keyboard_none.add(InlineKeyboardButton('Добавить', callback_data='obj_menu_dir_add'))
                self.bot.send_message(self.message.chat.id,
                                 "В базе нет объектов. Пожалуйста, сначала добавьте объекты.",
                                 reply_markup=keyboard_none)
            elif len(self.object_data) != 0:
                text = f'{self.current_id+1}/{len(self.object_data)} \n*Название*: {self.object_data[self.current_id].name} \n*Адрес:* {self.object_data[self.current_id].address} \n*Ответственный*{self.object_data[self.current_id].supervisor}'
                if self.current_id == 0:
                    self.bot.edit_message_text(text,
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=self.start_keyboard(),
                                          parse_mode="Markdown")
                elif self.current_id > 0 and self.current_id < len(self.object_data)-1:
                    self.bot.edit_message_text(text,
                                          chat_id=call.message.chat.id,
                                          message_id=call.message.message_id,
                                          reply_markup=self.keyboard(),
                                          parse_mode="Markdown")
                elif self.current_id == len(self.object_data)-1:
                    self.bot.edit_message_text(text,
                                          chat_id=call.message.chat.id,
                                          message_id = call.message.message_id,
                                          reply_markup=self.end_keyboard(),
                                          parse_mode="Markdown")

    def handle_navigation(self, call):
        if call.data == 'obj_menu_dir_next':
            self.current_id = self.current_id + 1
            self.menu(call)
        elif call.data == 'obj_menu_dir_prev':
            self.current_id = self.current_id - 1
            self.menu(call)
        elif call.data == 'obj_menu_dir_create_graf':
            graf = Graf(self.message, self.bot, self.object_data[self.current_id])
            graf.start()
        elif call.data == 'obj_menu_dir_watch_graf':
            self.show_graf(call)
        elif call.data == 'obj_menu_dir_next_graf':
            self.current_id += 1
            self.show_graf(call)
        elif call.data == 'obj_menu_dir_prev_graf':
            self.current_id -= 1
            self.show_graf(call)
        elif call.data == 'obj_menu_dir_change_duty':
            self.input_date_change()

    def start(self):
        self.load_obj()
        self.menu(None)