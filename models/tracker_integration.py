"""
Module for Yandex Tracker integration
This module handles all interactions with Yandex Tracker API
"""

import requests
import json
from typing import Dict, List, Optional
from config.settings import YT_ORG_ID, YT_TOKEN, YT_PROJECT_ID

class YandexTrackerClient:
    """
    Client for interacting with Yandex Tracker API
    """
    
    def __init__(self):
        if not YT_ORG_ID or not YT_TOKEN:
            raise ValueError("YT_ORG_ID and YT_TOKEN must be set in environment variables")
        
        self.org_id = YT_ORG_ID
        self.token = YT_TOKEN
        self.project_id = YT_PROJECT_ID
        self.base_url = "https://api.tracker.yandex.net/v2"
        self.headers = {
            "Authorization": f"OAuth {self.token}",
            "X-Org-ID": self.org_id,
            "Content-Type": "application/json"
        }
    
    def create_issue(self, issue_data: Dict) -> Dict:
        """
        Create a new issue in Yandex Tracker
        """
        url = f"{self.base_url}/issues"
        response = requests.post(url, headers=self.headers, json=issue_data)
        response.raise_for_status()
        return response.json()
    
    def get_issue(self, issue_key: str) -> Dict:
        """
        Get issue by key from Yandex Tracker
        """
        url = f"{self.base_url}/issues/{issue_key}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()
    
    def update_issue(self, issue_key: str, issue_data: Dict) -> Dict:
        """
        Update an existing issue in Yandex Tracker
        """
        url = f"{self.base_url}/issues/{issue_key}"
        response = requests.patch(url, headers=self.headers, json=issue_data)
        response.raise_for_status()
        return response.json()
    
    def search_issues(self, query: str) -> List[Dict]:
        """
        Search issues in Yandex Tracker
        """
        url = f"{self.base_url}/issues/_search"
        search_data = {
            "query": query,
            "fields": ["key", "summary", "description", "status", "assignee", "created", "updated"]
        }
        response = requests.post(url, headers=self.headers, json=search_data)
        response.raise_for_status()
        return response.json()
    
    def add_comment(self, issue_key: str, comment: str) -> Dict:
        """
        Add a comment to an issue
        """
        url = f"{self.base_url}/issues/{issue_key}/comments"
        comment_data = {"text": comment}
        response = requests.post(url, headers=self.headers, json=comment_data)
        response.raise_for_status()
        return response.json()


class EmployeeManager:
    """
    Manager for employee-related operations using Yandex Tracker
    """
    
    def __init__(self):
        self.tracker = YandexTrackerClient()
    
    def create_employee(self, employee_data: Dict) -> Dict:
        """
        Create a new employee in Yandex Tracker
        """
        issue_data = {
            "queue": "EMP",  # Employee queue
            "summary": f"Сотрудник: {employee_data.get('first_name', '')} {employee_data.get('last_name', '')}",
            "description": "Карточка сотрудника",
            "type": "task",
            "customFields": {
                # Map employee data to custom fields in tracker
                "lastName": employee_data.get('last_name', ''),
                "firstName": employee_data.get('first_name', ''),
                "middleName": employee_data.get('middle_name', ''),
                "birthDate": employee_data.get('birth_date', ''),
                "phone": employee_data.get('phone', ''),
                "telegram": employee_data.get('telegram', ''),
                "company": employee_data.get('company', ''),
                "objects": employee_data.get('objects', []),
                "workEmail": employee_data.get('work_email', ''),
                "passportSeries": employee_data.get('passport_series', ''),
                "passportNumber": employee_data.get('passport_number', ''),
                "passportDivision": employee_data.get('passport_division', ''),
                "passportIssueDate": employee_data.get('passport_issue_date', ''),
                "passportIssuedBy": employee_data.get('passport_issued_by', ''),
                "birthCity": employee_data.get('birth_city', ''),
                "registrationAddress": employee_data.get('registration_address', ''),
                "registrationDate": employee_data.get('registration_date', ''),
                "education": employee_data.get('education', ''),
                "bank": employee_data.get('bank', ''),
                "accountNumber": employee_data.get('account_number', ''),
                "bic": employee_data.get('bic', ''),
                "corrAccount": employee_data.get('corr_account', ''),
                "bankInn": employee_data.get('bank_inn', ''),
                "role": employee_data.get('role', 'employee'),
                "status": employee_data.get('status', 'active')
            }
        }
        return self.tracker.create_issue(issue_data)
    
    def get_employee(self, employee_id: str) -> Dict:
        """
        Get employee by ID from Yandex Tracker
        """
        return self.tracker.get_issue(employee_id)
    
    def update_employee(self, employee_id: str, employee_data: Dict) -> Dict:
        """
        Update employee data in Yandex Tracker
        """
        issue_data = {
            "summary": f"Сотрудник: {employee_data.get('first_name', '')} {employee_data.get('last_name', '')}",
            "customFields": {
                "lastName": employee_data.get('last_name', ''),
                "firstName": employee_data.get('first_name', ''),
                "middleName": employee_data.get('middle_name', ''),
                "birthDate": employee_data.get('birth_date', ''),
                "phone": employee_data.get('phone', ''),
                "telegram": employee_data.get('telegram', ''),
                "company": employee_data.get('company', ''),
                "objects": employee_data.get('objects', []),
                "workEmail": employee_data.get('work_email', ''),
                "passportSeries": employee_data.get('passport_series', ''),
                "passportNumber": employee_data.get('passport_number', ''),
                "passportDivision": employee_data.get('passport_division', ''),
                "passportIssueDate": employee_data.get('passport_issue_date', ''),
                "passportIssuedBy": employee_data.get('passport_issued_by', ''),
                "birthCity": employee_data.get('birth_city', ''),
                "registrationAddress": employee_data.get('registration_address', ''),
                "registrationDate": employee_data.get('registration_date', ''),
                "education": employee_data.get('education', ''),
                "bank": employee_data.get('bank', ''),
                "accountNumber": employee_data.get('account_number', ''),
                "bic": employee_data.get('bic', ''),
                "corrAccount": employee_data.get('corr_account', ''),
                "bankInn": employee_data.get('bank_inn', ''),
                "role": employee_data.get('role', 'employee'),
                "status": employee_data.get('status', 'active')
            }
        }
        return self.tracker.update_issue(employee_id, issue_data)


