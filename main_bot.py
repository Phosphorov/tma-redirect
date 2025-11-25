#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main Telegram Bot for Yandex Tracker Integration
This bot manages employees, shifts, requests and other tasks using Yandex Tracker
"""

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from config.settings import TELEGRAM_BOT_TOKEN
from utils.user_auth import get_user_role_from_tracker
from utils.message_utils import update_user_state, get_user_state, create_back_button_keyboard
from models import tracker_integration
from handlers.employee_handlers import handle_employee_creation, handle_employee_list, handle_employee_search, handle_employee_details
from handlers.shift_handlers import handle_start_shift, handle_end_shift, handle_submit_to_request, handle_view_requests, handle_create_request
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Initialize the bot
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)

# Store user states
user_states = {}

def get_main_menu_keyboard(user_role):
    """Create main menu keyboard based on user role"""
    keyboard = InlineKeyboardMarkup()
    
    if user_role == 'admin':
        # Admin menu
        keyboard.row(InlineKeyboardButton("Управление сотрудниками", callback_data="admin_employees"))
        keyboard.row(InlineKeyboardButton("Управление городами", callback_data="admin_cities"))
        keyboard.row(InlineKeyboardButton("Управление складами", callback_data="admin_warehouses"))
        keyboard.row(InlineKeyboardButton("Управление компаниями", callback_data="admin_companies"))
        keyboard.row(InlineKeyboardButton("Тарифы", callback_data="admin_rates"))
        keyboard.row(InlineKeyboardButton("Уведомления", callback_data="admin_notifications"))
        keyboard.row(InlineKeyboardButton("Графики", callback_data="admin_schedules"))
        keyboard.row(InlineKeyboardButton("Согласование", callback_data="admin_approval"))
    elif user_role == 'manager':
        # Manager menu
        keyboard.row(InlineKeyboardButton("Смена", callback_data="manager_shift"))
        keyboard.row(InlineKeyboardButton("Согласование", callback_data="manager_approval"))
        keyboard.row(InlineKeyboardButton("Заявки", callback_data="manager_requests"))
        keyboard.row(InlineKeyboardButton("Сотрудники", callback_data="manager_employees"))
        keyboard.row(InlineKeyboardButton("Графики", callback_data="manager_schedules"))
        keyboard.row(InlineKeyboardButton("Отсутствие", callback_data="manager_absence"))
    elif user_role == 'shift_supervisor':
        # Shift supervisor menu
        keyboard.row(InlineKeyboardButton("Смена", callback_data="supervisor_shift"))
        keyboard.row(InlineKeyboardButton("Согласование", callback_data="supervisor_approval"))
        keyboard.row(InlineKeyboardButton("Заявки", callback_data="supervisor_requests"))
        keyboard.row(InlineKeyboardButton("Графики", callback_data="supervisor_schedules"))
        keyboard.row(InlineKeyboardButton("Отсутствие", callback_data="supervisor_absence"))
    elif user_role == 'employee':
        # Employee menu
        keyboard.row(InlineKeyboardButton("Смена", callback_data="employee_shift"))
        keyboard.row(InlineKeyboardButton("Отсутствие", callback_data="employee_absence"))
    elif user_role == 'outs_staff_manager':
        # Outsourced staff manager menu
        keyboard.row(InlineKeyboardButton("Смена", callback_data="outs_manager_shift"))
        keyboard.row(InlineKeyboardButton("Заявки", callback_data="outs_manager_requests"))
        keyboard.row(InlineKeyboardButton("Тарифы", callback_data="outs_manager_rates"))
        keyboard.row(InlineKeyboardButton("Сотрудники", callback_data="outs_manager_employees"))
    elif user_role == 'brigadier':
        # Brigadier menu
        keyboard.row(InlineKeyboardButton("Смена", callback_data="brigadier_shift"))
        keyboard.row(InlineKeyboardButton("Заявки", callback_data="brigadier_requests"))
    elif user_role == 'outs_employee':
        # Outsourced employee menu
        keyboard.row(InlineKeyboardButton("Смена", callback_data="outs_employee_shift"))
    
    # Common back button
    keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
    
    return keyboard

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Handle /start command"""
    try:
        # Determine user role from tracker based on Telegram ID
        user_role = get_user_role_from_tracker(str(message.from_user.id))
        
        welcome_text = f"Добро пожаловать в систему управления персоналом!\nВаша роль: {user_role}\n\nВыберите действие из меню ниже:"
        
        keyboard = get_main_menu_keyboard(user_role)
        msg = bot.send_message(message.chat.id, welcome_text, reply_markup=keyboard)
        
        # Store message ID for editing later
        update_user_state(message.chat.id, msg.message_id, {'role': user_role})
    except Exception as e:
        logger.error(f"Error in send_welcome: {e}")
        bot.reply_to(message, "Произошла ошибка при обработке команды")

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Handle inline keyboard callbacks"""
    try:
        chat_id = call.message.chat.id
        message_id = call.message.message_id
        
        # Get user role from state or tracker
        user_data = get_user_state(chat_id)
        user_role = user_data.get('role', get_user_role_from_tracker(str(call.from_user.id)))
        
        # Update user state with new message
        update_user_state(chat_id, message_id, {'role': user_role})
        
        # Process different callback data
        if call.data == 'back_to_main':
            # Return to main menu
            welcome_text = f"Добро пожаловать в систему управления персоналом!\nВаша роль: {user_role}\n\nВыберите действие из меню ниже:"
            keyboard = get_main_menu_keyboard(user_role)
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=welcome_text, reply_markup=keyboard)
        else:
            # Handle other callbacks
            handle_specific_callback(call, chat_id, message_id, user_role)
        
        # Always answer callback
        bot.answer_callback_query(call.id)
    except Exception as e:
        logger.error(f"Error in handle_callback: {e}")

def handle_specific_callback(call, chat_id, message_id, user_role):
    """Handle specific callback data"""
    # This function will be expanded to handle different callbacks
    if call.data.startswith('admin_'):
        handle_admin_callback(call, chat_id, message_id, user_role)
    elif call.data.startswith('manager_'):
        handle_manager_callback(call, chat_id, message_id, user_role)
    elif call.data.startswith('supervisor_'):
        handle_supervisor_callback(call, chat_id, message_id, user_role)
    elif call.data.startswith('employee_'):
        handle_employee_callback(call, chat_id, message_id, user_role)
    elif call.data.startswith('outs_manager_'):
        handle_outs_manager_callback(call, chat_id, message_id, user_role)
    elif call.data.startswith('brigadier_'):
        handle_brigadier_callback(call, chat_id, message_id, user_role)
    elif call.data.startswith('outs_employee_'):
        handle_outs_employee_callback(call, chat_id, message_id, user_role)

def handle_admin_callback(call, chat_id, message_id, user_role):
    """Handle admin-specific callbacks"""
    action = call.data.split('_')[1]
    
    if action == 'employees':
        handle_employee_list(chat_id, message_id, bot)
    elif action == 'add':
        # This handles the "add employee" callback for admin
        handle_employee_creation(chat_id, message_id, bot)
    elif action == 'search':
        # This handles the "search employee" callback for admin
        handle_employee_search(chat_id, message_id, bot)
    elif action.startswith('edit'):
        # This handles the "edit employee" callback for admin
        # Extract employee ID from callback data
        parts = call.data.split('_')
        if len(parts) >= 4:
            employee_id = parts[3]
            handle_employee_details(chat_id, message_id, employee_id, bot)
    elif action.startswith('block'):
        # This handles the "block employee" callback for admin
        text = "Сотрудник заблокирован."
        keyboard = create_navigation_keyboard([
            ("Назад", "admin_employees")
        ], "admin_employees")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'cities':
        text = "Управление городами:\n- Добавить город\n- Редактировать город"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Добавить", callback_data="admin_add_city"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'warehouses':
        text = "Управление складами:\n- Добавить склад\n- Редактировать склад"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Добавить", callback_data="admin_add_warehouse"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'companies':
        text = "Управление компаниями:\n- Добавить компанию\n- Редактировать компанию"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Добавить", callback_data="admin_add_company"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'rates':
        text = "Управление тарифами:\n- Добавить тариф\n- Редактировать тариф"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Добавить", callback_data="admin_add_rate"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'notifications':
        text = "Управление уведомлениями:\n- Отправить уведомление\n- Настроить рассылку"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Отправить", callback_data="admin_send_notification"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'schedules':
        text = "Управление графиками:\n- Создать график\n- Редактировать график"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Создать", callback_data="admin_create_schedule"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'approval':
        text = "Согласование:\n- Смены\n- Переработки\n- Не профильные часы\n- Отпуска"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Смены", callback_data="admin_approve_shifts"))
        keyboard.row(InlineKeyboardButton("Переработки", callback_data="admin_approve_overtime"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

def handle_manager_callback(call, chat_id, message_id, user_role):
    """Handle manager-specific callbacks"""
    action = call.data.split('_')[1]
    
    if action == 'shift':
        text = "Управление сменой:\n- Выйти в смену\n- Закрыть смену\n- Взять оборудование\n- Сдать оборудование\n- Указать номер жилета\n- Указать переработку\n- Указать не профильные часы"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Выйти в смену", callback_data="manager_start_shift"))
        keyboard.row(InlineKeyboardButton("Закрыть смену", callback_data="manager_end_shift"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'start':
        handle_start_shift(chat_id, message_id, user_role, bot)
    elif action == 'end':
        handle_end_shift(chat_id, message_id, user_role, bot)
    elif action == 'confirm':
        # Handle shift confirmation
        if 'start' in call.data:
            text = "Смена успешно начата. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Закрыть смену", "manager_end_shift")
            ], "manager_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
        elif 'end' in call.data:
            text = "Смена успешно завершена. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Назад", "manager_shift")
            ], "manager_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'approval':
        text = "Согласование:\n- Смены\n- Переработки\n- Не профильные часы\n- Отпуска"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Смены", callback_data="manager_approve_shifts"))
        keyboard.row(InlineKeyboardButton("Переработки", callback_data="manager_approve_overtime"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'requests':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action == 'create':
        handle_create_request(chat_id, message_id, user_role, bot)
    elif action == 'view':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action.startswith('request'):
        # Handle request details
        parts = call.data.split('_')
        if len(parts) >= 3:
            request_id = parts[2]
            handle_submit_to_request(chat_id, message_id, request_id, user_role, bot)
    elif action.startswith('confirm') and 'create' in call.data:
        # Handle request creation confirmation
        text = "Заявка успешно создана. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", "manager_view_requests")
        ], "manager_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('select') or action.startswith('submit'):
        # Handle employee selection for requests
        text = "Выберите сотрудника для заявки:"
        keyboard = create_navigation_keyboard([
            ("Сотрудник 1", f"manager_confirm_submit_1"),
            ("Сотрудник 2", f"manager_confirm_submit_2")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('confirm') and 'submit' in call.data:
        # Handle submission confirmation
        text = "Сотрудник успешно заявлен на смену. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", f"{user_role}_view_requests")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'employees':
        handle_employee_list(chat_id, message_id, bot)
    elif action == 'add':
        # This handles the "add employee" callback
        handle_employee_creation(chat_id, message_id, bot)
    elif action == 'search':
        # This handles the "search employee" callback
        handle_employee_search(chat_id, message_id, bot)
    elif action.startswith('edit'):
        # This handles the "edit employee" callback
        # Extract employee ID from callback data
        parts = call.data.split('_')
        if len(parts) >= 4:
            employee_id = parts[3]
            handle_employee_details(chat_id, message_id, employee_id, bot)
    elif action.startswith('block'):
        # This handles the "block employee" callback
        text = "Сотрудник заблокирован."
        keyboard = create_navigation_keyboard([
            ("Назад", "manager_employees")
        ], "manager_employees")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'schedules':
        text = "Управление графиками:\n- Просмотр по дням\n- Редактировать график сотрудника\n- Добавить смену вне графика"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Просмотр", callback_data="manager_view_schedule"))
        keyboard.row(InlineKeyboardButton("Добавить", callback_data="manager_add_schedule"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'absence':
        text = "Отсутствие:\n- Запланировать отсутствие\n- Просмотреть отсутствие\n- Отправить на согласование"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Запланировать", callback_data="manager_plan_absence"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

def handle_supervisor_callback(call, chat_id, message_id, user_role):
    """Handle shift supervisor-specific callbacks"""
    action = call.data.split('_')[1]
    
    if action == 'shift':
        text = "Управление сменой:\n- Выйти в смену\n- Закрыть смену\n- Взять оборудование\n- Сдать оборудование\n- Указать номер жилета\n- Указать переработку\n- Указать не профильные часы"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Выйти в смену", callback_data="supervisor_start_shift"))
        keyboard.row(InlineKeyboardButton("Закрыть смену", callback_data="supervisor_end_shift"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'start':
        handle_start_shift(chat_id, message_id, user_role, bot)
    elif action == 'end':
        handle_end_shift(chat_id, message_id, user_role, bot)
    elif action == 'confirm':
        # Handle shift confirmation
        if 'start' in call.data:
            text = "Смена успешно начата. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Закрыть смену", "supervisor_end_shift")
            ], "supervisor_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
        elif 'end' in call.data:
            text = "Смена успешно завершена. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Назад", "supervisor_shift")
            ], "supervisor_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'approval':
        text = "Согласование:\n- Смены\n- Переработки\n- Не профильные часы\n- Отпуска"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Смены", callback_data="supervisor_approve_shifts"))
        keyboard.row(InlineKeyboardButton("Переработки", callback_data="supervisor_approve_overtime"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'requests':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action == 'create':
        handle_create_request(chat_id, message_id, user_role, bot)
    elif action == 'view':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action.startswith('request'):
        # Handle request details
        parts = call.data.split('_')
        if len(parts) >= 3:
            request_id = parts[2]
            handle_submit_to_request(chat_id, message_id, request_id, user_role, bot)
    elif action.startswith('confirm') and 'create' in call.data:
        # Handle request creation confirmation
        text = "Заявка успешно создана. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", "supervisor_view_requests")
        ], "supervisor_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('select') or action.startswith('submit'):
        # Handle employee selection for requests
        text = "Выберите сотрудника для заявки:"
        keyboard = create_navigation_keyboard([
            ("Сотрудник 1", f"supervisor_confirm_submit_1"),
            ("Сотрудник 2", f"supervisor_confirm_submit_2")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('confirm') and 'submit' in call.data:
        # Handle submission confirmation
        text = "Сотрудник успешно заявлен на смену. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", f"{user_role}_view_requests")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'schedules':
        text = "Управление графиками:\n- Просмотр по дням\n- Редактировать график сотрудника\n- Добавить смену вне графика"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Просмотр", callback_data="supervisor_view_schedule"))
        keyboard.row(InlineKeyboardButton("Добавить", callback_data="supervisor_add_schedule"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'absence':
        text = "Отсутствие:\n- Запланировать отсутствие\n- Просмотреть отсутствие\n- Отправить на согласование"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Запланировать", callback_data="supervisor_plan_absence"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

def handle_employee_callback(call, chat_id, message_id, user_role):
    """Handle employee-specific callbacks"""
    action = call.data.split('_')[1]
    
    if action == 'shift':
        text = "Управление сменой:\n- Выйти в смену\n- Закрыть смену\n- Взять оборудование\n- Сдать оборудование\n- Указать номер жилета\n- Указать переработку\n- Указать не профильные часы"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Выйти в смену", callback_data="employee_start_shift"))
        keyboard.row(InlineKeyboardButton("Закрыть смену", callback_data="employee_end_shift"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'start':
        handle_start_shift(chat_id, message_id, user_role, bot)
    elif action == 'end':
        handle_end_shift(chat_id, message_id, user_role, bot)
    elif action == 'confirm':
        # Handle shift confirmation
        if 'start' in call.data:
            text = "Смена успешно начата. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Закрыть смену", "employee_end_shift")
            ], "employee_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
        elif 'end' in call.data:
            text = "Смена успешно завершена. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Назад", "employee_shift")
            ], "employee_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'absence':
        text = "Отсутствие:\n- Запланировать отсутствие\n- Просмотреть отсутствие\n- Отправить на согласование"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Запланировать", callback_data="employee_plan_absence"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

def handle_outs_manager_callback(call, chat_id, message_id, user_role):
    """Handle outsourced manager-specific callbacks"""
    action = call.data.split('_')[1]
    
    if action == 'shift':
        text = "Управление сменой:\n- Выйти в смену\n- Закрыть смену\n- Взать оборудование\n- Сдать оборудование\n- Указать номер жилета\n- Указать переработку\n- Указать не профильные часы"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Выйти в смену", callback_data="outs_manager_start_shift"))
        keyboard.row(InlineKeyboardButton("Закрыть смену", callback_data="outs_manager_end_shift"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'start':
        handle_start_shift(chat_id, message_id, user_role, bot)
    elif action == 'end':
        handle_end_shift(chat_id, message_id, user_role, bot)
    elif action == 'confirm':
        # Handle shift confirmation
        if 'start' in call.data:
            text = "Смена успешно начата. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Закрыть смену", "outs_manager_end_shift")
            ], "outs_manager_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
        elif 'end' in call.data:
            text = "Смена успешно завершена. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Назад", "outs_manager_shift")
            ], "outs_manager_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'requests':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action == 'create':
        handle_create_request(chat_id, message_id, user_role, bot)
    elif action == 'view':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action.startswith('request'):
        # Handle request details
        parts = call.data.split('_')
        if len(parts) >= 3:
            request_id = parts[2]
            handle_submit_to_request(chat_id, message_id, request_id, user_role, bot)
    elif action.startswith('confirm') and 'create' in call.data:
        # Handle request creation confirmation
        text = "Заявка успешно создана. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", "outs_manager_view_requests")
        ], "outs_manager_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('select') or action.startswith('submit'):
        # Handle employee selection for requests
        text = "Выберите сотрудника для заявки:"
        keyboard = create_navigation_keyboard([
            ("Сотрудник 1", f"outs_manager_confirm_submit_1"),
            ("Сотрудник 2", f"outs_manager_confirm_submit_2")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('confirm') and 'submit' in call.data:
        # Handle submission confirmation
        text = "Сотрудник успешно заявлен на смену. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", f"{user_role}_view_requests")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'rates':
        text = "Тарифы:\n- Создать заявку на тариф\n- Просмотреть заявки\n- Просмотр текущих тарифов"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Создать", callback_data="outs_manager_create_rate"))
        keyboard.row(InlineKeyboardButton("Просмотр", callback_data="outs_manager_view_rates"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'employees':
        handle_employee_list(chat_id, message_id, bot)
    elif action == 'add':
        # This handles the "add employee" callback for outsourced manager
        handle_employee_creation(chat_id, message_id, bot)
    elif action == 'search':
        # This handles the "search employee" callback for outsourced manager
        handle_employee_search(chat_id, message_id, bot)
    elif action.startswith('edit'):
        # This handles the "edit employee" callback for outsourced manager
        # Extract employee ID from callback data
        parts = call.data.split('_')
        if len(parts) >= 4:
            employee_id = parts[3]
            handle_employee_details(chat_id, message_id, employee_id, bot)
    elif action.startswith('block'):
        # This handles the "block employee" callback for outsourced manager
        text = "Сотрудник заблокирован."
        keyboard = create_navigation_keyboard([
            ("Назад", "outs_manager_employees")
        ], "outs_manager_employees")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

def handle_brigadier_callback(call, chat_id, message_id, user_role):
    """Handle brigadier-specific callbacks"""
    action = call.data.split('_')[1]
    
    if action == 'shift':
        text = "Управление сменой:\n- Выйти в смену\n- Закрыть смену\n- Взять оборудование\n- Сдать оборудование\n- Указать номер жилета\n- Указать переработку\n- Указать не профильные часы"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Выйти в смену", callback_data="brigadier_start_shift"))
        keyboard.row(InlineKeyboardButton("Закрыть смену", callback_data="brigadier_end_shift"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'start':
        handle_start_shift(chat_id, message_id, user_role, bot)
    elif action == 'end':
        handle_end_shift(chat_id, message_id, user_role, bot)
    elif action == 'confirm':
        # Handle shift confirmation
        if 'start' in call.data:
            text = "Смена успешно начата. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Закрыть смену", "brigadier_end_shift")
            ], "brigadier_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
        elif 'end' in call.data:
            text = "Смена успешно завершена. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Назад", "brigadier_shift")
            ], "brigadier_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'requests':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action == 'create':
        handle_create_request(chat_id, message_id, user_role, bot)
    elif action == 'view':
        handle_view_requests(chat_id, message_id, user_role, bot)
    elif action.startswith('request'):
        # Handle request details
        parts = call.data.split('_')
        if len(parts) >= 3:
            request_id = parts[2]
            handle_submit_to_request(chat_id, message_id, request_id, user_role, bot)
    elif action.startswith('confirm') and 'create' in call.data:
        # Handle request creation confirmation
        text = "Заявка успешно создана. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", "brigadier_view_requests")
        ], "brigadier_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('select') or action.startswith('submit'):
        # Handle employee selection for requests
        text = "Выберите сотрудника для заявки:"
        keyboard = create_navigation_keyboard([
            ("Сотрудник 1", f"brigadier_confirm_submit_1"),
            ("Сотрудник 2", f"brigadier_confirm_submit_2")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action.startswith('confirm') and 'submit' in call.data:
        # Handle submission confirmation
        text = "Сотрудник успешно заявлен на смену. Информация зафиксирована в Yandex Tracker."
        keyboard = create_navigation_keyboard([
            ("Посмотреть заявки", f"{user_role}_view_requests")
        ], f"{user_role}_requests")
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

def handle_outs_employee_callback(call, chat_id, message_id, user_role):
    """Handle outsourced employee-specific callbacks"""
    action = call.data.split('_')[1]
    
    if action == 'shift':
        text = "Управление сменой:\n- Выйти в смену\n- Закрыть смену\n- Взять оборудование\n- Сдать оборудование\n- Указать номер жилета\n- Указать переработку\n- Указать не профильные часы"
        keyboard = InlineKeyboardMarkup()
        keyboard.row(InlineKeyboardButton("Выйти в смену", callback_data="outs_employee_start_shift"))
        keyboard.row(InlineKeyboardButton("Закрыть смену", callback_data="outs_employee_end_shift"))
        keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    elif action == 'start':
        handle_start_shift(chat_id, message_id, user_role, bot)
    elif action == 'end':
        handle_end_shift(chat_id, message_id, user_role, bot)
    elif action == 'confirm':
        # Handle shift confirmation
        if 'start' in call.data:
            text = "Смена успешно начата. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Закрыть смену", "outs_employee_end_shift")
            ], "outs_employee_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
        elif 'end' in call.data:
            text = "Смена успешно завершена. Информация зафиксирована в Yandex Tracker."
            keyboard = create_navigation_keyboard([
                ("Назад", "outs_employee_shift")
            ], "outs_employee_shift")
            bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)

if __name__ == '__main__':
    logger.info("Starting the Telegram bot...")
    bot.polling(none_stop=True)