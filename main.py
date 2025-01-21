import telebot
import sqlite3
from telebot.types import ReplyKeyboardMarkup, KeyboardButton
from employee.sub_menu_employee import EmployeeMenu
from company.company import Company
from supervisor import Supervisor
from objects.object_add_sv import Object_adding
from objects.object_menu import ObjectMenu
from objects.object_menu_dir import ObjectMenuDir
from director import Director

TOKEN = '7827964570:AAH2uEmeIlsFR1Z-Fe-41hXA9kj-7zlgJ1I'
bot = telebot.TeleBot(TOKEN)

user_data = {}

def initialize_db_employees():
    # Подключение к базе данных
    conn = sqlite3.connect("employees.db")
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS employees (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fio TEXT,
            phone TEXT,
            card BOOLEAN DEFAULT 0,
            is_free_today BOOLEAN DEFAULT 1
        )
    """)

    # Закрываем соединение
    conn.commit()
    conn.close()

def initialize_db_objects():
    # Подключение к базе данных
    conn = sqlite3.connect("objects.db")
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS objects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            address TEXT NOT NULL,
            supervisor_id INTEGER
        )
    """)

    # Закрываем соединение
    conn.commit()
    conn.close()

def initialize_db_companies():
    # Подключение к базе данных
    conn = sqlite3.connect("company.db")
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS company (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            code INTEGER UNIQUE NOT NULL,            
            code_for_emp INTEGER UNIQUE NOT NULL,
            phone TEXT NOT NULL,
            super_v TEXT,
            days INTEGER
        )
    """)
    # Закрываем соединение
    conn.commit()
    conn.close()

def initialize_db_schedule():
    # Подключение к базе данных
    conn = sqlite3.connect("schedule.db")
    cursor = conn.cursor()

    # Создаем таблицу, если она еще не существует
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS schedule (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date DATE NOT NULL,                -- Дата смены
            object_id INTEGER NOT NULL,        -- ID объекта
            employee_id INTEGER NOT NULL      -- ID дежурного
        )
    """)

    # Закрываем соединение
    conn.commit()
    conn.close()

def menu_for_dir():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton("Объекты")
    btn3 = KeyboardButton("Сотрудники (директор)")
    markup.add(btn1)
    markup.add(btn3)
    return markup

def menu_for_nach():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton("Посмотреть объекты (нач. смены)")
    btn2 = KeyboardButton("Сотрудники (нач. смены)")
    markup.add(btn1)
    markup.add(btn2)
    return markup

def main_menu():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton("Директор")
    btn2 = KeyboardButton("Начальник смены")
    markup.add(btn1, btn2)
    return markup

def menu_objects_dir():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton("Посмотреть объекты (директор)")
    btn2 = KeyboardButton("Договор охраны")
    btn3 = KeyboardButton("Добавить новый объект")
    btn4 = KeyboardButton("Главное меню директора")
    markup.add(btn1)
    markup.add(btn2)
    markup.add(btn3)
    markup.add(btn4)
    return markup

def menu_employee_dir():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton("Посмотреть сотрудников")
    btn2 = KeyboardButton("Трудовой договор")
    btn3 = KeyboardButton("Главное меню директора")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

def menu_employee_sv():
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn1 = KeyboardButton("Посмотреть сотрудников")
    btn2 = KeyboardButton("Трудовой договор")
    btn3 = KeyboardButton("Главное меню нач. смены")
    markup.add(btn1, btn2)
    markup.add(btn3)
    return markup

#Старт бота и инициализация БД
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    initialize_db_employees()
    initialize_db_objects()
    initialize_db_schedule()
    initialize_db_companies()
    bot.send_message(user_id, 'Выберите вашу роль в компании:"', reply_markup=main_menu())

@bot.message_handler(func=lambda message: message.text == "Директор")
def director(message):
    dir = Director(message, bot)
    dir.input_code()

@bot.message_handler(func=lambda message: message.text == "Объекты")
def objects(message):
    bot.send_message(message.chat.id, 'Вы выбрали пункт "Объекты"', reply_markup=menu_objects_dir())

@bot.message_handler(func=lambda message: message.text == "Добавить новый объект")
def add_new_object(message):
    new_obj = Object_adding(message, bot)
    new_obj.start()

@bot.message_handler(func=lambda message: message.text == "Начальник смены")
def ruk_smen(message):
    supvis = Supervisor(message, bot)
    supvis.input_code()

@bot.message_handler(func=lambda message: message.text == "Посмотреть объекты (директор)")
def watch_objects(message):
    watch_obj = ObjectMenuDir(message, bot)
    watch_obj.start()

@bot.message_handler(func=lambda message: message.text == "Посмотреть объекты (нач. смены)")
def watch_objects(message):
    watch_obj = ObjectMenu(message, bot)
    watch_obj.start()

@bot.message_handler(func=lambda message: message.text == "Сотрудники (директор)")
def employees_dir(message):
    bot.send_message(message.chat.id, 'Вы выбрали пункт "Сотрудники"', reply_markup=menu_employee_dir())

@bot.message_handler(func=lambda message: message.text == "Cотрудники (нач. смены)")
def employees_sv(message):
    bot.send_message(message.chat.id, 'Вы выбрали пункт "Сотрудники"', reply_markup=menu_employee_sv())

@bot.message_handler(func=lambda message: message.text == "Главное меню директора")
def m_dir(message):
    bot.send_message(message.chat.id, 'Главное меню директора', reply_markup=menu_for_dir())

@bot.message_handler(func=lambda message: message.text == "Главное меню нач. смены")
def m_sv(message):
    bot.send_message(message.chat.id, 'Главное меню директора', reply_markup=menu_for_nach())

@bot.message_handler(func=lambda message: message.text == "Посмотреть сотрудников")
def employees_base(message):
    sub_menu_employee = EmployeeMenu(bot, message)
    sub_menu_employee.start()

@bot.message_handler(commands=['create_comp'])
def create_company(message):
    comp = Company(message, bot)
    comp.start()

bot.polling(none_stop=True)