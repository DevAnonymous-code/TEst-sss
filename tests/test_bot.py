"""
Basic tests for bot functionality
"""
import pytest
from src.bot.query_parser import QueryParser
from src.bot.intent_classifier import Intent, IntentClassifier
from src.bot.entity_extractor import EntityExtractor


def test_intent_classifier():
    """Test intent classification"""
    classifier = IntentClassifier()
    
    parsed_query = {"intent": "CREATE", "entity_type": "TIMESHEET", "entities": {}}
    intent = classifier.classify(parsed_query)
    assert intent == Intent.CREATE


def test_entity_extractor():
    """Test entity extraction"""
    extractor = EntityExtractor()
    
    # Test timesheet ID extraction
    text = "Show me timesheet TS-202510-148"
    timesheet_id = extractor.extract_timesheet_id(text)
    assert timesheet_id == "TS-202510-148"
    
    # Test invoice number extraction
    text = "Invoice INV-202511-186"
    invoice_number = extractor.extract_invoice_number(text)
    assert invoice_number == "INV-202511-186"
    
    # Test UUID extraction
    text = "Expense ID 6479b09b-07f3-433c-aaae-ddc9b9b8f21d"
    uuid = extractor.extract_uuid(text)
    assert uuid == "6479b09b-07f3-433c-aaae-ddc9b9b8f21d"


def test_date_extraction():
    """Test date extraction"""
    extractor = EntityExtractor()
    
    text = "Create timesheet from Oct 15 to Nov 7"
    dates = extractor.extract_dates(text)
    assert "start_date" in dates
    assert "end_date" in dates


def test_status_extraction():
    """Test status extraction"""
    extractor = EntityExtractor()
    
    text = "Find invoices in draft status"
    status = extractor.extract_status(text)
    assert status == "draft"

