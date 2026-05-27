from sqlalchemy.orm import sessionmaker
from models import engine, Hotel, Room, Client, Booking, Service, BookingStatus
from datetime import datetime

Session = sessionmaker(bind=engine)


def get_available_rooms(city=None):
    session = Session()
    query = session.query(Room).filter(Room.is_available == True)
    if city:
        query = query.join(Hotel).filter(Hotel.city == city)
    rooms = query.all()
    for room in rooms:
        print(f"Кімната {room.room_number} | {room.room_type} | {room.price_per_night} грн/ніч | Готель: {room.hotel.name}")
    session.close()
    return rooms


def create_booking(client_id, room_id, check_in, check_out, service_ids=[]):
    session = Session()
    room = session.query(Room).filter(Room.id == room_id).first()
    if not room:
        print("❌ Кімнату не знайдено!")
        session.close()
        return None
    if not room.is_available:
        print("❌ Кімната вже зайнята!")
        session.close()
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

    if service_ids:
        services = session.query(Service).filter(Service.id.in_(service_ids)).all()
        booking.services = services
        total_price += sum(s.price for s in services)
        booking.total_price = total_price

    room.is_available = False
    session.add(booking)
    session.commit()
    print(f"✅ Бронювання створено! ID: {booking.id} | Сума: {booking.total_price} грн")
    session.close()
    return booking


def cancel_booking(booking_id):
    session = Session()
    booking = session.query(Booking).filter(Booking.id == booking_id).first()
    if not booking:
        print("❌ Бронювання не знайдено!")
        session.close()
        return
    booking.status = BookingStatus.cancelled
    booking.room.is_available = True
    session.commit()
    print(f"✅ Бронювання #{booking_id} скасовано, кімната знову вільна!")
    session.close()


def get_client_bookings(client_id):
    session = Session()
    bookings = session.query(Booking).filter(Booking.client_id == client_id).all()
    for b in bookings:
        print(f"Бронювання #{b.id} | Кімната {b.room.room_number} | {b.check_in.date()} → {b.check_out.date()} | {b.status.value}")
    session.close()
    return bookings


def create_client(first_name, last_name, email, phone=None):
    session = Session()
    client = Client(first_name=first_name, last_name=last_name, email=email, phone=phone)
    session.add(client)
    session.commit()
    print(f"✅ Клієнт створений! ID: {client.id}")
    session.close()
    return client


if __name__ == "__main__":
    session = Session()
    hotel = Hotel(name="Grand Palace", city="Київ", address="вул. Хрещатик, 1", stars=5)
    session.add(hotel)
    session.flush()
    room1 = Room(hotel_id=hotel.id, room_number="101", room_type="single", price_per_night=1200.0, capacity=1)
    room2 = Room(hotel_id=hotel.id, room_number="202", room_type="double", price_per_night=2000.0, capacity=2)
    session.add_all([room1, room2])
    service = Service(name="Сніданок", price=150.0)
    session.add(service)
    session.commit()
    room1_id = room1.id
    service_id = service.id
    session.close()

    client = create_client("Олег", "Петренко", "oleg@gmail.com", "+380991234567")

    print("\n📋 Вільні кімнати:")
    get_available_rooms()

    print("\n📝 Створюємо бронювання:")
    create_booking(
        client_id=client.id,
        room_id=room1_id,
        check_in=datetime(2026, 6, 1),
        check_out=datetime(2026, 6, 5),
        service_ids=[service_id]
    )

    print("\n📋 Бронювання клієнта:")
    get_client_bookings(client.id)

    print("\n❌ Скасовуємо бронювання:")
    cancel_booking(1)