class CompanyManager:
    """
    Manager for company-related operations using Yandex Tracker
    """
    
    def __init__(self):
        self.tracker = YandexTrackerClient()
    
    def create_company(self, company_data: Dict) -> Dict:
        """
        Create a new company in Yandex Tracker
        """
        issue_data = {
            "queue": "COMP",  # Company queue
            "summary": f"Компания: {company_data.get('full_name', '')}",
            "description": "Карточка компании",
            "type": "task",
            "customFields": {
                "directorFio": company_data.get('director_fio', ''),
                "fullName": company_data.get('full_name', ''),
                "shortName": company_data.get('short_name', ''),
                "inn": company_data.get('inn', ''),
                "actualAddress": company_data.get('actual_address', ''),
                "legalAddress": company_data.get('legal_address', ''),
                "ogrnip": company_data.get('ogrnip', ''),
                "ogrn": company_data.get('ogrn', ''),
                "okpo": company_data.get('okpo', ''),
                "bank": company_data.get('bank', ''),
                "bik": company_data.get('bik', ''),
                "corrAccount": company_data.get('corr_account', ''),
                "account": company_data.get('account', ''),
                "email": company_data.get('email', ''),
                "phone": company_data.get('phone', ''),
                "okved": company_data.get('okved', ''),
                "taxSystem": company_data.get('tax_system', '')
            }
        }
        return self.tracker.create_issue(issue_data)
    
    def get_company(self, company_id: str) -> Dict:
        """
        Get company by ID from Yandex Tracker
        """
        return self.tracker.get_issue(company_id)
    
    def update_company(self, company_id: str, company_data: Dict) -> Dict:
        """
        Update company data in Yandex Tracker
        """
        issue_data = {
            "summary": f"Компания: {company_data.get('full_name', '')}",
            "customFields": {
                "directorFio": company_data.get('director_fio', ''),
                "fullName": company_data.get('full_name', ''),
                "shortName": company_data.get('short_name', ''),
                "inn": company_data.get('inn', ''),
                "actualAddress": company_data.get('actual_address', ''),
                "legalAddress": company_data.get('legal_address', ''),
                "ogrnip": company_data.get('ogrnip', ''),
                "ogrn": company_data.get('ogrn', ''),
                "okpo": company_data.get('okpo', ''),
                "bank": company_data.get('bank', ''),
                "bik": company_data.get('bik', ''),
                "corrAccount": company_data.get('corr_account', ''),
                "account": company_data.get('account', ''),
                "email": company_data.get('email', ''),
                "phone": company_data.get('phone', ''),
                "okved": company_data.get('okved', ''),
                "taxSystem": company_data.get('tax_system', '')
            }
        }
        return self.tracker.update_issue(company_id, issue_data)


class CityManager:
    """
    Manager for city-related operations using Yandex Tracker
    """
    
    def __init__(self):
        self.tracker = YandexTrackerClient()
    
    def create_city(self, city_data: Dict) -> Dict:
        """
        Create a new city in Yandex Tracker
        """
        issue_data = {
            "queue": "CITY",  # City queue
            "summary": f"Город: {city_data.get('name', '')}",
            "description": "Карточка города",
            "type": "task",
            "customFields": {
                "name": city_data.get('name', '')
            }
        }
        return self.tracker.create_issue(issue_data)
    
    def get_city(self, city_id: str) -> Dict:
        """
        Get city by ID from Yandex Tracker
        """
        return self.tracker.get_issue(city_id)


