"""
API routes for bot endpoints
"""
import os
import logging
from fastapi import APIRouter, HTTPException, Header, Depends
from pydantic import BaseModel
from typing import Optional
from dotenv import load_dotenv

from src.bot.bot_orchestrator import BotOrchestrator

load_dotenv()

logger = logging.getLogger(__name__)

router = APIRouter()

# Initialize bot orchestrator
_bot_orchestrator: Optional[BotOrchestrator] = None


def get_bot_orchestrator() -> BotOrchestrator:
    """Get or create bot orchestrator instance"""
    global _bot_orchestrator
    
    if _bot_orchestrator is None:
        model_name = os.getenv("OPENAI_MODEL", "gpt-4")
        _bot_orchestrator = BotOrchestrator(model_name=model_name)
    
    return _bot_orchestrator


def verify_api_key(x_api_key: str = Header(None)) -> bool:
    """Verify API key from header"""
    expected_key = os.getenv("API_KEY")
    
    if not expected_key:
        # If no API key is set, allow all requests (development mode)
        logger.warning("No API_KEY set in environment, allowing all requests")
        return True
    
    if not x_api_key:
        raise HTTPException(status_code=401, detail="API key required")
    
    if x_api_key != expected_key:
        raise HTTPException(status_code=403, detail="Invalid API key")
    
    return True


class QueryRequest(BaseModel):
    """Query request model"""
    query: str
    user_id: Optional[str] = None


class QueryResponse(BaseModel):
    """Query response model"""
    success: bool
    result: Optional[str] = None
    error: Optional[str] = None
    message: Optional[str] = None
    metadata: Optional[dict] = None


@router.post("/query", response_model=QueryResponse)
async def process_query(
    request: QueryRequest,
    api_key: bool = Depends(verify_api_key)
):
    """
    Process a natural language query
    
    Example queries:
    - "Show me all timesheets for project X"
    - "Create a timesheet for project X and talent Y from Oct 1 to Oct 31"
    - "Generate an invoice for timesheet TS-202510-148"
    - "Update timesheet TS-202510-148 to range from Oct 15 to Nov 7"
    """
    try:
        bot = get_bot_orchestrator()
        result = bot.process_query(request.query, request.user_id)
        
        if result["success"]:
            return QueryResponse(
                success=True,
                result=result.get("result"),
                metadata=result.get("metadata")
            )
        else:
            return QueryResponse(
                success=False,
                error=result.get("error"),
                message=result.get("message")
            )
            
    except Exception as e:
        logger.error(f"Error processing query: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/status")
async def get_status():
    """Get bot status"""
    return {
        "status": "operational",
        "model": os.getenv("OPENAI_MODEL", "gpt-4"),
        "database": os.getenv("DATABASE_NAME", "OzProd")
    }

