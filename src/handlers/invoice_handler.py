"""
Invoice operation handler
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from src.database import get_collection, DatabaseModels
from src.handlers.timesheet_handler import TimesheetHandler
from src.handlers.expense_handler import ExpenseHandler

logger = logging.getLogger(__name__)


class InvoiceHandler:
    """Handle invoice database operations"""
    
    def __init__(self):
        self.collection = get_collection(DatabaseModels.INVOICES)
        self.timesheet_handler = TimesheetHandler()
        self.expense_handler = ExpenseHandler()
        self.talent_invoice_collection = get_collection(DatabaseModels.TALENT_INVOICE)
        self.billing_info_collection = get_collection(DatabaseModels.BILLING_INFO)
        self.oz_master_data_collection = get_collection(DatabaseModels.OZ_MASTER_DATA)
    
    def create_timesheet_invoice(self, timesheet_id: str) -> Dict[str, Any]:
        """Create invoice from timesheet"""
        try:
            # Get timesheet
            timesheet = self.timesheet_handler.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")
            
            project_id = timesheet.get("project_id")
            talent_id = timesheet.get("user_id")
            
            # Get talent invoice settings
            talent_invoice = self.talent_invoice_collection.find_one({
                "project_id": project_id,
                "talent_id": talent_id
            })
            
            if not talent_invoice:
                raise ValueError(f"Talent invoice settings not found for project {project_id} and talent {talent_id}")
            
            rate_type = talent_invoice.get("talentInvoiceRateType", "Hourly")
            rate_value = talent_invoice.get("talentInvoiceRateValue", 0)
            currency = talent_invoice.get("talentInvoicingCurrency", "USD")
            
            # Calculate invoice amount
            total_hours = timesheet.get("total_hours", 0)
            invoice_amount = 0.0
            
            if rate_type == "Hourly":
                invoice_amount = total_hours * rate_value
            elif rate_type == "Daily":
                # Assume 8 hours per day
                days = total_hours / 8.0
                invoice_amount = days * rate_value
            elif rate_type == "Weekly":
                weeks = total_hours / (8.0 * 5)  # 5 days per week
                invoice_amount = weeks * rate_value
            elif rate_type == "Monthly":
                # Approximate months
                months = total_hours / (8.0 * 20)  # 20 days per month
                invoice_amount = months * rate_value
            
            # Generate invoice number
            now = datetime.now()
            invoice_number = f"INV-{now.strftime('%Y%m')}-{now.microsecond % 1000}"
            
            # Create invoice items
            items = [{
                "description": f"Timesheet {timesheet_id} - {total_hours} hours",
                "quantity": total_hours,
                "rate": rate_value,
                "amount": invoice_amount,
                "rate_type": rate_type
            }]
            
            # Get billing information for due date
            billing_info = self.billing_info_collection.find_one({"project_id": project_id})
            due_days = 30  # Default
            if billing_info and "supply_address" in billing_info:
                # Could extract payment terms from billing info
                pass
            
            issue_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=due_days)).strftime("%Y-%m-%d")
            
            invoice = {
                "invoice_number": invoice_number,
                "project_id": project_id,
                "talent_id": talent_id,
                "timesheet_id": timesheet_id,
                "status": "draft",
                "items": items,
                "currency": currency,
                "issue_date": issue_date,
                "due_date": due_date,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.collection.insert_one(invoice)
            invoice["_id"] = str(result.inserted_id)
            
            logger.info(f"Created invoice: {invoice_number} from timesheet {timesheet_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error creating timesheet invoice: {e}")
            raise
    
    def create_expense_invoice(self, expense_id: str, talent_id: str) -> Dict[str, Any]:
        """Create invoice from expense"""
        try:
            # Get expense
            expense = self.expense_handler.get_expense(expense_id)
            if not expense:
                raise ValueError(f"Expense {expense_id} not found")
            
            project_id = expense.get("project_id")
            total_amount = expense.get("total_amount", 0)
            currency = expense.get("currency", "USD")
            
            # Generate invoice number
            now = datetime.now()
            invoice_number = f"INV-{now.strftime('%Y%m')}-{now.microsecond % 1000}"
            
            # Create invoice items from expense items
            items = []
            expense_items = expense.get("items", [])
            for item in expense_items:
                items.append({
                    "description": item.get("description", "Expense item"),
                    "quantity": item.get("quantity", 1),
                    "rate": item.get("amount", 0),
                    "amount": item.get("amount", 0)
                })
            
            # If no items, create one from total
            if not items:
                items.append({
                    "description": f"Expense {expense_id}",
                    "quantity": 1,
                    "rate": total_amount,
                    "amount": total_amount
                })
            
            issue_date = datetime.now().strftime("%Y-%m-%d")
            due_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
            
            invoice = {
                "invoice_number": invoice_number,
                "project_id": project_id,
                "talent_id": talent_id,
                "expense_id": expense_id,
                "status": "draft",
                "items": items,
                "currency": currency,
                "issue_date": issue_date,
                "due_date": due_date,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.collection.insert_one(invoice)
            invoice["_id"] = str(result.inserted_id)
            
            logger.info(f"Created invoice: {invoice_number} from expense {expense_id}")
            return invoice
            
        except Exception as e:
            logger.error(f"Error creating expense invoice: {e}")
            raise
    
    def get_invoice(self, invoice_number: str) -> Optional[Dict[str, Any]]:
        """Get invoice by number"""
        try:
            invoice = self.collection.find_one({"invoice_number": invoice_number})
            if invoice and "_id" in invoice:
                invoice["_id"] = str(invoice["_id"])
            return invoice
        except Exception as e:
            logger.error(f"Error getting invoice: {e}")
            raise
    
    def update_invoice_status(self, invoice_number: str, status: str) -> Dict[str, Any]:
        """Update invoice status"""
        try:
            valid_statuses = ["draft", "sent", "paid", "cancelled"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")
            
            result = self.collection.update_one(
                {"invoice_number": invoice_number},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise ValueError(f"Invoice {invoice_number} not found")
            
            updated_invoice = self.get_invoice(invoice_number)
            logger.info(f"Updated invoice status: {invoice_number} -> {status}")
            return updated_invoice
            
        except Exception as e:
            logger.error(f"Error updating invoice status: {e}")
            raise
    
    def list_invoices(
        self,
        status: Optional[str] = None,
        project_id: Optional[str] = None,
        talent_id: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List invoices with filters"""
        try:
            query = {}
            
            if status:
                query["status"] = status
            if project_id:
                query["project_id"] = project_id
            if talent_id:
                query["talent_id"] = talent_id
            if start_date:
                query["issue_date"] = {"$gte": start_date}
            if end_date:
                if "issue_date" in query:
                    query["issue_date"]["$lte"] = end_date
                else:
                    query["issue_date"] = {"$lte": end_date}
            
            invoices = list(self.collection.find(query))
            
            # Convert ObjectId to string
            for invoice in invoices:
                if "_id" in invoice:
                    invoice["_id"] = str(invoice["_id"])
            
            logger.info(f"Found {len(invoices)} invoices")
            return invoices
            
        except Exception as e:
            logger.error(f"Error listing invoices: {e}")
            raise

