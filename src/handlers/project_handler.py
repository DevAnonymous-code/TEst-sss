"""
Project and talent operation handler
"""
import logging
from typing import Dict, Any, List, Optional
from bson import ObjectId
from src.database import get_collection, DatabaseModels

logger = logging.getLogger(__name__)


class ProjectHandler:
    """Handle project and talent database operations"""
    
    def __init__(self):
        self.projects_collection = get_collection(DatabaseModels.PROJECTS)
        self.talents_collection = get_collection(DatabaseModels.TALENTS)
    
    def get_project(self, project_id: str) -> Optional[Dict[str, Any]]:
        """Get project by ID"""
        try:
            project = self.projects_collection.find_one({"project_id": project_id})
            if project and "_id" in project:
                project["_id"] = str(project["_id"])
            return project
        except Exception as e:
            logger.error(f"Error getting project: {e}")
            raise
    
    def get_talent(self, talent_id: str) -> Optional[Dict[str, Any]]:
        """Get talent by user_id"""
        try:
            talent = self.talents_collection.find_one({"user_id": talent_id})
            if talent and "_id" in talent:
                talent["_id"] = str(talent["_id"])
            return talent
        except Exception as e:
            logger.error(f"Error getting talent: {e}")
            raise
    
    def list_projects(self, talent_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List projects, optionally filtered by talent"""
        try:
            query = {}
            if talent_id:
                query["talent_id"] = talent_id
            
            projects = list(self.projects_collection.find(query))
            
            # Convert ObjectId to string
            for project in projects:
                if "_id" in project:
                    project["_id"] = str(project["_id"])
            
            logger.info(f"Found {len(projects)} projects")
            return projects
            
        except Exception as e:
            logger.error(f"Error listing projects: {e}")
            raise
    
    def get_project_talents(self, project_id: str) -> List[Dict[str, Any]]:
        """Get all talents associated with a project"""
        try:
            project = self.get_project(project_id)
            if not project:
                return []
            
            talent_ids = []
            if project.get("talent_id"):
                talent_ids.append(project.get("talent_id"))
            
            # Could also query other collections for additional talent relationships
            
            talents = []
            for talent_id in talent_ids:
                talent = self.get_talent(talent_id)
                if talent:
                    talents.append(talent)
            
            return talents
            
        except Exception as e:
            logger.error(f"Error getting project talents: {e}")
            raise

