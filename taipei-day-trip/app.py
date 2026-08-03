import query

from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session
from database import SessionDep, engine, create_database_if_not_exists
from load_data import load_attractions_if_updated
from contextlib import asynccontextmanager



@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create database and tables on startup if not exists
    create_database_if_not_exists()
    SQLModel.metadata.create_all(engine)

    # Update attraction data if outdated
    with Session(engine) as session:
        load_attractions_if_updated(session)

    yield


app = FastAPI(lifespan=lifespan)


# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
    return FileResponse("./static/index.html", media_type="text/html")


@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
    return FileResponse("./static/attraction.html", media_type="text/html")


@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
    return FileResponse("./static/booking.html", media_type="text/html")


@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
    return FileResponse("./static/thankyou.html", media_type="text/html")



## API
# Attraction
@app.get("/api/attractions")
async def get_attractions(request: Request, session: SessionDep, page: int = 0, 
                        category: str | None = None, keyword: str | None = None):

    # Check if the input page is valid
    if page < 0:
        return {"error": True, "message": "Page must be a positive integer"}

    # Check if the input category is valid
    if category:
        categories_list = query.get_all_categories(session)
        if category not in categories_list:
            return {"error": True, "message": "Category does not exist"}

    # Retrieve filtered data 
    data, next_page = query.get_filtered_attractions(session, page, category, keyword)

    return {"nextPage": next_page, "data": data}


@app.get("/api/attraction/{attractionId}")
async def get_an_attraction(request: Request, session: SessionDep, attractionId: int):
    return 


# Attraction Category
@app.get("/api/categories")
async def get_category(request: Request, session: SessionDep):
    return 


# MRT Station
@app.get("/api/mrts")
async def get_mrts(request: Request, session: SessionDep):
    return 


app.mount("/static", StaticFiles(directory = "static"), name = "static")