# Setup Guide

## Prerequisites

- Python 3.9 or higher
- MongoDB instance (local or remote)
- OpenAI API key

## Installation Steps

### 1. Clone or navigate to the project directory

```bash
cd gigs-bot
```

### 2. Create a virtual environment (recommended)

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment variables

Copy the example environment file:
```bash
cp .env.example .env
```

Edit `.env` and set the following variables:

```env
OPENAI_API_KEY=sk-your-openai-api-key-here
MONGODB_URI=mongodb://localhost:27017
DATABASE_NAME=OzProd
LOG_LEVEL=INFO
API_KEY=your-secure-api-key-here
OPENAI_MODEL=gpt-4
```

**Important Notes:**
- Replace `your-openai-api-key-here` with your actual OpenAI API key
- Update `MONGODB_URI` to point to your MongoDB instance
- Set `DATABASE_NAME` to your database name (default: OzProd)
- Generate a secure `API_KEY` for API authentication
- You can use `gpt-3.5-turbo` instead of `gpt-4` for lower costs

### 5. Verify MongoDB connection

Make sure your MongoDB instance is running and accessible. You can test the connection:

```python
from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()
client = MongoClient(os.getenv("MONGODB_URI"))
client.admin.command('ping')
print("MongoDB connection successful!")
```

### 6. Run the bot

Start the FastAPI server:

```bash
python run.py
```

Or:

```bash
uvicorn src.api.main:app --reload --port 8000
```

### 7. Test the API

Open your browser and navigate to:
- API Documentation: http://localhost:8000/docs
- Health Check: http://localhost:8000/health

Or test with curl:

```bash
curl http://localhost:8000/health
```

## Troubleshooting

### MongoDB Connection Issues

If you encounter MongoDB connection errors:

1. Verify MongoDB is running:
   ```bash
   mongosh  # or mongo
   ```

2. Check the connection string format:
   - Local: `mongodb://localhost:27017`
   - Remote: `mongodb://username:password@host:port/database`
   - Atlas: `mongodb+srv://username:password@cluster.mongodb.net/database`

3. Check firewall and network settings

### OpenAI API Issues

If you encounter OpenAI API errors:

1. Verify your API key is correct
2. Check your OpenAI account has sufficient credits
3. Ensure the model name is correct (gpt-4, gpt-3.5-turbo, etc.)
4. Check rate limits

### Import Errors

If you encounter import errors:

1. Make sure you're in the virtual environment
2. Reinstall dependencies: `pip install -r requirements.txt`
3. Check Python version: `python --version` (should be 3.9+)

## Next Steps

- Read the [README.md](README.md) for usage examples
- Check the API documentation at http://localhost:8000/docs
- Try the example script: `python example_usage.py`

