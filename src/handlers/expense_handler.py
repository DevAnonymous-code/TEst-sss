"""
Expense operation handler
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from bson import ObjectId
from src.database import get_collection, DatabaseModels

logger = logging.getLogger(__name__)


class ExpenseHandler:
    """Handle expense database operations"""
    
    def __init__(self):
        self.collection = get_collection(DatabaseModels.EXPENSES)
    
    def get_expense(self, expense_id: str) -> Optional[Dict[str, Any]]:
        """Get expense by ID"""
        try:
            expense = self.collection.find_one({"expense_id": expense_id})
            if expense and "_id" in expense:
                expense["_id"] = str(expense["_id"])
            return expense
        except Exception as e:
            logger.error(f"Error getting expense: {e}")
            raise
    
    def list_expenses(
        self,
        project_id: Optional[str] = None,
        talent_id: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List expenses with filters"""
        try:
            query = {}
            
            if project_id:
                query["project_id"] = project_id
            if talent_id:
                query["user_id"] = talent_id
            if status:
                query["status"] = status
            
            expenses = list(self.collection.find(query))
            
            # Convert ObjectId to string
            for expense in expenses:
                if "_id" in expense:
                    expense["_id"] = str(expense["_id"])
            
            logger.info(f"Found {len(expenses)} expenses")
            return expenses
            
        except Exception as e:
            logger.error(f"Error listing expenses: {e}")
            raise
    
    def get_expense_total(self, expense_id: str) -> float:
        """Get total amount for an expense"""
        expense = self.get_expense(expense_id)
        if not expense:
            raise ValueError(f"Expense {expense_id} not found")
        return expense.get("total_amount", 0.0)

