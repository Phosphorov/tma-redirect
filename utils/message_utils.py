"""
Message utilities for the Telegram bot
Handles message editing, user states, and interactive elements
"""

from telebot.types import InlineKeyboardMarkup
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)

# Store user states globally (in production, use a database)
user_states: Dict[int, Dict[str, Any]] = {}

def update_user_state(chat_id: int, message_id: int, data: Dict[str, Any]):
    """
    Update user state with new information
    """
    if chat_id not in user_states:
        user_states[chat_id] = {}
    
    user_states[chat_id].update({
        'last_message_id': message_id,
        **data
    })

def get_user_state(chat_id: int) -> Dict[str, Any]:
    """
    Get user state
    """
    return user_states.get(chat_id, {})

def get_last_message_id(chat_id: int) -> int:
    """
    Get the last message ID for a user
    """
    return user_states.get(chat_id, {}).get('last_message_id', None)

def create_back_button_keyboard() -> InlineKeyboardMarkup:
    """
    Create a keyboard with just a back button
    """
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton("Назад", callback_data="back_to_main"))
    return keyboard

def create_navigation_keyboard(buttons: list, back_callback: str = "back_to_main") -> InlineKeyboardMarkup:
    """
    Create a keyboard with provided buttons and a back button
    :param buttons: List of tuples (button_text, callback_data)
    :param back_callback: Callback data for the back button
    """
    from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
    keyboard = InlineKeyboardMarkup()
    
    # Add main buttons
    for text, callback in buttons:
        keyboard.row(InlineKeyboardButton(text, callback_data=callback))
    
    # Add back button at the end
    keyboard.row(InlineKeyboardButton("Назад", callback_data=back_callback))
    
    return keyboard

def format_employee_info(employee_data: Dict) -> str:
    """
    Format employee information for display
    """
    return f"""
ФИО: {employee_data.get('lastName', '')} {employee_data.get('firstName', '')} {employee_data.get('middleName', '')}
Дата рождения: {employee_data.get('birthDate', '')}
Телефон: {employee_data.get('phone', '')}
Telegram: {employee_data.get('telegram', '')}
Компания: {employee_data.get('company', '')}
Роль: {employee_data.get('role', '')}
Статус: {employee_data.get('status', '')}
    """.strip()

def format_company_info(company_data: Dict) -> str:
    """
    Format company information for display
    """
    return f"""
Полное наименование: {company_data.get('fullName', '')}
Сокращенное наименование: {company_data.get('shortName', '')}
ИНН: {company_data.get('inn', '')}
Фактический адрес: {company_data.get('actualAddress', '')}
Юридический адрес: {company_data.get('legalAddress', '')}
Руководитель: {company_data.get('directorFio', '')}
    """.strip()

def format_shift_info(shift_data: Dict) -> str:
    """
    Format shift information for display
    """
    return f"""
Дата: {shift_data.get('date', '')}
Сотрудник: {shift_data.get('employeeName', '')}
Время начала: {shift_data.get('startTime', '')}
Время окончания: {shift_data.get('endTime', '')}
Номер жилета: {shift_data.get('vestNumber', '')}
Статус: {shift_data.get('status', '')}
    """.strip()

def format_request_info(request_data: Dict) -> str:
    """
    Format request information for display
    """
    applied_count = len(request_data.get('appliedEmployees', []))
    required_count = request_data.get('requiredEmployees', 0)
    available_slots = request_data.get('availableSlots', 0)
    
    return f"""
Заголовок: {request_data.get('title', '')}
Объект: {request_data.get('object', '')}
Необходимо сотрудников: {required_count}
Заявлено сотрудников: {applied_count}
Свободных мест: {available_slots}
Статус: {request_data.get('status', '')}
    """.strip()