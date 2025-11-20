"""
Example usage of the AI Database Bot
"""
import os
from dotenv import load_dotenv
from src.bot.bot_orchestrator import BotOrchestrator

load_dotenv()

def main():
    """Example usage"""
    # Initialize bot
    bot = BotOrchestrator(model_name=os.getenv("OPENAI_MODEL", "gpt-4"))
    
    # Example queries
    queries = [
        "Show me all timesheets for project abc-123",
        "Create a timesheet for project abc-123 and talent xyz-456 from 2025-10-01 to 2025-10-31",
        "Generate an invoice for timesheet TS-202510-148",
        "Update timesheet TS-202510-148 to range from 2025-10-15 to 2025-11-07",
        "Find invoices for talent xyz-456 in draft status"
    ]
    
    print("AI Database Bot - Example Usage\n" + "="*50 + "\n")
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        try:
            result = bot.process_query(query)
            
            if result["success"]:
                print("Result:")
                print(result["result"])
                print(f"\nMetadata: {result.get('metadata', {})}")
            else:
                print(f"Error: {result.get('error')}")
                print(f"Message: {result.get('message')}")
        except Exception as e:
            print(f"Exception: {e}")
        
        print("\n" + "="*50)

if __name__ == "__main__":
    main()

