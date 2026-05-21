import re
import httpx
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from bs4 import BeautifulSoup

from app.core.database import get_db
from app.models.campus import CampusFigure, CampusScenery
from app.schemas.campus import CampusFigureOut, CampusSceneryOut, AnnouncementOut

router = APIRouter(prefix="/api/campus", tags=["campus"])


@router.get("/figures", response_model=list[CampusFigureOut])
def list_figures(category: str | None = None, db: Session = Depends(get_db)):
    query = db.query(CampusFigure)
    if category:
        query = query.filter(CampusFigure.category == category)
    return query.all()


@router.get("/sceneries", response_model=list[CampusSceneryOut])
def list_sceneries(area: str | None = None, db: Session = Depends(get_db)):
    query = db.query(CampusScenery)
    if area:
        query = query.filter(CampusScenery.area == area)
    return query.all()


@router.get("/announcements", response_model=list[AnnouncementOut])
async def list_announcements():
    try:
        async with httpx.AsyncClient(timeout=10, follow_redirects=True) as client:
            resp = await client.get("https://jwc.mycc.edu.cn/jwgl/tzgg.htm")
            resp.encoding = "utf-8"
            soup = BeautifulSoup(resp.text, "html.parser")
        items = []
        for li in soup.find_all("li"):
            a = li.find("a")
            if not a:
                continue
            href = a.get("href", "")
            if "info/1011/" not in href:
                continue
            text = a.get_text(strip=True)
            date_match = re.search(r"(\d{4}-\d{2}-\d{2})$", text)
            date = date_match.group(1) if date_match else None
            title = text[:-10] if date else text
            full_url = "https://jwc.mycc.edu.cn" + href.replace("../", "/")
            items.append(AnnouncementOut(title=title, date=date, url=full_url))
        return items[:10]
    except Exception:
        return []
