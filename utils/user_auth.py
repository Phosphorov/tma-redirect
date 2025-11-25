"""
User authentication and role management utilities
"""

import os
from typing import Dict, Optional
from models.tracker_integration import EmployeeManager

class UserRoleManager:
    """
    Manages user roles and permissions based on Yandex Tracker data
    """
    
    def __init__(self):
        self.employee_manager = EmployeeManager()
    
    def get_user_role(self, telegram_id: str) -> Optional[str]:
        """
        Get user role based on their Telegram ID from Yandex Tracker
        In a real implementation, this would search for an employee with this telegram ID
        """
        # Check if this is the admin user
        admin_telegram_id = os.getenv('ADMIN_TELEGRAM_ID')
        if admin_telegram_id and str(telegram_id) == str(admin_telegram_id):
            return 'admin'
        
        # In a real implementation, we would search for an employee with this telegram ID
        # For now, returning a default role for demonstration
        # This is a simplified implementation - in reality, you'd search in Yandex Tracker
        # for an employee record that has this telegram_id
        try:
            # Search for employee with matching telegram ID
            # This is a placeholder implementation
            employees = self.search_employees_by_telegram_id(telegram_id)
            if employees:
                # Return the role of the first matching employee
                # In real implementation, you'd get this from the employee record
                return employees[0].get('role', 'employee')
            return 'employee'  # Default role
        except Exception:
            return 'employee'  # Default role if error occurs
    
    def search_employees_by_telegram_id(self, telegram_id: str) -> list:
        """
        Search for employees by Telegram ID in Yandex Tracker
        This is a placeholder method - in real implementation it would query the tracker
        """
        # In a real implementation, this would query Yandex Tracker for employees
        # with the matching telegram ID
        # For now, returning a mock result
        return [{'role': 'employee', 'id': f'EMP-{telegram_id}'}]
    
    def has_permission(self, user_role: str, required_role: str) -> bool:
        """
        Check if user has permission based on role hierarchy
        Role hierarchy (from highest to lowest):
        - admin
        - manager
        - shift_supervisor
        - employee
        - outs_staff_manager
        - brigadier
        - outs_employee
        """
        role_hierarchy = {
            'admin': 7,
            'manager': 6,
            'shift_supervisor': 5,
            'employee': 4,
            'outs_staff_manager': 3,
            'brigadier': 2,
            'outs_employee': 1
        }
        
        user_level = role_hierarchy.get(user_role, 0)
        required_level = role_hierarchy.get(required_role, 0)
        
        return user_level >= required_level

def get_user_role_from_tracker(telegram_id: str) -> str:
    """
    Convenience function to get user role from tracker
    """
    role_manager = UserRoleManager()
    return role_manager.get_user_role(telegram_id)