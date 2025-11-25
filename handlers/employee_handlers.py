"""
Employee-related handlers for the Telegram bot
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.tracker_integration import EmployeeManager
from utils.message_utils import create_navigation_keyboard, format_employee_info
import logging

logger = logging.getLogger(__name__)

def handle_employee_creation(chat_id, message_id, bot):
    """
    Handle employee creation process
    """
    try:
        # For now, we'll just send a message that employee creation is initiated
        # In a real implementation, you would collect employee data step by step
        
        text = "Создание сотрудника:\n\nВведите данные сотрудника по следующим полям:\n1. Фамилия\n2. Имя\n3. Отчество\n4. Дата рождения\n5. Телефон\n6. Telegram (ID или @username)\n7. Компания\n8. Рабочая почта\n\nДля аутстафф сотрудников также потребуются:\n- Серия паспорта\n- Номер паспорта\n- и другие данные"
        
        keyboard = create_navigation_keyboard([
            ("Назад", "manager_employees")
        ], "manager_employees")
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_employee_creation: {e}")

def handle_employee_list(chat_id, message_id, bot):
    """
    Handle employee list display
    """
    try:
        # In a real implementation, you would fetch employees from Yandex Tracker
        # For now, we'll just send a placeholder message
        
        text = "Список сотрудников:\n\n1. Иванов Иван Иванович\n2. Петров Петр Петрович\n3. Сидоров Сидор Сидорович\n\n(В реальной системе список загружается из Yandex Tracker)"
        
        keyboard = create_navigation_keyboard([
            ("Добавить сотрудника", "manager_add_employee"),
            ("Найти сотрудника", "manager_search_employee")
        ], "manager_employees")
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_employee_list: {e}")

def handle_employee_search(chat_id, message_id, bot):
    """
    Handle employee search
    """
    try:
        text = "Поиск сотрудника:\n\nВведите ФИО или ID сотрудника для поиска:"
        
        keyboard = create_navigation_keyboard([
            ("Назад", "manager_employees")
        ], "manager_employees")
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_employee_search: {e}")

def handle_employee_details(chat_id, message_id, employee_id, bot):
    """
    Handle employee details display
    """
    try:
        # In a real implementation, you would fetch employee details from Yandex Tracker
        # For now, we'll use mock data
        
        employee_data = {
            'lastName': 'Иванов',
            'firstName': 'Иван',
            'middleName': 'Иванович',
            'birthDate': '1990-01-01',
            'phone': '+7 (123) 456-78-90',
            'telegram': '@ivanov_ivan',
            'company': 'АО "Рога и копыта"',
            'role': 'employee',
            'status': 'active'
        }
        
        text = format_employee_info(employee_data)
        
        keyboard = create_navigation_keyboard([
            ("Редактировать", f"manager_edit_employee_{employee_id}"),
            ("Заблокировать", f"manager_block_employee_{employee_id}")
        ], "manager_employees")
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_employee_details: {e}")