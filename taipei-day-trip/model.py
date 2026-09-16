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


class BookingOrder(SQLModel, table=True):
    __tablename__ = "booking_order"

    id: int | None = Field(
        default=None,
        sa_column=Column(MySQLInteger(unsigned=True), primary_key=True, autoincrement=True)
    )
    order_number: str = Field(unique=True, max_length=50, nullable=False)
    user_id: int = Field(
        sa_column=Column(MySQLInteger(unsigned=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )
    booking_id: int = Field(
        sa_column=Column(MySQLInteger(unsigned=True), ForeignKey("booking.id", ondelete="SET NULL"))
    )

    # Attraction and Booking data
    attr_id: int = Field(nullable=False)
    attr_name: str = Field(max_length=255, nullable=False)
    attr_address: str = Field(max_length=255, nullable=False)
    attr_image: str = Field(max_length=500, nullable=False)
    booking_date: date = Field(nullable=False)
    time: str = Field(max_length=20, nullable=False)
    price: int = Field(nullable=False)

    # Contact and Payment data
    name: str = Field(max_length=255, nullable=False)
    email: str = Field(max_length=255, nullable=False)
    phone: str = Field(max_length=20, nullable=False)
    prime: str = Field(max_length=255, nullable=False)
    status: int = Field(default=1, nullable=False)
    rec_trade_id: str = Field(max_length=255, default="", nullable=False)


class MCPToken(SQLModel, table=True):
    __tablename__ = "mcp_token"

    id: int | None = Field(
        default=None,
        sa_column=Column(MySQLInteger(unsigned=True), primary_key=True, autoincrement=True)
    )
    user_id: int = Field(
        sa_column=Column(MySQLInteger(unsigned=True), ForeignKey("user.id", ondelete="CASCADE"), nullable=False)
    )
    token: str = Field(max_length=255)
    