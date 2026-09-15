import hashlib
import secrets
import time
from typing import Counter

from sqlmodel import or_, select
from model import Attraction, User, Booking, BookingOrder, MCPToken

PAGE_SIZE = 8


def get_filtered_attractions(session, page, category, keyword):
    stat = select(Attraction)

    if category:
        stat = stat.where(Attraction.category == category)

    if keyword:
        stat = stat.where(
            or_(
                Attraction.name.contains(keyword),
                Attraction.mrt == keyword
            )
        )

    # Only retrieve needed data
    stat = stat.offset(page * PAGE_SIZE).limit(PAGE_SIZE + 1)
    results = session.exec(stat).all()

    # Check for a next page
    if len(results) > PAGE_SIZE:
        next_page = page + 1
    else:
        next_page = None

    
    return results[:PAGE_SIZE], next_page


def get_all_categories(session):
    stat = select(Attraction.category).distinct()
    return session.exec(stat).all()


def get_attraction_by_id(session, id):
    stat = select(Attraction).where(Attraction.attr_id == id)
    return session.exec(stat).first()


def get_ordered_mrts(session):
    # Filter null and empty string
    stat = select(Attraction.mrt).where(Attraction.mrt.is_not(None), Attraction.mrt != "")
    results = session.exec(stat).all()
    
    # Count the num of attractions near each MRT station
    mrts = Counter(results)

    # Sort MRT stations by the num of attractions
    sorted_mrts = [station for station, count in mrts.most_common()]

    return sorted_mrts


def get_user_by_email(session, email):
    stat = select(User).where(User.email == email)
    return session.exec(stat).first()


def create_user(session, name, email, password):
    hashed_pwd = hash_password(password)
    user = User(name=name, email=email, password=hashed_pwd)

    try:
        session.add(user)
        session.commit()
        session.refresh(user)
        return user
    except Exception as e:
        print(e)
        session.rollback()
        return None


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(8)
    hashed_pwd = hashlib.sha256(f"{password}|{salt}".encode()).hexdigest()
    return f"{salt}${hashed_pwd}"


def verify_password(password, stored_pwd):
    salt, hashed_pwd = stored_pwd.split("$")
    return hash_password(password, salt) == stored_pwd


def get_all_booking_data(session, user_id):
    stat = (
        select(Booking, Attraction)
        .join(Attraction, Booking.attr_id == Attraction.attr_id)
        .where(Booking.user_id == user_id)
    )
    return session.exec(stat).one_or_none()


def get_booking_by_userid(session, user_id):
    stat = select(Booking).where(Booking.user_id == user_id)
    return session.exec(stat).one_or_none()


def add_booking_to_cart(session, user_id, attr_id, booking_date, time, price):
    booking = get_booking_by_userid(session, user_id)

    try:
        if booking is not None:
            booking.attr_id = attr_id
            booking.booking_date = booking_date
            booking.time = time
            booking.price = price
        else:
            booking= Booking(user_id=user_id , attr_id=attr_id, booking_date=booking_date, time=time, price=price)
            session.add(booking)

        session.commit()
        session.refresh(booking)
        return booking
    except Exception as e:
        print(e)
        session.rollback()
        return None


def delete_booking(session, user_id):
    booking = get_booking_by_userid(session, user_id)

    if booking is None:
        return None

    try:
        session.delete(booking)
        session.commit()
        return booking
    except Exception as e:
        print(e)
        session.rollback()
        return None


def create_order(session, user_id, prime, name, email, phone, order_number, booking, attraction):
    try:
        order = BookingOrder(order_number=order_number, user_id=user_id, booking_id=booking.id, 
                             attr_id=attraction.attr_id, attr_name=attraction.name, attr_address=attraction.address,
                             attr_image=attraction.images[0], booking_date=booking.booking_date, time=booking.time,
                             price=booking.price, name=name, email=email, phone=phone, prime=prime)
        session.add(order)
        session.commit()
        session.refresh(order)
        return order
    except Exception as e:
        print(e)
        session.rollback()
        return None


def check_duplicate_order(session, user_id, attr_id, booking_date, booking_time):
    try:
        stat = select(BookingOrder).where(
                BookingOrder.user_id == user_id,
                BookingOrder.attr_id == attr_id,
                BookingOrder.booking_date == booking_date, 
                BookingOrder.time == booking_time)
        return session.exec(stat).first() is not None
    except Exception as e:
        print(e)
        session.rollback()
        return None


def update_order_status(session, order_id, tappay_result):
    if tappay_result is None:
        return None
    
    try:
        order = session.get(BookingOrder, order_id)

        if order is None:
            return None
        
        order.status = tappay_result.get("status")
        order.rec_trade_id = tappay_result.get("rec_trade_id") or ""

        session.commit()
        session.refresh(order)
        return order
    except Exception as e:
        print(e)
        session.rollback()
        return None


def get_order_by_number(session, order_number):
    try:
        stat = select(BookingOrder).where(BookingOrder.order_number == order_number)
        return session.exec(stat).one_or_none()
    except Exception as e:
        print(e)
        return None


def get_order_by_user(session, user_id):
    try:
        stat = select(BookingOrder).where(BookingOrder.user_id == user_id)
        return session.exec(stat).all()
    except Exception as e:
        print(e)
        return None


def get_token(session, user_id):
    stat = select(MCPToken).where(MCPToken.user_id == user_id)
    return session.exec(stat).one_or_none()


def update_token(session, user_data):

    user_id = int(user_data.get("id"))
    user_name = user_data.get("name")
    user_email = user_data.get("email")

    salt = secrets.token_hex(8)
    new_token = hashlib.sha256(f"{user_name}|{user_email}|{salt}|{time.time()}".encode()).hexdigest()

    try:
        stat = select(MCPToken).where(MCPToken.user_id == user_id)
        token= session.exec(stat).one_or_none()

        if token is None:
            # Create a new token
            token = MCPToken(user_id=user_id, token=new_token)
            session.add(token)
        else:
            # Update token
            token.token = new_token

        session.commit()
        session.refresh(token)
        return token
    except Exception as e:
        print(e)
        session.rollback()
        return None