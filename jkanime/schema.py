from typing import Optional, Union, List
from pydantic import BaseModel, Field


class EpisodeInfo(BaseModel):
    id: str = Field(..., description="Episode id")
    anime_id: str = Field(..., description="Anime id")
    image_preview: Optional[str] = Field(None, description="Episode image preview")
    date: Optional[str] = Field(None, description="Episode date")


class AnimeShortInfo(BaseModel):
    id: str = Field(..., description="Anime id")
    title: str = Field(..., description="Anime title")
    poster: Optional[str] = Field(None, description="Anime poster")
    type: Optional[str] = Field(None, description="Anime type")
    status: Optional[str] = Field(None, description="Anime status")
    synopsis: Optional[str] = Field(None, description="Anime synopsis")
    last_episode: Optional[EpisodeInfo] = Field(None, description="Last episode")


class AnimeInfo(AnimeShortInfo):
    unique_id: str = Field(..., description="Unique id")
    alt_title: Optional[str] = Field(None, description="Alternative title")
    genres: Optional[List[str]] = Field(None, description="Anime genres")
    study: Optional[str] = Field(None, description="Anime study")
    demographic: Optional[str] = Field(None, description="Anime demographic")
    languages: Optional[List[str]] = Field(None, description="Anime languages")
    number_of_episodes: Optional[str] = Field(None, description="Number of episodes")
    duration: Optional[str] = Field(None, description="Anime duration")
    debut: Optional[str] = Field(None, description="Anime debut")
    quality: Optional[str] = Field(None, description="Anime quality")
    episodes: Optional[List[EpisodeInfo]] = Field(None, description="Anime episodes")


class LastAnimes(BaseModel):
    animes: List[AnimeShortInfo] = Field(..., description="Anime list")


class AnimeList(BaseModel):
    current_page: int = Field(..., description="Current page")
    last_page: bool = Field(..., description="Last page")
    data: List[AnimeShortInfo] = Field(..., description="Anime list")


class LastEpisodes(BaseModel):
    episodes: List[EpisodeInfo] = Field(..., description="Last episodes")


class Schedule(BaseModel):
    day: str = Field(..., description="Day")
    anime: List[AnimeShortInfo] = Field(..., description="Anime list")


class ListSchedule(BaseModel):
    schedule: List[Schedule] = Field(..., description="Schedule list")


class EpisodeVideoUrls(BaseModel):
    urls: List[Optional[str]] = Field(..., description="Video urls")