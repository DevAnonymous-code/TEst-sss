"""
Main bot orchestrator using LangChain chains (similar to SQLDatabaseChain pattern)
"""
import logging
from typing import Dict, Any, Optional

from src.bot.query_parser import QueryParser
from src.bot.intent_classifier import Intent, IntentClassifier, EntityType
from src.bot.entity_extractor import EntityExtractor
from src.bot.response_formatter import ResponseFormatter
from src.handlers.timesheet_handler import TimesheetHandler
from src.handlers.invoice_handler import InvoiceHandler
from src.handlers.expense_handler import ExpenseHandler
from src.handlers.project_handler import ProjectHandler

logger = logging.getLogger(__name__)


class BotOrchestrator:
    """
    Main orchestrator that uses LangChain chains to process queries
    Similar to SQLDatabaseChain but adapted for MongoDB operations
    """
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0):
        """Initialize bot orchestrator"""
        self.query_parser = QueryParser(model_name=model_name, temperature=temperature)
        self.intent_classifier = IntentClassifier()
        self.entity_extractor = EntityExtractor()
        self.response_formatter = ResponseFormatter()
        
        # Initialize handlers
        self.timesheet_handler = TimesheetHandler()
        self.invoice_handler = InvoiceHandler()
        self.expense_handler = ExpenseHandler()
        self.project_handler = ProjectHandler()
    
    def process_query(self, query: str, user_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Process a natural language query and return result
        
        This is the main entry point, similar to SQLDatabaseChain.run()
        """
        try:
            logger.info(f"Processing query: {query}")
            
            # Step 1: Parse query using LangChain
            parsed_query = self.query_parser.parse(query)
            
            if parsed_query.get("error"):
                return {
                    "success": False,
                    "error": "Query parsing failed",
                    "message": parsed_query.get("error"),
                    "result": None
                }
            
            # Step 2: Extract entities from both parsed query and original query
            entities = self.entity_extractor.extract_all_entities(parsed_query, query)
            
            # Step 3: Classify intent and entity type
            intent = self.intent_classifier.classify(parsed_query)
            entity_type = self.intent_classifier.get_entity_type(parsed_query)
            
            # Step 4: Execute operation based on intent and entity type
            result = self._execute_operation(intent, entity_type, entities, parsed_query)
            
            # Step 5: Format response
            formatted_result = self._format_result(result, intent, entity_type)
            
            return {
                "success": True,
                "result": formatted_result,
                "metadata": {
                    "intent": intent.value,
                    "entity_type": entity_type.value if entity_type else None,
                    "entities": entities,
                    "confidence": parsed_query.get("confidence", 0.8)
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing query: {e}", exc_info=True)
            return {
                "success": False,
                "error": "Processing error",
                "message": str(e),
                "result": None
            }
    
    def _execute_operation(
        self,
        intent: Intent,
        entity_type: Optional[EntityType],
        entities: Dict[str, Any],
        parsed_query: Dict[str, Any]
    ) -> Any:
        """Execute database operation based on intent and entity type"""
        
        # CREATE Operations
        if intent == Intent.CREATE:
            if entity_type == EntityType.TIMESHEET:
                return self._create_timesheet(entities)
            elif entity_type == EntityType.INVOICE:
                return self._create_invoice(entities)
            else:
                raise ValueError(f"Create operation not supported for {entity_type}")
        
        # READ Operations
        elif intent == Intent.READ:
            if entity_type == EntityType.TIMESHEET:
                return self._read_timesheet(entities)
            elif entity_type == EntityType.INVOICE:
                return self._read_invoice(entities)
            elif entity_type == EntityType.EXPENSE:
                return self._read_expense(entities)
            elif entity_type == EntityType.PROJECT:
                return self._read_project(entities)
            elif entity_type == EntityType.TALENT:
                return self._read_talent(entities)
            else:
                # Generic query
                return self._generic_query(entities, parsed_query)
        
        # UPDATE Operations
        elif intent == Intent.UPDATE:
            if entity_type == EntityType.TIMESHEET:
                return self._update_timesheet(entities)
            elif entity_type == EntityType.INVOICE:
                return self._update_invoice(entities)
            else:
                raise ValueError(f"Update operation not supported for {entity_type}")
        
        # QUERY Operations (similar to READ but more flexible)
        elif intent == Intent.QUERY:
            return self._generic_query(entities, parsed_query)
        
        else:
            raise ValueError(f"Unsupported intent: {intent}")
    
    def _create_timesheet(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Create timesheet"""
        project_id = entities.get("project_id")
        talent_id = entities.get("talent_id") or entities.get("user_id")
        start_date = entities.get("start_date")
        end_date = entities.get("end_date")
        hours_per_day = entities.get("hours", 8.0)
        
        if not all([project_id, talent_id, start_date, end_date]):
            raise ValueError("Missing required fields: project_id, talent_id, start_date, end_date")
        
        timesheet = self.timesheet_handler.create_timesheet(
            project_id=project_id,
            talent_id=talent_id,
            start_date=start_date,
            end_date=end_date,
            hours_per_day=hours_per_day
        )
        
        return {
            "operation": "create_timesheet",
            "data": timesheet,
            "message": f"Created timesheet {timesheet['timesheet_id']}"
        }
    
    def _create_invoice(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Create invoice"""
        timesheet_id = entities.get("timesheet_id")
        expense_id = entities.get("expense_id")
        talent_id = entities.get("talent_id") or entities.get("user_id")
        
        if timesheet_id:
            invoice = self.invoice_handler.create_timesheet_invoice(timesheet_id)
            return {
                "operation": "create_timesheet_invoice",
                "data": invoice,
                "message": f"Created invoice {invoice['invoice_number']} from timesheet {timesheet_id}"
            }
        elif expense_id:
            if not talent_id:
                raise ValueError("talent_id required for expense invoice")
            invoice = self.invoice_handler.create_expense_invoice(expense_id, talent_id)
            return {
                "operation": "create_expense_invoice",
                "data": invoice,
                "message": f"Created invoice {invoice['invoice_number']} from expense {expense_id}"
            }
        else:
            raise ValueError("Either timesheet_id or expense_id required")
    
    def _read_timesheet(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Read timesheet(s)"""
        timesheet_id = entities.get("timesheet_id")
        
        if timesheet_id:
            timesheet = self.timesheet_handler.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")
            return {
                "operation": "get_timesheet",
                "data": timesheet,
                "entity_type": "TIMESHEET"
            }
        else:
            # List timesheets
            timesheets = self.timesheet_handler.list_timesheets(
                project_id=entities.get("project_id"),
                talent_id=entities.get("talent_id") or entities.get("user_id"),
                status=entities.get("status"),
                start_date=entities.get("start_date"),
                end_date=entities.get("end_date")
            )
            return {
                "operation": "list_timesheets",
                "data": timesheets,
                "entity_type": "TIMESHEET"
            }
    
    def _read_invoice(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Read invoice(s)"""
        invoice_number = entities.get("invoice_number")
        
        if invoice_number:
            invoice = self.invoice_handler.get_invoice(invoice_number)
            if not invoice:
                raise ValueError(f"Invoice {invoice_number} not found")
            return {
                "operation": "get_invoice",
                "data": invoice,
                "entity_type": "INVOICE"
            }
        else:
            invoices = self.invoice_handler.list_invoices(
                status=entities.get("status"),
                project_id=entities.get("project_id"),
                talent_id=entities.get("talent_id") or entities.get("user_id")
            )
            return {
                "operation": "list_invoices",
                "data": invoices,
                "entity_type": "INVOICE"
            }
    
    def _read_expense(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Read expense(s)"""
        expense_id = entities.get("expense_id")
        
        if expense_id:
            expense = self.expense_handler.get_expense(expense_id)
            if not expense:
                raise ValueError(f"Expense {expense_id} not found")
            return {
                "operation": "get_expense",
                "data": expense,
                "entity_type": "EXPENSE"
            }
        else:
            expenses = self.expense_handler.list_expenses(
                project_id=entities.get("project_id"),
                talent_id=entities.get("talent_id") or entities.get("user_id"),
                status=entities.get("status")
            )
            return {
                "operation": "list_expenses",
                "data": expenses,
                "entity_type": "EXPENSE"
            }
    
    def _read_project(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Read project"""
        project_id = entities.get("project_id")
        if not project_id:
            raise ValueError("project_id required")
        
        project = self.project_handler.get_project(project_id)
        if not project:
            raise ValueError(f"Project {project_id} not found")
        
        return {
            "operation": "get_project",
            "data": project,
            "entity_type": "PROJECT"
        }
    
    def _read_talent(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Read talent"""
        talent_id = entities.get("talent_id") or entities.get("user_id")
        if not talent_id:
            raise ValueError("talent_id or user_id required")
        
        talent = self.project_handler.get_talent(talent_id)
        if not talent:
            raise ValueError(f"Talent {talent_id} not found")
        
        return {
            "operation": "get_talent",
            "data": talent,
            "entity_type": "TALENT"
        }
    
    def _update_timesheet(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Update timesheet"""
        timesheet_id = entities.get("timesheet_id")
        if not timesheet_id:
            raise ValueError("timesheet_id required")
        
        start_date = entities.get("start_date")
        end_date = entities.get("end_date")
        status = entities.get("status")
        hours = entities.get("hours")
        
        if status:
            timesheet = self.timesheet_handler.update_timesheet_status(timesheet_id, status)
            return {
                "operation": "update_timesheet_status",
                "data": timesheet,
                "message": f"Updated timesheet {timesheet_id} status to {status}"
            }
        elif start_date and end_date:
            hours_per_day = hours if hours else 8.0
            timesheet = self.timesheet_handler.update_timesheet_dates(
                timesheet_id, start_date, end_date, hours_per_day
            )
            return {
                "operation": "update_timesheet_dates",
                "data": timesheet,
                "message": f"Updated timesheet {timesheet_id} date range"
            }
        else:
            raise ValueError("Either status or start_date/end_date required for update")
    
    def _update_invoice(self, entities: Dict[str, Any]) -> Dict[str, Any]:
        """Update invoice"""
        invoice_number = entities.get("invoice_number")
        if not invoice_number:
            raise ValueError("invoice_number required")
        
        status = entities.get("status")
        if not status:
            raise ValueError("status required for invoice update")
        
        invoice = self.invoice_handler.update_invoice_status(invoice_number, status)
        return {
            "operation": "update_invoice_status",
            "data": invoice,
            "message": f"Updated invoice {invoice_number} status to {status}"
        }
    
    def _generic_query(self, entities: Dict[str, Any], parsed_query: Dict[str, Any]) -> Dict[str, Any]:
        """Handle generic queries that don't fit specific patterns"""
        # Try to infer entity type from entities present
        if entities.get("timesheet_id"):
            return self._read_timesheet(entities)
        elif entities.get("invoice_number"):
            return self._read_invoice(entities)
        elif entities.get("expense_id"):
            return self._read_expense(entities)
        elif entities.get("project_id"):
            return self._read_project(entities)
        else:
            # Default to listing timesheets if no specific entity
            timesheets = self.timesheet_handler.list_timesheets(
                project_id=entities.get("project_id"),
                talent_id=entities.get("talent_id") or entities.get("user_id"),
                status=entities.get("status")
            )
            return {
                "operation": "list_timesheets",
                "data": timesheets,
                "entity_type": "TIMESHEET"
            }
    
    def _format_result(
        self,
        result: Dict[str, Any],
        intent: Intent,
        entity_type: Optional[EntityType]
    ) -> str:
        """Format result into human-readable response"""
        operation = result.get("operation")
        data = result.get("data")
        message = result.get("message")
        result_entity_type = result.get("entity_type")
        
        if message:
            # Success message for create/update operations
            return self.response_formatter.format_success(message, data)
        
        if isinstance(data, list):
            # List of results
            entity_type_str = result_entity_type or (entity_type.value if entity_type else "RESULT")
            return self.response_formatter.format_list(data, entity_type_str)
        elif isinstance(data, dict):
            # Single result
            if result_entity_type == "TIMESHEET":
                return self.response_formatter.format_timesheet(data)
            elif result_entity_type == "INVOICE":
                return self.response_formatter.format_invoice(data)
            elif result_entity_type == "EXPENSE":
                return self.response_formatter.format_expense(data)
            elif result_entity_type == "PROJECT":
                return self.response_formatter.format_project(data)
            else:
                return str(data)
        else:
            return str(data)

