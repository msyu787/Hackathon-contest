"""분실물 찾아주기 AI 매칭 플랫폼 - FastAPI 애플리케이션"""

from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.core.database import Base, engine
from app.core.exceptions import register_exception_handlers

# 모든 모델을 import해야 Base.metadata에 테이블이 등록됨
import app.models.user  # noqa: F401
import app.models.lost_item  # noqa: F401
import app.models.chat  # noqa: F401

# 테이블 자동 생성 (개발 단계용)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="분실물 찾아주기 AI 매칭 플랫폼",
    description="비전 및 텍스트 기반 AI를 활용한 분실물 매칭 서비스",
    version="0.1.0",
)

register_exception_handlers(app)

# 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# 라우터 등록
from app.routers import chat, pages

app.include_router(chat.router, prefix="/chat", tags=["채팅"])
app.include_router(pages.router, tags=["페이지"])

# TODO: 나머지 라우터 등록 (각 모듈 구현 후 활성화)
# from app.routers import auth, items, search, meetings
# app.include_router(auth.router, prefix="/auth", tags=["인증"])
# app.include_router(items.router, prefix="/items", tags=["분실물"])
# app.include_router(search.router, prefix="/search", tags=["검색"])
# app.include_router(meetings.router, prefix="/meetings", tags=["만남 예약"])


@app.get("/health")
async def health():
    """헬스 체크 엔드포인트"""
    return {"success": True, "message": "분실물 찾아주기 플랫폼 API 서버 가동 중"}