class WarehouseManager:
    """
    Manager for warehouse-related operations using Yandex Tracker
    """
    
    def __init__(self):
        self.tracker = YandexTrackerClient()
    
    def create_warehouse(self, warehouse_data: Dict) -> Dict:
        """
        Create a new warehouse in Yandex Tracker
        """
        issue_data = {
            "queue": "WH",  # Warehouse queue
            "summary": f"Склад: {warehouse_data.get('name', '')}",
            "description": "Карточка склада",
            "type": "task",
            "customFields": {
                "name": warehouse_data.get('name', ''),
                "synonyms": warehouse_data.get('synonyms', []),
                "partnerChatId": warehouse_data.get('partner_chat_id', ''),
                "partnerChatLink": warehouse_data.get('partner_chat_link', ''),
                "warehouseChatId": warehouse_data.get('warehouse_chat_id', ''),
                "warehouseChatLink": warehouse_data.get('warehouse_chat_link', ''),
                "legalEntity": warehouse_data.get('legal_entity', ''),
                "area": warehouse_data.get('area', ''),
                "selfOperated": warehouse_data.get('self_operated', ''),
                "openingDate": warehouse_data.get('opening_date', ''),
                "closingDate": warehouse_data.get('closing_date', ''),
                "status": warehouse_data.get('status', ''),
                "tgCs": warehouse_data.get('tg_cs', ''),
                "phone": warehouse_data.get('phone', ''),
                "workAccount": warehouse_data.get('work_account', '')
            }
        }
        return self.tracker.create_issue(issue_data)
    
    def get_warehouse(self, warehouse_id: str) -> Dict:
        """
        Get warehouse by ID from Yandex Tracker
        """
        return self.tracker.get_issue(warehouse_id)


class ShiftManager:
    """
    Manager for shift-related operations using Yandex Tracker
    """
    
    def __init__(self):
        self.tracker = YandexTrackerClient()
    
    def create_shift(self, shift_data: Dict) -> Dict:
        """
        Create a new shift in Yandex Tracker
        """
        issue_data = {
            "queue": "SHIFT",  # Shift queue
            "summary": f"Смена: {shift_data.get('date', '')} - {shift_data.get('employee_name', '')}",
            "description": "Карточка смены",
            "type": "task",
            "customFields": {
                "date": shift_data.get('date', ''),
                "employee": shift_data.get('employee', ''),
                "employeeName": shift_data.get('employee_name', ''),
                "startTime": shift_data.get('start_time', ''),
                "endTime": shift_data.get('end_time', ''),
                "vestNumber": shift_data.get('vest_number', ''),
                "overtime": shift_data.get('overtime', ''),
                "nonProfileHours": shift_data.get('non_profile_hours', ''),
                "equipmentTaken": shift_data.get('equipment_taken', []),
                "equipmentReturned": shift_data.get('equipment_returned', []),
                "status": shift_data.get('status', 'planned')
            }
        }
        return self.tracker.create_issue(issue_data)
    
    def get_shift(self, shift_id: str) -> Dict:
        """
        Get shift by ID from Yandex Tracker
        """
        return self.tracker.get_issue(shift_id)


class RequestManager:
    """
    Manager for request-related operations using Yandex Tracker
    """
    
    def __init__(self):
        self.tracker = YandexTrackerClient()
    
    def create_request(self, request_data: Dict) -> Dict:
        """
        Create a new request in Yandex Tracker
        """
        issue_data = {
            "queue": "REQ",  # Request queue
            "summary": f"Заявка: {request_data.get('title', '')}",
            "description": request_data.get('description', ''),
            "type": "task",
            "customFields": {
                "title": request_data.get('title', ''),
                "requester": request_data.get('requester', ''),
                "requesterName": request_data.get('requester_name', ''),
                "object": request_data.get('object', ''),
                "requiredEmployees": request_data.get('required_employees', 0),
                "availableSlots": request_data.get('required_employees', 0),  # Initially same as required
                "appliedEmployees": request_data.get('applied_employees', []),
                "status": request_data.get('status', 'open')
            }
        }
        return self.tracker.create_issue(issue_data)
    
    def get_request(self, request_id: str) -> Dict:
        """
        Get request by ID from Yandex Tracker
        """
        return self.tracker.get_issue(request_id)
    
    def update_request_slots(self, request_id: str, slots: int) -> Dict:
        """
        Update available slots in a request
        """
        issue_data = {
            "customFields": {
                "availableSlots": slots
            }
        }
        return self.tracker.update_issue(request_id, issue_data)
    
    def add_employee_to_request(self, request_id: str, employee_id: str) -> Dict:
        """
        Add an employee to a request
        """
        # Get current request data
        request = self.get_request(request_id)
        current_applied = request.get('customFields', {}).get('appliedEmployees', [])
        
        # Add new employee if not already in the list
        if employee_id not in current_applied:
            current_applied.append(employee_id)
            
            issue_data = {
                "customFields": {
                    "appliedEmployees": current_applied,
                    "availableSlots": max(0, request.get('customFields', {}).get('availableSlots', 0) - 1)
                }
            }
            return self.tracker.update_issue(request_id, issue_data)
        
        return request