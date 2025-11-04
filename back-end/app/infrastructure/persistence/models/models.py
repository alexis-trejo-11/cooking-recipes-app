from sqlalchemy import Column, Integer, String, Boolean, DateTime, Table, Text
from sqlalchemy.orm import declarative_base
from sqlalchemy.sql import func
from datetime import datetime


Base = declarative_base()


userRoles = Table(
    "user_roles",
    Base.metadata,
    Column("user_id", Integer, primary_key=True),
    Column("role", String, primary_key=True),
)


class UserModel(Base):
    """SQLAlchemy model for User entity"""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    password = Column(String(255), nullable=False)
    phone_number = Column(String(20), nullable=True)
    is_active = Column(Boolean, default=True)
    joined_at = Column(DateTime(timezone=True), server_default=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)

    roles = Column(
        Text, nullable=False, default="common_user"
    )  # JSON serialized list of roles

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}"
