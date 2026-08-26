import os
import jwt
import query

from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Session
from database import SessionDep, engine, create_database_if_not_exists
from load_data import load_attractions_if_updated
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel
from jwt import ExpiredSignatureError, InvalidTokenError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")


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
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "Page must be a positive integer"}
        )

    # Check if the input category is valid
    if category:
        categories_list = query.get_all_categories(session)
        if category not in categories_list:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "Category does not exist"}
            )

    # Retrieve filtered data
    try:
        data, next_page = query.get_filtered_attractions(session, page, category, keyword)
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )
    return {"nextPage": next_page, "data": data}


@app.get("/api/attraction/{attractionId}")
async def get_an_attraction(request: Request, session: SessionDep, attractionId: int):
    try:
        data = query.get_attraction_by_id(session, attractionId)
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )

    if data is None:
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "景點編號不正確"}
        )
    return {"data": data}


# Attraction Category
@app.get("/api/categories")
async def get_category(request: Request, session: SessionDep):
    try:
        data = query.get_all_categories(session)
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )

    return {"data": data}


# MRT Station
@app.get("/api/mrts")
async def get_mrts(request: Request, session: SessionDep):
    try:
        data = query.get_ordered_mrts(session)
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )
    
    return {"data": data}


# User
class SigninInput(BaseModel):
    email: str = ""
    password: str = ""

class SignupInput(BaseModel):
    name: str = ""
    email: str = ""
    password: str = ""


@app.post("/api/user")
async def signup(request: Request, session: SessionDep, body: SignupInput):
    try:
        if not query.get_user_by_email(body.email):
            user = query.create_user(session, body.name, body.email, body.password)
            return {"ok": True}
        else:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "註冊失敗，重複的 Email 或其他原因"}
            )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )    


@app.get("/api/user/auth")
async def get_current_user(request: Request, session: SessionDep):
    auth = request.headers.get("Authorization")

    # No token -> null
    if not auth or not auth.startswith("Bearer "):
        return {"data": None}

    token = auth.split(" ")[1]

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except (ExpiredSignatureError, InvalidTokenError) as e:
        print(e)
        return {"data": None}

    # Token is valid
    return {"data": {"id": payload.get("id"), "name": payload.get("name"), "email": payload.get("email")}}


@app.put("/api/user/auth")
async def signin(session: SessionDep, body: SigninInput):
    try:
        user = query.get_user_by_email(session, body.email);
        # Verify that the user has signed in successfully
        if user and query.hashed_password(body.password) == user.password:
            payload = {"id": str(user.id), "email": user.email, "name": user.name, "iat": datetime.now(datetime.timezone.utc), 
                    "exp": datetime.now(timezone.utc) + timedelta(days=7)}
            encoded_jwt = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
            return JSONResponse(
                status_code=200,
                content={"token": encoded_jwt}
            )
        else:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "登入失敗，帳號或密碼錯誤或其他原因"}
            )
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )

    

app.mount("/static", StaticFiles(directory = "static"), name = "static")