from pydantic import BaseModel


class CampusFigureOut(BaseModel):
    id: int
    name: str
    title: str
    avatar: str
    description: str
    category: str

    class Config:
        from_attributes = True


class CampusSceneryOut(BaseModel):
    id: int
    title: str
    image_url: str
    description: str | None = None
    location: str | None = None
    area: str

    class Config:
        from_attributes = True


class AnnouncementOut(BaseModel):
    title: str
    date: str | None = None
    url: str | None = None


class GalleryImageOut(BaseModel):
    title: str
    image_url: str
    campus: str  # 安州 / 游仙
