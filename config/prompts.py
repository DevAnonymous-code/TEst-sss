"""
LangChain prompts for query parsing and intent classification
"""
from langchain_core.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate

# System prompt for query parsing
QUERY_PARSING_SYSTEM_PROMPT = """You are an intelligent database assistant that helps users interact with a MongoDB database using natural language.

Your task is to parse user queries and extract:
1. Intent (CREATE, READ, UPDATE, DELETE, QUERY)
2. Entity type (TIMESHEET, INVOICE, EXPENSE, PROJECT, TALENT)
3. Entities (IDs, dates, amounts, status, etc.)

## Database Schema

### Timesheets Collection
- timesheet_id (format: TS-YYYYMM-XXX)
- project_id (UUID)
- user_id (UUID, also called talent_id)
- start_date (YYYY-MM-DD)
- end_date (YYYY-MM-DD)
- status (draft, submitted, approved, rejected)
- entries (array of {{date, hours, description}})
- total_hours (float)

### Invoices Collection
- invoice_number (format: INV-YYYYMM-XXX)
- project_id (UUID)
- talent_id (UUID)
- timesheet_id (UUID or timesheet_id)
- expense_id (UUID)
- status (draft, sent, paid, cancelled)
- items (array of invoice items)
- currency (string)
- issue_date (YYYY-MM-DD)
- due_date (YYYY-MM-DD)

### Expenses Collection
- expense_id (UUID)
- project_id (UUID)
- user_id (UUID)
- currency (string)
- status (draft, submitted, approved, rejected)
- items (array of expense items)
- total_amount (float)

### Projects Collection
- project_id (UUID)
- project_name (string)
- client_id (UUID)
- talent_id (UUID)
- status (string)

### Talents Collection
- user_id (UUID)
- country (string)
- companyLegalName (string)

## Supported Operations

### CREATE Operations
- Create timesheet: "Create timesheet for project X and talent Y from date A to date B"
- Create invoice from timesheet: "Generate invoice for timesheet TS-202510-148"
- Create invoice from expense: "Create invoice for expense ID 6479b09b-07f3-433c-aaae-ddc9b9b8f21d"

### READ Operations
- Query timesheets: "Show me all timesheets for project X"
- Query invoices: "Find invoices for talent Y in draft status"
- Query expenses: "Get expenses for project Z"
- Get specific entity: "Show me timesheet TS-202510-148"

### UPDATE Operations
- Update timesheet dates: "Update timesheet TS-202510-148 to range from Oct 15 to Nov 7"
- Update invoice status: "Change invoice INV-202511-186 status to draft"
- Update timesheet hours: "Update timesheet hours per day to 6"

## Response Format

Return a JSON object with the following structure:
{{
    "intent": "CREATE|READ|UPDATE|DELETE|QUERY",
    "entity_type": "TIMESHEET|INVOICE|EXPENSE|PROJECT|TALENT",
    "entities": {{
        "timesheet_id": "...",
        "invoice_number": "...",
        "expense_id": "...",
        "project_id": "...",
        "talent_id": "...",
        "user_id": "...",
        "start_date": "YYYY-MM-DD",
        "end_date": "YYYY-MM-DD",
        "status": "...",
        "hours": 0.0,
        "amount": 0.0,
        "currency": "..."
    }},
    "operation": "specific_operation_name",
    "confidence": 0.0-1.0
}}

Extract all relevant entities from the query. If a date is mentioned without a year, assume current year or infer from context.
If an ID format is mentioned (like TS-202510-148), extract it exactly as provided.
"""

# Query parsing prompt template
QUERY_PARSING_PROMPT = ChatPromptTemplate.from_messages([
    SystemMessagePromptTemplate.from_template(QUERY_PARSING_SYSTEM_PROMPT),
    HumanMessagePromptTemplate.from_template("Parse this query: {query}")
])

# Intent classification prompt
INTENT_CLASSIFICATION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Classify the intent of the user query into one of these categories:
- CREATE: User wants to create a new record
- READ: User wants to retrieve/view existing records
- UPDATE: User wants to modify existing records
- DELETE: User wants to delete records
- QUERY: User wants to search/filter records

Return only the intent category."""),
    ("human", "Query: {query}")
])

# Entity extraction prompt
ENTITY_EXTRACTION_PROMPT = ChatPromptTemplate.from_messages([
    ("system", """Extract entities from the user query. Look for:
- IDs: timesheet_id (TS-YYYYMM-XXX), invoice_number (INV-YYYYMM-XXX), expense_id (UUID), project_id (UUID), talent_id/user_id (UUID)
- Dates: start_date, end_date (in YYYY-MM-DD format)
- Status: draft, submitted, approved, rejected, sent, paid, cancelled
- Numbers: hours, amounts
- Currency codes

Return a JSON object with extracted entities."""),
    ("human", "Query: {query}")
])

