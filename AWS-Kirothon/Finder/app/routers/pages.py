"""웹 UI 페이지 라우터"""

from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.lost_item import LostItem

router = APIRouter()
templates = Jinja2Templates(directory="templates")


@router.get("/")
async def home(request: Request):
    """메인 페이지 - 채팅 입장"""
    return templates.TemplateResponse("index.html", {"request": request})


@router.get("/items")
async def items_page(request: Request, db: Session = Depends(get_db)):
    """분실물 목록 페이지"""
    items = db.query(LostItem).filter(LostItem.status == "active").order_by(LostItem.found_at.desc()).all()
    return templates.TemplateResponse("items.html", {"request": request, "items": items})


@router.get("/items/{item_id}")
async def item_detail_page(request: Request, item_id: int, db: Session = Depends(get_db)):
    """분실물 상세 페이지"""
    item = db.query(LostItem).filter(LostItem.id == item_id).first()
    if not item:
        from fastapi.responses import RedirectResponse
        return RedirectResponse(url="/items")
    return templates.TemplateResponse("item_detail.html", {"request": request, "item": item})


@router.get("/chat/{room_id}")
async def chat_page(request: Request, room_id: int, user_id: int = 0):
    """채팅 페이지"""
    return templates.TemplateResponse("chat.html", {
        "request": request,
        "room_id": room_id,
        "user_id": user_id,
    })
