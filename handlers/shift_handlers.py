"""
Shift-related handlers for the Telegram bot
"""

from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
from models.tracker_integration import ShiftManager, RequestManager
from utils.message_utils import create_navigation_keyboard, format_shift_info, format_request_info
import logging

logger = logging.getLogger(__name__)

def handle_start_shift(chat_id, message_id, user_role, bot):
    """
    Handle starting a shift
    """
    try:
        text = "Начало смены:\n\nДля начала смены укажите:\n1. Дату смены\n2. Время начала\n3. Номер жилета (если требуется)\n\nСистема зафиксирует начало смены в Yandex Tracker."
        
        # Create appropriate back button based on user role
        back_callback = f"{user_role.replace('outs_', '').replace('staff_', '')}_shift" if user_role != 'employee' else "employee_shift"
        
        keyboard = create_navigation_keyboard([
            ("Подтвердить начало смены", f"{user_role}_confirm_start_shift"),
            ("Отмена", back_callback)
        ], back_callback)
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_start_shift: {e}")

def handle_end_shift(chat_id, message_id, user_role, bot):
    """
    Handle ending a shift
    """
    try:
        text = "Завершение смены:\n\nДля завершения смены укажите:\n1. Время окончания\n2. Оборудование, которое сдаете\n3. Дополнительная информация\n\nСистема зафиксирует окончание смены в Yandex Tracker."
        
        # Create appropriate back button based on user role
        back_callback = f"{user_role.replace('outs_', '').replace('staff_', '')}_shift" if user_role != 'employee' else "employee_shift"
        
        keyboard = create_navigation_keyboard([
            ("Подтвердить окончание смены", f"{user_role}_confirm_end_shift"),
            ("Отмена", back_callback)
        ], back_callback)
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_end_shift: {e}")

def handle_submit_to_request(chat_id, message_id, request_id, user_role, bot):
    """
    Handle submitting an employee to a request
    """
    try:
        # In a real implementation, you would fetch request details from Yandex Tracker
        # For now, we'll use mock data
        request_data = {
            'title': 'Заявка на сотрудников',
            'object': 'Склад №1',
            'requiredEmployees': 5,
            'appliedEmployees': ['EMP001', 'EMP002'],
            'availableSlots': 3,
            'status': 'open'
        }
        
        text = format_request_info(request_data)
        
        if request_data['availableSlots'] > 0:
            text += f"\n\nВы можете заявить себя или своих сотрудников на эту заявку."
            
            # For different user roles, show appropriate options
            if user_role in ['manager', 'shift_supervisor']:
                # Show option to submit their own employees
                keyboard = create_navigation_keyboard([
                    ("Заявить своих сотрудников", f"{user_role}_select_employees_{request_id}"),
                    ("Заявить себя", f"{user_role}_submit_self_{request_id}")
                ], f"{user_role}_requests")
            elif user_role in ['outs_staff_manager', 'brigadier']:
                # Show option to submit employees from their company
                keyboard = create_navigation_keyboard([
                    ("Заявить сотрудников компании", f"{user_role}_select_employees_{request_id}")
                ], f"{user_role}_requests")
            elif user_role in ['employee', 'outs_employee']:
                # Show option to submit themselves
                keyboard = create_navigation_keyboard([
                    ("Заявить себя", f"{user_role}_submit_self_{request_id}")
                ], f"{user_role}_requests")
            else:
                keyboard = create_navigation_keyboard([
                    ("Назад", f"{user_role}_requests")
                ], f"{user_role}_requests")
        else:
            text += f"\n\nК сожалению, все места в этой заявке уже заняты."
            keyboard = create_navigation_keyboard([
                ("Назад", f"{user_role}_requests")
            ], f"{user_role}_requests")
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_submit_to_request: {e}")

def handle_view_requests(chat_id, message_id, user_role, bot):
    """
    Handle viewing requests
    """
    try:
        # In a real implementation, you would fetch requests from Yandex Tracker
        # For now, we'll use mock data
        text = "Доступные заявки:\n\n1. Заявка на склад №1 - 5 мест (3 свободных)\n2. Заявка на склад №2 - 3 места (1 свободное)\n3. Заявка на склад №3 - 2 места (2 свободных)\n\n(В реальной системе заявки загружаются из Yandex Tracker)"
        
        keyboard = create_navigation_keyboard([
            ("Заявка 1", f"{user_role}_request_details_1"),
            ("Заявка 2", f"{user_role}_request_details_2"),
            ("Заявка 3", f"{user_role}_request_details_3")
        ], f"{user_role}_requests")
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_view_requests: {e}")

def handle_create_request(chat_id, message_id, user_role, bot):
    """
    Handle creating a new request
    """
    try:
        text = "Создание заявки на сотрудников:\n\nДля создания заявки укажите:\n1. Объект (склад)\n2. Количество необходимых сотрудников\n3. Требуемые должности/навыки\n4. Дата и время работы\n\nСистема создаст заявку в Yandex Tracker, которая будет доступна для заявления сотрудникам."
        
        keyboard = create_navigation_keyboard([
            ("Создать заявку", f"{user_role}_confirm_create_request"),
            ("Назад", f"{user_role}_requests")
        ], f"{user_role}_requests")
        
        bot.edit_message_text(chat_id=chat_id, message_id=message_id, text=text, reply_markup=keyboard)
    except Exception as e:
        logger.error(f"Error in handle_create_request: {e}")