from abc import ABC, abstractmethod
from typing import TypeVar
from dataclasses import dataclass

T = TypeVar("T")


class Specification(ABC):
    @abstractmethod
    def is_satisfied_by(self, candidate: T) -> bool:
        pass

    def __and__(self, other: "Specification") -> "AndSpecification":
        return AndSpecification(self, other)

    def __or__(self, other: "Specification") -> "OrSpecification":
        return OrSpecification(self, other)

    def __invert__(self) -> "NotSpecification":
        return NotSpecification(self)


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
