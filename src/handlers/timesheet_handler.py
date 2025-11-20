"""
Timesheet operation handler
"""
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from src.database import get_collection, DatabaseModels

logger = logging.getLogger(__name__)


class TimesheetHandler:
    """Handle timesheet database operations"""
    
    def __init__(self):
        self.collection = get_collection(DatabaseModels.TIMESHEETS)
    
    def create_timesheet(
        self,
        project_id: str,
        talent_id: str,
        start_date: str,
        end_date: str,
        hours_per_day: float = 8.0
    ) -> Dict[str, Any]:
        """Create a new timesheet with entries"""
        try:
            # Generate timesheet ID
            now = datetime.now()
            timesheet_id = f"TS-{now.strftime('%Y%m')}-{now.microsecond % 1000}"
            
            # Parse dates
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Generate entries for each day
            entries = []
            current_date = start
            total_hours = 0.0
            
            while current_date <= end:
                entry = {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "hours": hours_per_day,
                    "description": None
                }
                entries.append(entry)
                total_hours += hours_per_day
                current_date += timedelta(days=1)
            
            timesheet = {
                "timesheet_id": timesheet_id,
                "project_id": project_id,
                "user_id": talent_id,
                "start_date": start_date,
                "end_date": end_date,
                "status": "draft",
                "entries": entries,
                "total_hours": total_hours,
                "created_at": datetime.now().isoformat(),
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.collection.insert_one(timesheet)
            timesheet["_id"] = str(result.inserted_id)
            
            logger.info(f"Created timesheet: {timesheet_id}")
            return timesheet
            
        except Exception as e:
            logger.error(f"Error creating timesheet: {e}")
            raise
    
    def get_timesheet(self, timesheet_id: str) -> Optional[Dict[str, Any]]:
        """Get timesheet by ID"""
        try:
            timesheet = self.collection.find_one({"timesheet_id": timesheet_id})
            if timesheet and "_id" in timesheet:
                timesheet["_id"] = str(timesheet["_id"])
            return timesheet
        except Exception as e:
            logger.error(f"Error getting timesheet: {e}")
            raise
    
    def update_timesheet_dates(
        self,
        timesheet_id: str,
        start_date: str,
        end_date: str,
        hours_per_day: float = 8.0
    ) -> Dict[str, Any]:
        """Update timesheet date range and regenerate entries"""
        try:
            timesheet = self.get_timesheet(timesheet_id)
            if not timesheet:
                raise ValueError(f"Timesheet {timesheet_id} not found")
            
            # Parse dates
            start = datetime.strptime(start_date, "%Y-%m-%d")
            end = datetime.strptime(end_date, "%Y-%m-%d")
            
            # Generate new entries
            entries = []
            current_date = start
            total_hours = 0.0
            
            while current_date <= end:
                entry = {
                    "date": current_date.strftime("%Y-%m-%d"),
                    "hours": hours_per_day,
                    "description": None
                }
                entries.append(entry)
                total_hours += hours_per_day
                current_date += timedelta(days=1)
            
            # Update timesheet
            update_data = {
                "start_date": start_date,
                "end_date": end_date,
                "entries": entries,
                "total_hours": total_hours,
                "updated_at": datetime.now().isoformat()
            }
            
            result = self.collection.update_one(
                {"timesheet_id": timesheet_id},
                {"$set": update_data}
            )
            
            if result.modified_count == 0:
                raise ValueError(f"Failed to update timesheet {timesheet_id}")
            
            updated_timesheet = self.get_timesheet(timesheet_id)
            logger.info(f"Updated timesheet: {timesheet_id}")
            return updated_timesheet
            
        except Exception as e:
            logger.error(f"Error updating timesheet: {e}")
            raise
    
    def update_timesheet_status(self, timesheet_id: str, status: str) -> Dict[str, Any]:
        """Update timesheet status"""
        try:
            valid_statuses = ["draft", "submitted", "approved", "rejected"]
            if status not in valid_statuses:
                raise ValueError(f"Invalid status: {status}")
            
            result = self.collection.update_one(
                {"timesheet_id": timesheet_id},
                {
                    "$set": {
                        "status": status,
                        "updated_at": datetime.now().isoformat()
                    }
                }
            )
            
            if result.modified_count == 0:
                raise ValueError(f"Timesheet {timesheet_id} not found")
            
            updated_timesheet = self.get_timesheet(timesheet_id)
            logger.info(f"Updated timesheet status: {timesheet_id} -> {status}")
            return updated_timesheet
            
        except Exception as e:
            logger.error(f"Error updating timesheet status: {e}")
            raise
    
    def list_timesheets(
        self,
        project_id: Optional[str] = None,
        talent_id: Optional[str] = None,
        status: Optional[str] = None,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """List timesheets with filters"""
        try:
            query = {}
            
            if project_id:
                query["project_id"] = project_id
            if talent_id:
                query["user_id"] = talent_id
            if status:
                query["status"] = status
            if start_date:
                query["start_date"] = {"$gte": start_date}
            if end_date:
                if "start_date" in query:
                    query["start_date"]["$lte"] = end_date
                else:
                    query["end_date"] = {"$lte": end_date}
            
            timesheets = list(self.collection.find(query))
            
            # Convert ObjectId to string
            for timesheet in timesheets:
                if "_id" in timesheet:
                    timesheet["_id"] = str(timesheet["_id"])
            
            logger.info(f"Found {len(timesheets)} timesheets")
            return timesheets
            
        except Exception as e:
            logger.error(f"Error listing timesheets: {e}")
            raise
    
    def get_timesheet_hours(self, timesheet_id: str) -> float:
        """Get total hours for a timesheet"""
        timesheet = self.get_timesheet(timesheet_id)
        if not timesheet:
            raise ValueError(f"Timesheet {timesheet_id} not found")
        return timesheet.get("total_hours", 0.0)

