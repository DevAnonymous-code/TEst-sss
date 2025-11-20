"""
Database models and schemas
"""
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime


class DatabaseModels:
    """Database collection names and field references"""
    
    # Collection names
    TIMESHEETS = "timesheets"
    INVOICES = "invoices"
    EXPENSES = "expenses"
    PROJECTS = "projects"
    TALENTS = "talents"
    TALENT_INVOICE = "talentInvoice"
    BILLING_INFO = "billingInformation"
    OZ_MASTER_DATA = "ozMasterData"
    
    # Common field names
    ID = "_id"
    TIMESHEET_ID = "timesheet_id"
    INVOICE_NUMBER = "invoice_number"
    EXPENSE_ID = "expense_id"
    PROJECT_ID = "project_id"
    USER_ID = "user_id"
    TALENT_ID = "talent_id"
    CLIENT_ID = "client_id"
    STATUS = "status"
    START_DATE = "start_date"
    END_DATE = "end_date"
    TOTAL_HOURS = "total_hours"
    ENTRIES = "entries"
    ITEMS = "items"
    CURRENCY = "currency"
    ISSUE_DATE = "issue_date"
    DUE_DATE = "due_date"
    TOTAL_AMOUNT = "total_amount"


class TimesheetEntry(BaseModel):
    """Timesheet entry model"""
    date: str
    hours: float
    description: Optional[str] = None


class Timesheet(BaseModel):
    """Timesheet model"""
    _id: Optional[str] = None
    timesheet_id: str
    project_id: str
    user_id: str
    start_date: str
    end_date: str
    status: str
    entries: List[Dict[str, Any]] = []
    total_hours: float = 0.0


class Invoice(BaseModel):
    """Invoice model"""
    _id: Optional[str] = None
    invoice_number: str
    project_id: Optional[str] = None
    talent_id: Optional[str] = None
    timesheet_id: Optional[str] = None
    expense_id: Optional[str] = None
    status: str
    items: List[Dict[str, Any]] = []
    currency: str
    issue_date: Optional[str] = None
    due_date: Optional[str] = None


class Expense(BaseModel):
    """Expense model"""
    _id: Optional[str] = None
    expense_id: str
    project_id: str
    user_id: str
    currency: str
    status: str
    items: List[Dict[str, Any]] = []
    total_amount: float = 0.0


class Project(BaseModel):
    """Project model"""
    _id: Optional[str] = None
    project_id: str
    project_name: str
    client_id: Optional[str] = None
    talent_id: Optional[str] = None
    status: Optional[str] = None

