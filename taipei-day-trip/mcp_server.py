import query

from fastmcp import FastMCP
from sqlmodel import Session
from fastmcp.server.dependencies import get_http_request
from database import engine


mcp = FastMCP("台北一日遊")

def get_user_id():
    # Get mcp token
    request = get_http_request()
    auth = request.headers.get("authorization", "")

    if not auth.startswith("Bearer "):
        return None

    mcp_token = auth.removeprefix("Bearer ").strip()

    # Get user id
    with Session(engine) as session:
        user_id = query.get_user_by_mcp_token(session, mcp_token)

    if user_id:
        return user_id
    
    return None


@mcp.tool(name="搜尋台北市景點", description="透過關鍵字和捷運站名搜尋台北市一日旅遊的景點")
def search_attractions(keyword: str) -> dict:
    user_id = get_user_id()
    
    if user_id is None:
        return {"error": True}
    
    try:
        with Session(engine) as session:
            attractions = query.get_attractions_by_keyword(session, keyword)

        print(attractions)

        return { 
            "data": [
                {
                    "id": attr.attr_id,
                    "name": attr.name,
                    "description": attr.description
                }                
                for attr in attractions
            ]   
        }
    except Exception as e:
        print(e)
        return {"error": True}


@mcp.tool(name="預訂景點導覽行程", description="根據景點編號、日期、時間、價格，預定一個景點導覽行程")
def add_to_cart(date: str, time: str, id: int) -> dict:
    user_id = get_user_id()

    if user_id is None:
        return {"error": True}

    try:
        with Session(engine) as session:
            attraction = query.get_attraction_by_id(session, id)

            if attraction is None:
                return {"error": True}

            if time == "早上":
                price = "2000"
            elif time == "下午":
                price = "2500"

            query.add_booking_to_cart(session, user_id, id, date, time, price)

            url = "http://127.0.0.1:8000/booking"
            
            message = f"(台北導覽行程，預定成功，請到 {url} 完成付款。)"

            return {"ok": True, "message": message}
    except Exception as e:
        print(e)
        return {"error": True}

mcp_app = mcp.http_app(path="/")