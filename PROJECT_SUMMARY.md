# AI Database Bot - Project Summary

## Overview

This project implements an intelligent bot using LangChain and OpenAI that allows users to interact with a MongoDB database using natural language queries. The bot understands user intent and executes appropriate database operations for timesheets, invoices, expenses, projects, and related entities.

## Architecture

The bot uses a **LangChain chain-based architecture** (similar to SQLDatabaseChain) adapted for MongoDB operations:

1. **Query Parser** - Uses LangChain + OpenAI to parse natural language queries
2. **Intent Classifier** - Classifies query type (CREATE, READ, UPDATE, DELETE, QUERY)
3. **Entity Extractor** - Extracts IDs, dates, amounts, status, etc. from queries
4. **Operation Handlers** - Execute MongoDB operations using pymongo
5. **Response Formatter** - Formats results into human-readable responses
6. **Bot Orchestrator** - Main coordinator that uses LangChain chains to process queries

## Key Components

### Core Bot Logic (`src/bot/`)
- `query_parser.py` - LangChain-based query parsing
- `intent_classifier.py` - Intent classification
- `entity_extractor.py` - Entity extraction using regex and patterns
- `response_formatter.py` - Response formatting
- `bot_orchestrator.py` - Main orchestrator (similar to SQLDatabaseChain pattern)

### Database Handlers (`src/handlers/`)
- `timesheet_handler.py` - Timesheet CRUD operations
- `invoice_handler.py` - Invoice creation and management
- `expense_handler.py` - Expense queries
- `project_handler.py` - Project and talent queries

### Database Connection (`src/database/`)
- `connection.py` - MongoDB connection management
- `models.py` - Database models and schema definitions

### API Layer (`src/api/`)
- `main.py` - FastAPI application
- `routes.py` - API endpoints

### Configuration (`config/`)
- `prompts.py` - LangChain prompts for query parsing

## Supported Operations

### CREATE
- Create timesheets for projects and talents
- Generate invoices from timesheets
- Create invoices from expenses

### READ
- Query timesheets by project, talent, date range, status
- Query invoices by status, project, talent
- Query expenses by project, talent, status
- Get project and talent information

### UPDATE
- Update timesheet date ranges
- Update timesheet status
- Update invoice status

## Example Queries

- "Show me all timesheets for project X"
- "Create a timesheet for project X and talent Y from Oct 1 to Oct 31"
- "Generate an invoice for timesheet TS-202510-148"
- "Update timesheet TS-202510-148 to range from Oct 15 to Nov 7"
- "Find invoices for talent Y in draft status"

## Technology Stack

- **Python 3.9+**
- **LangChain** - LLM orchestration (chain-based pattern)
- **OpenAI API** - GPT-4/GPT-3.5-turbo for natural language understanding
- **pymongo** - MongoDB driver
- **FastAPI** - REST API framework
- **Pydantic** - Data validation

## Project Structure

```
gigs-bot/
├── src/
│   ├── bot/              # Core bot logic (LangChain chains)
│   ├── handlers/         # Database operation handlers
│   ├── database/         # MongoDB connection
│   ├── api/              # FastAPI endpoints
│   └── utils/            # Utility functions
├── config/               # Configuration and prompts
├── tests/                # Test files
├── requirements.txt      # Python dependencies
├── README.md             # Main documentation
├── SETUP.md              # Setup guide
├── run.py                # Run script
└── example_usage.py      # Example usage script
```

## Key Features

1. **Natural Language Processing** - Understands queries in plain English
2. **Intent Classification** - Automatically determines operation type
3. **Entity Extraction** - Extracts IDs, dates, amounts, etc. from queries
4. **MongoDB Integration** - Direct database operations using pymongo
5. **RESTful API** - FastAPI-based API for easy integration
6. **Error Handling** - Comprehensive error handling and logging
7. **Response Formatting** - Human-readable formatted responses

## Usage

### Python API
```python
from src.bot.bot_orchestrator import BotOrchestrator

bot = BotOrchestrator()
result = bot.process_query("Show me all timesheets for project X")
```

### REST API
```bash
curl -X POST "http://localhost:8000/api/bot/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{"query": "Show me all timesheets for project X"}'
```

## Next Steps

1. **Install dependencies**: `pip install -r requirements.txt`
2. **Configure environment**: Copy `.env.example` to `.env` and set variables
3. **Run the bot**: `python run.py`
4. **Test the API**: Visit http://localhost:8000/docs

## Notes

- The bot uses LangChain chains similar to SQLDatabaseChain but adapted for MongoDB
- All database operations are executed through handlers for safety and consistency
- The query parser uses GPT-4 by default but can be configured to use GPT-3.5-turbo
- API authentication is optional (set API_KEY in .env to enable)

