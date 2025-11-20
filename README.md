# AI Database Bot

An intelligent bot using LangChain and OpenAI that allows users to interact with MongoDB database using natural language queries.

## Features

- Natural language query processing
- Support for timesheets, invoices, expenses, projects, and talents
- Create, read, update operations
- Intelligent intent classification and entity extraction
- RESTful API interface

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and configure:
```bash
cp .env.example .env
```

3. Update `.env` with your credentials:
- `OPENAI_API_KEY`: Your OpenAI API key
- `MONGODB_URI`: MongoDB connection string
- `DATABASE_NAME`: Database name (default: OzProd)
- `API_KEY`: API key for bot authentication

## Running the Bot

### Option 1: Using the run script
```bash
python run.py
```

### Option 2: Using uvicorn directly
```bash
uvicorn src.api.main:app --reload --port 8000
```

### Option 3: Using Python module
```bash
python -m uvicorn src.api.main:app --reload --port 8000
```

The API will be available at:
- API: http://localhost:8000
- Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## API Usage

### Query Endpoint

```bash
POST /api/bot/query
Content-Type: application/json
X-API-Key: your_api_key_here

{
  "query": "Show me all timesheets for project X",
  "user_id": "optional-user-id"
}
```

## Example Queries

- "Show me all timesheets for project X"
- "Create a timesheet for project X and talent Y from Oct 1 to Oct 31"
- "Generate an invoice for timesheet TS-202510-148"
- "Update timesheet TS-202510-148 to range from Oct 15 to Nov 7"
- "Find invoices for talent Y in draft status"

## Project Structure

```
ai-database-bot/
├── src/
│   ├── bot/              # Core bot logic
│   ├── handlers/         # Database operation handlers
│   ├── database/         # Database connection
│   └── api/              # FastAPI endpoints
├── config/               # Configuration and prompts
├── tests/                # Test files
└── requirements.txt
```

## Testing

Run tests:
```bash
pytest tests/
```

## Example Usage

### Using the Python API directly:
```python
from src.bot.bot_orchestrator import BotOrchestrator

bot = BotOrchestrator()
result = bot.process_query("Show me all timesheets for project X")
print(result["result"])
```

### Using the REST API:
```bash
curl -X POST "http://localhost:8000/api/bot/query" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "query": "Show me all timesheets for project X"
  }'
```

### Run example script:
```bash
python example_usage.py
```

## License

MIT

