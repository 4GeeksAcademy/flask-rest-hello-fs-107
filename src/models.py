from typing import Literal, Optional, Union
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship, Session
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(
        String(120), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean(), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        DateTime, default=datetime.utcnow)

    favoritos: Mapped[list["Favorites"]] = relationship(back_populates="user")

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
            "created": self.created_at,
        }


class Planets(db.Model):
    __tablename__ = "planets"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
        }


class People(db.Model):
    __tablename__ = "people"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(nullable=False, unique=True)

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name
        }


class Favorites(db.Model):
    __tablename__ = "favorites"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    typeof: Mapped[Literal["planets", "people"]] = mapped_column(String(40))
    reference_id: Mapped[int] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship(back_populates="favoritos")

    def get_reference(self, session: Union[AsyncSession, Session]) -> Optional[object]:
        if self.typeof == "planets":
            return session.get(Planets, self.reference_id)
        elif self.typeof == "people":
            return session.get(People, self.reference_id)
        return None

    def serialize(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "typeof": self.typeof,
            "reference_id": self.reference_id,
        }
