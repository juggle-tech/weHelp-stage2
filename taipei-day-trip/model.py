from datetime import datetime, date
from typing import List, Optional
 
from sqlalchemy import Column, ForeignKey, Text, Integer
from sqlalchemy.dialects.mysql import INTEGER as MySQLInteger, JSON
from sqlmodel import DateTime, SQLModel, Field, text


class Attraction(SQLModel, table=True):
    __tablename__ = "attraction"

    id: int | None = Field(
        default=None,
        sa_column=Column(MySQLInteger(unsigned=True), primary_key=True, autoincrement=True)
    )
    attr_id: int = Field(nullable=False, unique=True)
    name: str = Field(max_length=255, nullable=False)
    category: str = Field(max_length=255, nullable=False)
    mrt: Optional[str] = Field(default=None, max_length=255)
    address: str = Field(max_length=255, nullable=False)
    description: str = Field(sa_column=Column(Text, nullable=False))
    transport: str = Field(sa_column=Column(Text, nullable=False))
    lat: float
    lng: float
    images: List[str] = Field(sa_column=Column(JSON))


class DataVersion(SQLModel, table=True):
    __tablename__ = "data_version"

    id: int | None = Field(
        default=None,
        sa_column=Column(MySQLInteger(unsigned=True), primary_key=True, autoincrement=True)
    )
    filename: str = Field(max_length=255, nullable=False, unique=True)
    filehash: str = Field(max_length=64, nullable=False)


class User(SQLModel, table=True):
    __tablename__ = "user"

    id: int | None = Field(
        default=None,
        sa_column=Column(MySQLInteger(unsigned=True), primary_key=True, autoincrement=True)
    )
    name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False, unique=True)
    password: str = Field(max_length=255, nullable=False)
    create_time: datetime = Field(
        default=None,
        sa_column=Column(DateTime, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    )


class Booking(SQLModel, table=True):
    __tablename__ = "booking"

    id: int | None = Field(
        default=None,
        sa_column=Column(MySQLInteger(unsigned=True), primary_key=True, autoincrement=True)
    )
    user_id: int = Field(
        sa_column=Column(MySQLInteger(unsigned=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False, unique=True)
    )
    attr_id: int = Field(
        sa_column=Column(
            Integer,
            ForeignKey("attraction.attr_id", ondelete="CASCADE"),
            nullable=False
        )
    )
    booking_date: date = Field(nullable=False)
    time: str = Field(max_length=20, nullable=False)
    price: int = Field(nullable=False)


# class BookingInfo(SQLModel, table=True):
#     __tablename__ = "booking_info"

#     id: int | None = Field(
#         default=None,
#         sa_column=Column(MySQLInteger(unsigned=True), primary_key=True, autoincrement=True)
#     )
#     booking_id: int = Field(
#         sa_column=Column(MySQLInteger(unsigned=True), ForeignKey("booking.id", ondelete="CASCADE"), nullable=False)
#     )
#     contact_name: str = Field(max_length=255, nullable=False)
#     contact_email: str = Field(max_length=255, nullable=False)
#     contact_number: str = Field(max_length=20, nullable=False)

