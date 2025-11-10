"""Array Operations Implementation"""
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session
from typing import Any, List, Dict, Optional


class ArrayOperationsManager:
    """Manage array operations operations"""

    def __init__(self, session: Session):
        self.session = session

    def execute(self, query: str, params: Optional[Dict] = None) -> Any:
        """Execute array operations operation"""
        try:
            result = self.session.execute(text(query), params or {})
            self.session.commit()
            return result
        except Exception as e:
            self.session.rollback()
            raise Exception(f"{name} operation failed: {str(e)}")

    def get_results(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Get array operations results"""
        try:
            result = self.session.execute(text(query), params or {})
            return [dict(row) for row in result]
        except Exception as e:
            raise Exception(f"Failed to get results: {str(e)}")
