"""
Query parser using LangChain to parse natural language queries
"""
import json
import logging
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from config.prompts import QUERY_PARSING_PROMPT

logger = logging.getLogger(__name__)


class QueryParser:
    """Parse natural language queries into structured format"""
    
    def __init__(self, model_name: str = "gpt-4", temperature: float = 0):
        """Initialize query parser with LLM"""
        self.llm = ChatOpenAI(
            model=model_name,
            temperature=temperature
        )
        # Use LCEL pattern for LangChain v1.0+
        self.chain = QUERY_PARSING_PROMPT | self.llm
    
    def parse(self, query: str) -> Dict[str, Any]:
        """
        Parse natural language query into structured format
        
        Returns:
            Dict with intent, entity_type, entities, operation, confidence
        """
        try:
            # Use LCEL invoke pattern for LangChain v1.0+
            response = self.chain.invoke({"query": query})
            # Extract content from AIMessage
            if hasattr(response, 'content'):
                response = response.content
            elif isinstance(response, dict) and "content" in response:
                response = response["content"]
            
            # Try to parse JSON from response
            # LLM might return JSON wrapped in markdown or text
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            response = response.strip()
            
            parsed = json.loads(response)
            
            # Validate structure
            if "intent" not in parsed:
                parsed["intent"] = "QUERY"
            if "entity_type" not in parsed:
                parsed["entity_type"] = None
            if "entities" not in parsed:
                parsed["entities"] = {}
            if "operation" not in parsed:
                parsed["operation"] = None
            if "confidence" not in parsed:
                parsed["confidence"] = 0.8
            
            logger.info(f"Parsed query: {parsed}")
            return parsed
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON from LLM response: {e}")
            logger.error(f"Response was: {response}")
            # Return default structure
            return {
                "intent": "QUERY",
                "entity_type": None,
                "entities": {},
                "operation": None,
                "confidence": 0.0,
                "error": "Failed to parse query"
            }
        except Exception as e:
            logger.error(f"Error parsing query: {e}")
            return {
                "intent": "QUERY",
                "entity_type": None,
                "entities": {},
                "operation": None,
                "confidence": 0.0,
                "error": str(e)
            }

