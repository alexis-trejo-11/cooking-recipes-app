from abc import ABC, abstractmethod
from typing import TypeVar, Generic, List, Any
from dataclasses import dataclass

T = TypeVar("T")


class Specification(ABC):
    """Base specification interface for domain-level filtering."""

    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        """Check if candidate satisfies the specification at domain level."""
        pass

    def __and__(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification":
        return NotSpecification(self)


class SQLCriteria(ABC):
    """Interface for specifications that can be converted to SQL."""

    @abstractmethod
    def to_sql_condition(self) -> Any:
        """Convert specification to SQLAlchemy condition."""
        pass

    @abstractmethod
    def get_joins(self) -> List[Any]:
        """Get necessary joins for the query."""
        pass


class SQLSpecification(Specification, SQLCriteria):
    """Combined interface for specifications that work both in domain and SQL."""

    pass


# Composite specifications for domain level
@dataclass
class AndSpecification(Specification):
    first: Specification
    second: Specification

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.first.is_satisfied_by(candidate) and self.second.is_satisfied_by(
            candidate
        )


@dataclass
class OrSpecification(Specification):
    first: Specification
    second: Specification

    def is_satisfied_by(self, candidate: T) -> bool:
        return self.first.is_satisfied_by(candidate) or self.second.is_satisfied_by(
            candidate
        )


@dataclass
class NotSpecification(Specification):
    spec: Specification

    def is_satisfied_by(self, candidate: T) -> bool:
        return not self.spec.is_satisfied_by(candidate)
