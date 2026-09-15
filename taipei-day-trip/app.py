import os
import jwt
import query
import tappay

from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from fastapi.staticfiles import StaticFiles
from sqlmodel import Field, SQLModel, Session
from database import SessionDep, engine, create_database_if_not_exists
from load_data import load_attractions_if_updated
from contextlib import asynccontextmanager
from datetime import datetime, timezone, timedelta
from pydantic import BaseModel, Field
from jwt import ExpiredSignatureError, InvalidTokenError
from email_validator import validate_email, EmailNotValidError

load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
TAPPAY_APP_ID = os.getenv("TAPPAY_APP_ID")
TAPPAY_APP_KEY = os.getenv("TAPPAY_APP_KEY")
TAPPAY_PARTNER_KEY = os.getenv("TAPPAY_PARTNER_KEY")
TAPPAY_MERCHANT_ID = os.getenv("TAPPAY_MERCHANT_ID")


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


@app.get("/member", include_in_schema=False)
async def member(request: Request):
    return FileResponse("./static/member.html", media_type="text/html")



## API
# Attraction
@app.get("/api/attractions")
async def get_attractions(session: SessionDep, page: int = 0, 
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
async def get_an_attraction(session: SessionDep, attractionId: int):
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
async def get_category(session: SessionDep):
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
async def get_mrts(session: SessionDep):
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
class SignupInput(BaseModel):
    name: str = Field(..., examples=["Jung"])
    email: str= Field(..., examples=["jung@example.com"])
    password: str = Field(..., examples=["jung"])


@app.post("/api/user")
async def signup(session: SessionDep, body: SignupInput):
    try:
        try:
            validate_email(body.email, check_deliverability=False)
        except EmailNotValidError:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "Email 格式不正確"}
            )
        
        if query.get_user_by_email(session, body.email):
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "註冊失敗，重複的 Email 或其他原因"}
            )
        
        user = query.create_user(session, body.name, body.email, body.password)
        if user is None:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "存取失敗"}
            )

        return {"ok": True}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        ) 


# Helper for decoding token
def _decode_token(request: Request):
    auth = request.headers.get("Authorization")
    
    # No token or in wrong format
    if not auth or not auth.startswith("Bearer "):
        return None

    # Token starts with Bearer but with empty token
    token = auth.removeprefix("Bearer ").strip()
    if not token:
        return None

    try:
        return jwt.decode(token, SECRET_KEY, algorithms="HS256")
    except (ExpiredSignatureError, InvalidTokenError) as e:
        print(e)
        return None


@app.get("/api/user/auth")
async def get_current_user(request: Request):
    payload = _decode_token(request)

    if payload is None:
        return {"data": None}
    return {"data": {"id": payload.get("id"), "name": payload.get("name"), "email": payload.get("email")}}


class SigninInput(BaseModel):
    email: str = Field(..., examples=["jung@example.com"])
    password: str = Field(..., examples=["jung"])

@app.put("/api/user/auth")
async def signin(session: SessionDep, body: SigninInput):
    try:
        user = query.get_user_by_email(session, body.email);

        # Verify that the user has signed in successfully
        if user and query.verify_password(body.password, user.password):
            payload = {"id": str(user.id), "email": user.email, "name": user.name, "iat": datetime.now(timezone.utc), 
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


# Booking
@app.get("/api/booking")
async def getBooking(request: Request, session: SessionDep):
    # Verify authentication
    payload = _decode_token(request)
    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )

    # Retrieve booking info
    try:
        booking = query.get_all_booking_data(session, int(payload.get("id")))
        if booking is None:
            return {"data": None}

        booking_data, attraction_data = booking

        return {"data": 
                    { "attraction": {
                        "id": attraction_data.attr_id, 
                        "name": attraction_data.name, 
                        "address": attraction_data.address, 
                        "image": attraction_data.images[0]
                      },
                      "date": booking_data.booking_date, 
                      "time": booking_data.time,
                      "price": booking_data.price
                    }
                }
        
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        ) 


class AttractionCart(BaseModel):
    attr_id: int = Field(..., examples=["1"])
    booking_date: datetime = Field(..., examples=["2026-09-03"])
    time: str = Field(..., examples=["morning"])
    price: int = Field(..., examples=["2000"])

@app.post("/api/booking")
async def createBooking(request: Request, session: SessionDep, body: AttractionCart):
    # Verify authentication
    payload = _decode_token(request)
    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )

    # Create booking
    try:
        user_id = int(payload.get("id"))
        booking = query.add_booking_to_cart(session, user_id, body.attr_id, body.booking_date, body.time, body.price)
        if booking is None:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "建立失敗，輸入不正確或其他原因"}
            )

        return {"attractionId": booking.attr_id, "date": booking.booking_date, "time": booking.time, "price": booking.price}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        ) 


