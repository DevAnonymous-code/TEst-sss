"""
Entity extractor for IDs, dates, amounts, etc.
"""
import re
import logging
from typing import Dict, Any, Optional
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)


class EntityExtractor:
    """Extract entities from parsed queries"""
    
    # Regex patterns
    TIMESHEET_ID_PATTERN = r'TS-\d{6}-\d+'
    INVOICE_NUMBER_PATTERN = r'INV-\d{6}-\d+'
    UUID_PATTERN = r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}'
    DATE_PATTERN = r'\d{4}-\d{2}-\d{2}'
    
    @staticmethod
    def extract_timesheet_id(text: str) -> Optional[str]:
        """Extract timesheet ID from text"""
        match = re.search(EntityExtractor.TIMESHEET_ID_PATTERN, text, re.IGNORECASE)
        return match.group() if match else None
    
    @staticmethod
    def extract_invoice_number(text: str) -> Optional[str]:
        """Extract invoice number from text"""
        match = re.search(EntityExtractor.INVOICE_NUMBER_PATTERN, text, re.IGNORECASE)
        return match.group() if match else None
    
    @staticmethod
    def extract_uuid(text: str) -> Optional[str]:
        """Extract UUID from text"""
        match = re.search(EntityExtractor.UUID_PATTERN, text, re.IGNORECASE)
        return match.group() if match else None
    
    @staticmethod
    def extract_dates(text: str) -> Dict[str, Optional[str]]:
        """Extract dates from text"""
        dates = {}
        
        # Look for date patterns
        date_matches = re.findall(EntityExtractor.DATE_PATTERN, text)
        
        # Look for relative dates (Oct 15, November 7, etc.)
        month_patterns = {
            r'jan(?:uary)?\s+(\d{1,2})': 1,
            r'feb(?:ruary)?\s+(\d{1,2})': 2,
            r'mar(?:ch)?\s+(\d{1,2})': 3,
            r'apr(?:il)?\s+(\d{1,2})': 4,
            r'may\s+(\d{1,2})': 5,
            r'jun(?:e)?\s+(\d{1,2})': 6,
            r'jul(?:y)?\s+(\d{1,2})': 7,
            r'aug(?:ust)?\s+(\d{1,2})': 8,
            r'sep(?:tember)?\s+(\d{1,2})': 9,
            r'oct(?:ober)?\s+(\d{1,2})': 10,
            r'nov(?:ember)?\s+(\d{1,2})': 11,
            r'dec(?:ember)?\s+(\d{1,2})': 12,
        }
        
        current_year = datetime.now().year
        
        for pattern, month in month_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                day = int(match.group(1))
                date_str = f"{current_year}-{month:02d}-{day:02d}"
                if "start" in text.lower()[:match.start()] or "from" in text.lower()[:match.start()]:
                    dates["start_date"] = date_str
                elif "end" in text.lower()[:match.start()] or "to" in text.lower()[:match.start()]:
                    dates["end_date"] = date_str
                else:
                    if "start_date" not in dates:
                        dates["start_date"] = date_str
                    else:
                        dates["end_date"] = date_str
        
        # Add explicit date matches
        if date_matches:
            if len(date_matches) >= 1:
                dates["start_date"] = date_matches[0]
            if len(date_matches) >= 2:
                dates["end_date"] = date_matches[1]
        
        return dates
    
    @staticmethod
    def extract_status(text: str) -> Optional[str]:
        """Extract status from text"""
        statuses = ["draft", "submitted", "approved", "rejected", "sent", "paid", "cancelled"]
        text_lower = text.lower()
        
        for status in statuses:
            if status in text_lower:
                return status
        return None
    
    @staticmethod
    def extract_numbers(text: str) -> Dict[str, float]:
        """Extract numeric values (hours, amounts)"""
        numbers = {}
        
        # Look for hours
        hours_patterns = [
            r'(\d+(?:\.\d+)?)\s*hours?',
            r'(\d+(?:\.\d+)?)\s*hrs?',
            r'hours?\s*[:\s]+(\d+(?:\.\d+)?)'
        ]
        for pattern in hours_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                numbers["hours"] = float(match.group(1))
                break
        
        # Look for amounts
        amount_patterns = [
            r'\$(\d+(?:\.\d+)?)',
            r'(\d+(?:\.\d+)?)\s*(?:USD|EUR|GBP|AUD)',
            r'amount[:\s]+(\d+(?:\.\d+)?)'
        ]
        for pattern in amount_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                numbers["amount"] = float(match.group(1))
                break
        
        return numbers
    
    @staticmethod
    def extract_currency(text: str) -> Optional[str]:
        """Extract currency code from text"""
        currencies = ["USD", "EUR", "GBP", "AUD", "CAD", "JPY"]
        text_upper = text.upper()
        
        for currency in currencies:
            if currency in text_upper:
                return currency
        return None
    
    @staticmethod
    def extract_all_entities(parsed_query: Dict[str, Any], original_query: str) -> Dict[str, Any]:
        """Extract all entities from query"""
        entities = parsed_query.get("entities", {}).copy()
        
        # Extract from original query using regex patterns
        if not entities.get("timesheet_id"):
            entities["timesheet_id"] = EntityExtractor.extract_timesheet_id(original_query)
        
        if not entities.get("invoice_number"):
            entities["invoice_number"] = EntityExtractor.extract_invoice_number(original_query)
        
        if not entities.get("expense_id"):
            entities["expense_id"] = EntityExtractor.extract_uuid(original_query)
        
        # Extract dates
        dates = EntityExtractor.extract_dates(original_query)
        entities.update(dates)
        
        # Extract status
        if not entities.get("status"):
            entities["status"] = EntityExtractor.extract_status(original_query)
        
        # Extract numbers
        numbers = EntityExtractor.extract_numbers(original_query)
        entities.update(numbers)
        
        # Extract currency
        if not entities.get("currency"):
            entities["currency"] = EntityExtractor.extract_currency(original_query)
        
        # Clean up None values
        entities = {k: v for k, v in entities.items() if v is not None}
        
        return entities

