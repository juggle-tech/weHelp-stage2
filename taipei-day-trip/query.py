import json

from sqlmodel import func, or_, select
from model import Attraction

PAGE_SIZE = 8


def get_filtered_attractions(session, page, category, keyword):
    
    stat = select(Attraction)

    if category:
        stat = stat.where(Attraction.category == category)

    if keyword:
        stat = stat.where(
            or_(
                Attraction.name.contains(keyword), 
                func.json_contains(Attraction.mrt, json.dumps(keyword))
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

    stat = select(Attraction.mrt).where(Attraction.mrt.is_not(None))
    results = session.exec(stat).all()

    # Count the num of attractions near each MRT station
    
    # List them in order from most attractions to least

    return 
