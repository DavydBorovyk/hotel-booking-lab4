from sqlalchemy import (
    create_engine, Column, Integer, String, Float,
    Boolean, DateTime, ForeignKey, Table, Text, Enum
)
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
import enum

Base = declarative_base()

booking_services = Table(
    "booking_services",
    Base.metadata,
    Column("booking_id", Integer, ForeignKey("bookings.id"), primary_key=True),
    Column("service_id", Integer, ForeignKey("services.id"), primary_key=True),
)

class BookingStatus(enum.Enum):
    pending   = "pending"
    confirmed = "confirmed"
    cancelled = "cancelled"
    completed = "completed"

class Hotel(Base):
    __tablename__ = "hotels"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(150), nullable=False)
    city        = Column(String(100), nullable=False)
    address     = Column(String(255), nullable=False)
    stars       = Column(Integer, nullable=False)
    description = Column(Text, nullable=True)
    created_at  = Column(DateTime, default=datetime.utcnow)
    rooms = relationship("Room", back_populates="hotel", cascade="all, delete-orphan")

class Room(Base):
    __tablename__ = "rooms"
    id              = Column(Integer, primary_key=True, index=True)
    hotel_id        = Column(Integer, ForeignKey("hotels.id"), nullable=False)
    room_number     = Column(String(10), nullable=False)
    room_type       = Column(String(50), nullable=False)
    price_per_night = Column(Float, nullable=False)
    capacity        = Column(Integer, nullable=False)
    is_available    = Column(Boolean, default=True)
    hotel    = relationship("Hotel", back_populates="rooms")
    bookings = relationship("Booking", back_populates="room")

class Client(Base):
    __tablename__ = "clients"
    id         = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(100), nullable=False)
    last_name  = Column(String(100), nullable=False)
    email      = Column(String(150), unique=True, nullable=False, index=True)
    phone      = Column(String(20), nullable=True)
    passport   = Column(String(50), unique=True, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    bookings = relationship("Booking", back_populates="client")

class Booking(Base):
    __tablename__ = "bookings"
    id          = Column(Integer, primary_key=True, index=True)
    client_id   = Column(Integer, ForeignKey("clients.id"), nullable=False)
    room_id     = Column(Integer, ForeignKey("rooms.id"), nullable=False)
    check_in    = Column(DateTime, nullable=False)
    check_out   = Column(DateTime, nullable=False)
    total_price = Column(Float, nullable=False)
    status      = Column(Enum(BookingStatus), default=BookingStatus.pending)
    created_at  = Column(DateTime, default=datetime.utcnow)
    client   = relationship("Client", back_populates="bookings")
    room     = relationship("Room", back_populates="bookings")
    services = relationship("Service", secondary=booking_services, back_populates="bookings")

class Service(Base):
    __tablename__ = "services"
    id          = Column(Integer, primary_key=True, index=True)
    name        = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    price       = Column(Float, nullable=False)
    bookings = relationship("Booking", secondary=booking_services, back_populates="services")

DATABASE_URL = "sqlite:///./hotel_booking.db"
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    Base.metadata.create_all(bind=engine)
    print("✅ База даних створена успішно!")

if __name__ == "__main__":
    init_db()