import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.future import select
from models import Base, Hotel, Room, Client, Booking, Service, BookingStatus
from datetime import datetime

ASYNC_DATABASE_URL = "sqlite+aiosqlite:///./hotel_booking_async.db"

async_engine = create_async_engine(ASYNC_DATABASE_URL, echo=True)

AsyncSessionLocal = sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False
)


async def init_async_db():
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Асинхронна БД створена!")


async def get_available_rooms():
    async with AsyncSessionLocal() as session:
        result = await session.execute(
            select(Room).where(Room.is_available == True)
        )
        rooms = result.scalars().all()
        for room in rooms:
            print(f"Кімната {room.room_number} | {room.room_type} | {room.price_per_night} грн/ніч")
        return rooms


async def create_booking(client_id, room_id, check_in, check_out):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Room).where(Room.id == room_id))
        room = result.scalar_one_or_none()
        if not room:
            print("❌ Кімнату не знайдено!")
            return None
        if not room.is_available:
            print("❌ Кімната вже зайнята!")
            return None

        days = (check_out - check_in).days
        total_price = days * room.price_per_night

        booking = Booking(
            client_id=client_id,
            room_id=room_id,
            check_in=check_in,
            check_out=check_out,
            total_price=total_price,
            status=BookingStatus.confirmed,
        )
        room.is_available = False
        session.add(booking)
        await session.commit()
        print(f"✅ Бронювання створено! Сума: {total_price} грн")
        return booking


async def cancel_booking(booking_id):
    async with AsyncSessionLocal() as session:
        result = await session.execute(select(Booking).where(Booking.id == booking_id))
        booking = result.scalar_one_or_none()
        if not booking:
            print("❌ Бронювання не знайдено!")
            return
        booking.status = BookingStatus.cancelled
        result2 = await session.execute(select(Room).where(Room.id == booking.room_id))
        room = result2.scalar_one_or_none()
        if room:
            room.is_available = True
        await session.commit()
        print(f"✅ Бронювання #{booking_id} скасовано!")


async def main():
    await init_async_db()

    async with AsyncSessionLocal() as session:
        hotel = Hotel(name="Async Hotel", city="Одеса", address="вул. Дерибасівська, 1", stars=4)
        session.add(hotel)
        await session.flush()
        room = Room(hotel_id=hotel.id, room_number="101", room_type="double", price_per_night=1800.0, capacity=2)
        client = Client(first_name="Анна", last_name="Мельник", email="anna@gmail.com")
        session.add_all([room, client])
        await session.commit()
        room_id = room.id
        client_id = client.id

    print("\n📋 Вільні кімнати:")
    await get_available_rooms()

    print("\n📝 Створюємо бронювання:")
    await create_booking(
        client_id=client_id,
        room_id=room_id,
        check_in=datetime(2026, 6, 10),
        check_out=datetime(2026, 6, 15),
    )

    print("\n❌ Скасовуємо бронювання:")
    await cancel_booking(1)


if __name__ == "__main__":
    asyncio.run(main())