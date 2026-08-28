import hashlib
import secrets
from typing import Counter

from sqlmodel import func, or_, select
from model import Attraction, User

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
    session.add(user)
    session.commit()
    session.refresh(user)
    return user


def hash_password(password, salt=None):
    if salt is None:
        salt = secrets.token_hex(8)
    hashed_pwd = hashlib.sha256(f"{password}|{salt}".encode()).hexdigest()
    return f"{salt}${hashed_pwd}"


def verify_password(password, stored_pwd):
    salt, hashed_pwd = stored_pwd.split("$")
    return hash_password(password, salt) == stored_pwd