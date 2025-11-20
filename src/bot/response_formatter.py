"""
Response formatter for database results
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class ResponseFormatter:
    """Format database results into human-readable responses"""
    
    @staticmethod
    def format_timesheet(timesheet: Dict[str, Any]) -> str:
        """Format timesheet data"""
        lines = [
            f"Timesheet: {timesheet.get('timesheet_id', 'N/A')}",
            f"Project ID: {timesheet.get('project_id', 'N/A')}",
            f"Talent ID: {timesheet.get('user_id', 'N/A')}",
            f"Date Range: {timesheet.get('start_date', 'N/A')} to {timesheet.get('end_date', 'N/A')}",
            f"Status: {timesheet.get('status', 'N/A')}",
            f"Total Hours: {timesheet.get('total_hours', 0)}"
        ]
        
        entries = timesheet.get('entries', [])
        if entries:
            lines.append(f"\nEntries ({len(entries)}):")
            for entry in entries[:10]:  # Show first 10 entries
                date = entry.get('date', 'N/A')
                hours = entry.get('hours', 0)
                lines.append(f"  - {date}: {hours} hours")
            if len(entries) > 10:
                lines.append(f"  ... and {len(entries) - 10} more entries")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_invoice(invoice: Dict[str, Any]) -> str:
        """Format invoice data"""
        lines = [
            f"Invoice: {invoice.get('invoice_number', 'N/A')}",
            f"Status: {invoice.get('status', 'N/A')}",
            f"Currency: {invoice.get('currency', 'N/A')}"
        ]
        
        if invoice.get('project_id'):
            lines.append(f"Project ID: {invoice.get('project_id')}")
        if invoice.get('talent_id'):
            lines.append(f"Talent ID: {invoice.get('talent_id')}")
        if invoice.get('timesheet_id'):
            lines.append(f"Timesheet ID: {invoice.get('timesheet_id')}")
        if invoice.get('expense_id'):
            lines.append(f"Expense ID: {invoice.get('expense_id')}")
        
        if invoice.get('issue_date'):
            lines.append(f"Issue Date: {invoice.get('issue_date')}")
        if invoice.get('due_date'):
            lines.append(f"Due Date: {invoice.get('due_date')}")
        
        items = invoice.get('items', [])
        if items:
            total = sum(item.get('amount', 0) for item in items)
            lines.append(f"\nItems ({len(items)}):")
            for item in items[:10]:  # Show first 10 items
                desc = item.get('description', 'N/A')
                amount = item.get('amount', 0)
                lines.append(f"  - {desc}: {amount}")
            if len(items) > 10:
                lines.append(f"  ... and {len(items) - 10} more items")
            lines.append(f"Total: {total} {invoice.get('currency', '')}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_expense(expense: Dict[str, Any]) -> str:
        """Format expense data"""
        lines = [
            f"Expense ID: {expense.get('expense_id', 'N/A')}",
            f"Project ID: {expense.get('project_id', 'N/A')}",
            f"User ID: {expense.get('user_id', 'N/A')}",
            f"Status: {expense.get('status', 'N/A')}",
            f"Currency: {expense.get('currency', 'N/A')}",
            f"Total Amount: {expense.get('total_amount', 0)}"
        ]
        
        items = expense.get('items', [])
        if items:
            lines.append(f"\nItems ({len(items)}):")
            for item in items[:10]:
                desc = item.get('description', 'N/A')
                amount = item.get('amount', 0)
                lines.append(f"  - {desc}: {amount}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_project(project: Dict[str, Any]) -> str:
        """Format project data"""
        lines = [
            f"Project ID: {project.get('project_id', 'N/A')}",
            f"Project Name: {project.get('project_name', 'N/A')}",
            f"Status: {project.get('status', 'N/A')}"
        ]
        
        if project.get('client_id'):
            lines.append(f"Client ID: {project.get('client_id')}")
        if project.get('talent_id'):
            lines.append(f"Talent ID: {project.get('talent_id')}")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_list(results: List[Dict[str, Any]], entity_type: str) -> str:
        """Format a list of results"""
        if not results:
            return f"No {entity_type.lower()}s found."
        
        lines = [f"Found {len(results)} {entity_type.lower()}(s):\n"]
        
        for i, result in enumerate(results[:20], 1):  # Show first 20
            if entity_type == "TIMESHEET":
                lines.append(f"{i}. {ResponseFormatter.format_timesheet(result)}")
            elif entity_type == "INVOICE":
                lines.append(f"{i}. {ResponseFormatter.format_invoice(result)}")
            elif entity_type == "EXPENSE":
                lines.append(f"{i}. {ResponseFormatter.format_expense(result)}")
            elif entity_type == "PROJECT":
                lines.append(f"{i}. {ResponseFormatter.format_project(result)}")
            else:
                lines.append(f"{i}. {result}")
            
            if i < len(results):
                lines.append("")
        
        if len(results) > 20:
            lines.append(f"\n... and {len(results) - 20} more results")
        
        return "\n".join(lines)
    
    @staticmethod
    def format_success(message: str, data: Optional[Dict[str, Any]] = None) -> str:
        """Format success message"""
        lines = [f"✓ {message}"]
        if data:
            lines.append("\nDetails:")
            for key, value in data.items():
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)
    
    @staticmethod
    def format_error(error: str, details: Optional[Dict[str, Any]] = None) -> str:
        """Format error message"""
        lines = [f"✗ Error: {error}"]
        if details:
            lines.append("\nDetails:")
            for key, value in details.items():
                lines.append(f"  {key}: {value}")
        return "\n".join(lines)

