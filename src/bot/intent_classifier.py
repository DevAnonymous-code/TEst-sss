"""
Intent classifier for user queries
"""
import logging
from typing import Dict, Any
from enum import Enum

logger = logging.getLogger(__name__)


class Intent(Enum):
    """Query intent types"""
    CREATE = "CREATE"
    READ = "READ"
    UPDATE = "UPDATE"
    DELETE = "DELETE"
    QUERY = "QUERY"


class EntityType(Enum):
    """Entity types in the database"""
    TIMESHEET = "TIMESHEET"
    INVOICE = "INVOICE"
    EXPENSE = "EXPENSE"
    PROJECT = "PROJECT"
    TALENT = "TALENT"


class IntentClassifier:
    """Classify user query intent"""
    
    @staticmethod
    def classify(parsed_query: Dict[str, Any]) -> Intent:
        """Classify intent from parsed query"""
        intent_str = parsed_query.get("intent", "QUERY").upper()
        
        try:
            return Intent(intent_str)
        except ValueError:
            logger.warning(f"Unknown intent: {intent_str}, defaulting to QUERY")
            return Intent.QUERY
    
    @staticmethod
    def get_entity_type(parsed_query: Dict[str, Any]) -> EntityType:
        """Get entity type from parsed query"""
        entity_type_str = parsed_query.get("entity_type")
        
        if not entity_type_str:
            return None
        
        try:
            return EntityType(entity_type_str.upper())
        except ValueError:
            logger.warning(f"Unknown entity type: {entity_type_str}")
            return None

