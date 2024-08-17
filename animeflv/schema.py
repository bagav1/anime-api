from typing import Optional, Union, List
from pydantic import BaseModel, Field
from enum import Flag, auto


class EpisodeInfo(BaseModel):
    id: Union[str, int] = Field(..., description="Episode id", examples=["1a2b3c", 123])
    anime: str = Field(..., description="Anime title", examples=["Nanatsu no Taizai", "One Piece"])
    image_preview: Optional[str] = Field(None, description="Episode image preview")

class AnimeShortInfo(BaseModel):
    id: Union[str, int] = Field(..., description="Anime id", examples=["1a2b3c", 123])
    title: str = Field(..., description="Anime title", examples=["Nanatsu no Taizai", "One Piece"])
    type: Optional[str] = Field(None, description="Anime type")
    rating: Optional[str] = Field(None, description="Anime rating")
    poster: Optional[str] = Field(None, description="Anime poster")
    banner: Optional[str] = Field(None, description="Anime banner")
    synopsis: Optional[str] = Field(None, description="Anime synopsis")

class AnimeInfo(AnimeShortInfo):
    genres: Optional[List[str]] = Field(None, description="Anime genres")
    status: Optional[str] = Field(None, description="Anime status")
    next_episode: Optional[str] = Field(None, description="Date of next episode")
    episodes: Optional[List[EpisodeInfo]] = Field(None, description="Anime episodes")


class ListAnime(BaseModel):
    current_page: int = Field(..., description="Current page")
    total_pages: int = Field(..., description="Total pages")
    data: List[AnimeShortInfo] = Field(..., description="Anime list")

class DownloadLinkInfo(BaseModel):
    server: str = Field(..., description="Video server")
    url: str = Field(..., description="Video url")


class EpisodeFormat(Flag):
    Subtitled = auto()
    Dubbed = auto()
