from sqlalchemy.orm import sessionmaker
from sqlalchemy import text
from models import engine, Hotel, Room, Client, Booking, Service, BookingStatus
from datetime import datetime

Session = sessionmaker(bind=engine)


def get_room_by_id(room_id: int):
    session = Session()
    room = session.query(Room).filter(Room.id == room_id).first()
    if room:
        print(f"✅ Кімната: {room.room_number} | {room.room_type} | {room.price_per_night} грн")
    else:
        print("❌ Кімнату не знайдено!")
    session.close()
    return room


def search_hotels_by_city(city: str):
    session = Session()
    hotels = session.query(Hotel).filter(Hotel.city == city).all()
    for hotel in hotels:
        print(f"🏨 {hotel.name} | {hotel.city} | {hotel.stars} ⭐")
    session.close()
    return hotels


def get_bookings_by_status(status: str):
    session = Session()
    try:
        booking_status = BookingStatus(status)
    except ValueError:
        print(f"❌ Невірний статус: {status}")
        session.close()
        return []
    bookings = session.query(Booking).filter(Booking.status == booking_status).all()
    for b in bookings:
        print(f"Бронювання #{b.id} | Статус: {b.status.value} | Сума: {b.total_price} грн")
    session.close()
    return bookings


def safe_raw_query(city: str):
    session = Session()
    result = session.execute(
        text("SELECT id, name, city, stars FROM hotels WHERE city = :city"),
        {"city": city}
    )
    rows = result.fetchall()
    for row in rows:
        print(f"🏨 ID:{row.id} | {row.name} | {row.city} | {row.stars}⭐")
    session.close()
    return rows


def demonstrate_sql_injection_protection():
    print("\n🔐 Демонстрація захисту від SQL-ін'єкцій:")
    print("=" * 50)

    malicious_input = "Київ' OR '1'='1"
    print(f"Шкідливий ввід: {malicious_input}")

    print("\n1. ORM-запит (безпечний):")
    session = Session()
    hotels = session.query(Hotel).filter(Hotel.city == malicious_input).all()
    print(f"   Знайдено готелів: {len(hotels)} (очікується 0 — ін'єкція не спрацювала)")
    session.close()

    print("\n2. Параметризований raw-запит (безпечний):")
    session = Session()
    result = session.execute(
        text("SELECT * FROM hotels WHERE city = :city"),
        {"city": malicious_input}
    )
    rows = result.fetchall()
    print(f"   Знайдено готелів: {len(rows)} (очікується 0 — ін'єкція не спрацювала)")
    session.close()

    print("\n✅ Обидва методи захищені від SQL-ін'єкцій!")


if __name__ == "__main__":
    session = Session()
    hotel = Hotel(name="Secure Hotel", city="Харків", address="пр. Науки, 1", stars=4)
    session.add(hotel)
    session.flush()
    room = Room(hotel_id=hotel.id, room_number="201", room_type="double", price_per_night=1500.0, capacity=2)
    session.add(room)
    session.commit()
    room_id = room.id
    session.close()

    print("\n🔍 Пошук кімнати за ID:")
    get_room_by_id(room_id)

    print("\n🔍 Пошук готелів у Харкові:")
    search_hotels_by_city("Харків")

    print("\n🔍 Параметризований SQL-запит:")
    safe_raw_query("Харків")

    demonstrate_sql_injection_protection()