@app.delete("/api/booking")
async def deleteBooking(request: Request, session: SessionDep):
    # Verify authentication
    payload = _decode_token(request)
    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )

    # Delete booking
    try:
        user_id = int(payload.get("id"))
        result = query.delete_booking(session, user_id)
        if result is None:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "刪除失敗"}
            )
        return {"ok": True}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )


# TapPay
@app.get("/api/tappay/config")
async def get_tappay_config():
    return { "appId": TAPPAY_APP_ID, "appKey": TAPPAY_APP_KEY }


# Retrieve client payment details from TapPay
def _tappy_pay_by_prime(prime, amount, order_number, name, email, phone):

    try:
        client = tappay.Client(is_sandbox=True, partner_key=TAPPAY_PARTNER_KEY, merchant_id=TAPPAY_MERCHANT_ID)
        card_holder_data = tappay.Models.CardHolderData(phone_number=phone, name=name, email=email)
        response = client.pay_by_prime(prime=prime, amount=amount, details=order_number, card_holder_data=card_holder_data)

        return response
    except Exception as e:
        print(e)
    

class OrderDetail(BaseModel):
    prime: str = Field(..., examples=["前端從第三方金流 TapPay 取得的交易碼"])
    name: str = Field(..., examples=["Jung"])
    email: str = Field(..., examples=["jung@example.com"])
    phone: str = Field(..., examples=["0912345678"])

@app.post("/api/orders")
async def create_order(request: Request, session: SessionDep, body: OrderDetail):
    payload = _decode_token(request)

    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )

    user_id = int(payload.get("id"))
    booking = query.get_booking_by_userid(session, user_id)
    attraction = query.get_attraction_by_id(session, booking.attr_id)

    # Create identical order number
    order_number = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{user_id}-{booking.id}"

    # Check if this booking already has an order
    if query.check_duplicate_order(session, user_id, booking.attr_id, booking.booking_date, booking.time):
        print("訂單建立失敗，已建立相同訂單")
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "訂單建立失敗，已建立相同訂單"}
        )

    try:
        # Create order
        order = query.create_order(session, user_id, body.prime, body.name, body.email, body.phone, order_number, booking, attraction)

        if order is None:
            print("訂單建立失敗，輸入不正確或其他原因")
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "訂單建立失敗，輸入不正確或其他原因"}
            )
        
        # Retrieve TapPay payment result
        tappay_result = _tappy_pay_by_prime(body.prime, booking.price, order_number, body.name, body.email, body.phone)

        # Update payment status
        order = query.update_order_status(session, order.id, tappay_result)

        if not order:
            print("付款失敗")
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "付款失敗"}
            )


        # Delete booking
        result = query.delete_booking(session, user_id)

        if result is None:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "刪除失敗"}
            )
        
        return {"data": {
                "number": order.order_number,
                "payment": {
                    "status": order.status,
                    "message": "付款成功"
                }
            }
        }
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )


@app.get("/api/orders/{orderNumber}")
def get_order_data(request: Request, session: SessionDep, orderNumber: str):
    payload = _decode_token(request)

    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )

    try:
        order = query.get_order_by_number(session, orderNumber)


        if order is None:
            return JSONResponse(
                status_code=400,
                content={"error": True, "message": "訂單編號不正確"}
            )

        user_id = int(payload.get("id"))

        # Check if the order owned by the user
        if order.user_id != user_id:
            return JSONResponse(
                status_code=403,
                content={"error": True, "message": "無權限存取此訂單"}
            )

        return {
            "data": {
                "number": order.order_number,
                "price": order.price,
                "trip": {
                    "attraction": {
                        "id": order.attr_id,
                        "name": order.attr_name,
                        "address": order.attr_address,
                        "image": order.attr_image[0]
                    },
                    "date": order.booking_date,
                    "time": order.time
                },
                "content": {
                    "name": order.name,
                    "email": order.email,
                    "phone": order.phone
                },
                "status": order.status
            }
        }
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )


# Get user's MCP token
@app.get("/api/token")
def get_token(request: Request, session: SessionDep):
    payload = _decode_token(request)
    user_id = int(payload.get("id"))
    
    try:
        token = query.get_token(session, user_id)
        return {"ok": True,"token": token.token}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )


# Regenerate user's MCP token
@app.put("/api/token")
def update_token(request: Request, session: SessionDep):
    payload = _decode_token(request)
    
    try:
        token = query.update_token(session, payload)
        return {"ok": True,"token": token.token}
    except Exception as e:
        print(e)
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器內部錯誤"}
        )
    
    

app.mount("/static", StaticFiles(directory = "static"), name = "static")