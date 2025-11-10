from typing import List, Optional
from datetime import datetime
from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from app.config.sql_session import Base
from app.modules.recipe.infrastructure.persistence.models import RecipeModel


class UserModel(Base):
    """SQLAlchemy model for User entity"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    first_name: Mapped[str] = mapped_column(String(100))
    last_name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    password: Mapped[str] = mapped_column(String(255))
    phone_number: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True)
    joined_at: Mapped[datetime] = mapped_column(server_default=func.now())
    last_login: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    roles: Mapped[str] = mapped_column(
        Text, default="common_user"
    )  # JSON serialized list of roles

    # Relationships
    recipes: Mapped[List["RecipeModel"]] = relationship(back_populates="author")

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email})>"
