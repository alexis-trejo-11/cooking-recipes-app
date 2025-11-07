from abc import ABC, abstractmethod
from typing import List, Any


class Criteria(ABC):
    """Interface for specifications that can be converted to SQL."""

    @abstractmethod
    def to_sql_condition(self) -> Any:
        """Convert specification to SQLAlchemy condition."""
        pass

    @abstractmethod
    def get_joins(self) -> List[Any]:
        """Get necessary joins for the query."""
        pass


class Specification(Criteria):
    """Combined interface for specifications that work in SQL."""

    pass
