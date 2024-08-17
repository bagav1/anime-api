import json
import re
from types import TracebackType
from typing import Dict, List, Optional, Type, Union
from urllib.parse import unquote, urlencode

import cloudscraper
from bs4 import BeautifulSoup, ResultSet, Tag

from animeflv.exception import AnimeFLVParseError
from animeflv.schema import (
    AnimeInfo,
    AnimeShortInfo,
    DownloadLinkInfo,
    EpisodeFormat,
    EpisodeInfo,
    ListAnime,
)
from animeflv.utils import parse_table, removeprefix, safe_strip

BASE_URL = "https://animeflv.net"
BROWSE_URL = "https://animeflv.net/browse"
ANIME_VIDEO_URL = "https://animeflv.net/ver/"
ANIME_URL = "https://animeflv.net/anime/"
BASE_EPISODE_IMG_URL = "https://cdn.animeflv.net/screenshots/"


class AnimeFLV(object):
    def __init__(self, *args, **kwargs):
        session = kwargs.get("session", None)
        self._scraper = cloudscraper.create_scraper(session)

    def close(self) -> None:
        self._scraper.close()

    def __enter__(self) -> "AnimeFLV":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def get_links(
        self,
        id: str,
        episode: Union[str, int],
        format: EpisodeFormat = EpisodeFormat.Subtitled,
        **kwargs,
    ) -> List[DownloadLinkInfo]:
        """
        Get download links of specific episode.
        Return a list of dictionaries like:
        [
            {
                "server": "...",
                "url": "..."
            },
            ...
        ]

        :param id (str): Anime id, like as 'nanatsu-no-taizai'.
        :param episode (Union[str, int]): Episode id, like as '1'.
        :param format (EpisodeFormat): Format of the episode.
        :param **kwargs: Optional arguments for filter output (see doc).
        :return List[DownloadLinkInfo]:
        """
        response = self._scraper.get(f"{ANIME_VIDEO_URL}{id}-{episode}")
        soup = BeautifulSoup(response.text, "lxml")
        table = soup.find("table", attrs={"class": "RTbl"})

        try:
            rows = parse_table(table)
            ret = []

            for row in rows:
                if (
                    row["FORMATO"].string == "SUB"
                    and EpisodeFormat.Subtitled in format
                    or row["FORMATO"].string == "LAT"
                    and EpisodeFormat.Dubbed in format
                ):
                    ret.append(
                        DownloadLinkInfo(
                            server=row["SERVIDOR"].string,
                            url=re.sub(
                                r"^http[s]?://ouo.io/[A-Za-z0-9]+/[A-Za-z0-9]+\?[A-Za-z0-9]+=",
                                "",
                                unquote(row["DESCARGAR"].a["href"]),
                            ),
                        )
                    )

            return ret
        except Exception as exc:
            raise AnimeFLVParseError(exc) from exc

    def list(self, page: int = None) -> ListAnime:
        """
        Shortcut for search(query=None)
        """

        return self.search(page=page)

    def search(self, query: str = None, page: int = None) -> ListAnime:
        """
        Search in animeflv.net by query.
        :param query: Query information like: 'Nanatsu no Taizai'.
        :param page: Page of the information return.
        :rtype: ListAnime
        """

        if page is not None and not isinstance(page, int):
            raise TypeError

        params = dict()
        if query is not None:
            params["q"] = query
        if page is not None:
            params["page"] = page
        params = urlencode(params)

        url = f"{BROWSE_URL}"
        if params != "":
            url += f"?{params}"

        response = self._scraper.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        elements = soup.select("div.Container ul.ListAnimes li article")

        if elements is None:
            raise AnimeFLVParseError("Unable to get list of animes")

        pagination = soup.select("div.Container div.NvCnAnm ul.pagination li")

        cuurrent_page = 1
        total_pages = 1

        if len(pagination) > 1:
            cuurrent_page = soup.select_one("div.Container div.NvCnAnm ul.pagination li.active a").string
            total_pages = soup.select("div.Container div.NvCnAnm ul.pagination li")[-2].string


        return ListAnime(
            current_page=int(cuurrent_page),
            total_pages=int(total_pages) if int(total_pages) <= 150 else 150,
            data=self._process_anime_list_info(elements),
        )

    def get_video_servers(
        self,
        id: str,
        episode: int,
        format: EpisodeFormat = EpisodeFormat.Subtitled,
        **kwargs,
    ) -> List[Dict[str, str]]:
        """
        Get in video servers, this work only using the iframe element.
        Return a list of dictionaries.

        :param id: Anime id, like as 'nanatsu-no-taizai'.
        :param episode: Episode id, like as '1'.
        :rtype: list
        """

        response = self._scraper.get(f"{ANIME_VIDEO_URL}{id}-{episode}")
        soup = BeautifulSoup(response.text, "lxml")
        scripts = soup.find_all("script")

        servers = []

        for script in scripts:
            content = str(script)
            if "var videos = {" in content:
                videos = content.split("var videos = ")[1].split(";")[0]
                data = json.loads(videos)

                if "SUB" in data and EpisodeFormat.Subtitled in format:
                    servers.append(data["SUB"])
                if "LAT" in data and EpisodeFormat.Dubbed in format:
                    servers.append(data["LAT"])

        return servers

    def get_latest_episodes(self) -> List[EpisodeInfo]:
        """
        Get a list of new episodes released (possibly this last week).
        Return a list

        :rtype: list
        """

        response = self._scraper.get(BASE_URL)
        soup = BeautifulSoup(response.text, "lxml")

        elements = soup.select("ul.ListEpisodios li a")
        ret = []

        for element in elements:
            try:
                anime, _, id = element["href"].rpartition("-")

                ret.append(
                    EpisodeInfo(
                        id=id,
                        anime=removeprefix(anime, "/ver/"),
                        image_preview=f"{BASE_URL}{element.select_one('span.Image img').get('src')}",
                    )
                )
            except Exception as exc:
                raise AnimeFLVParseError(exc) from exc

        return ret

    def get_latest_animes(self) -> List[AnimeShortInfo]:
        """
        Get a list of new animes released.
        Return a list

        :rtype: list
        """

        response = self._scraper.get(BASE_URL)
        soup = BeautifulSoup(response.text, "lxml")

        elements = soup.select("ul.ListAnimes li article")

        if elements is None:
            raise AnimeFLVParseError("Unable to get list of animes")

        return self._process_anime_list_info(elements)

    def get_anime_info(self, id: str) -> AnimeInfo:
        """
        Get information about specific anime.
        Return a dictionary.

        :param id: Anime id, like as 'nanatsu-no-taizai'.
        :rtype: dict
        """
        response = self._scraper.get(f"{ANIME_URL}/{id}")
        soup = BeautifulSoup(response.text, "lxml")

        image = BASE_URL + "/" + soup.select_one("body div div div div div aside div.AnimeCover div.Image figure img").get("src", "")
        information = {
            "title": soup.select_one("body div.Wrapper div.Body div div.Ficha.fchlt div.Container h1.Title").string,
            "type": soup.select_one("body div.Wrapper div.Body div div.Ficha.fchlt div.Container span.Type").string,
            "rating": soup.select_one("body div div div.Ficha.fchlt div.Container div.vtshr div.Votes span#votes_prmd").string,
            "poster": image,
            "banner": image.replace("covers", "banners"),
            "synopsis": safe_strip(soup.select_one("body div div div div div main section div.Description p").string),
        }

        genres = []

        for element in soup.select("main.Main section.WdgtCn nav.Nvgnrs a"):
            if "=" in element["href"]:
                genres.append(element["href"].split("=")[1])

        info_ids = []
        episodes_data = []
        episodes = []

        try:
            for script in soup.find_all("script"):
                contents = str(script)

                if "var anime_info = [" in contents:
                    anime_info = contents.split("var anime_info = ")[1].split(";")[0]
                    info_ids.append(json.loads(anime_info))

                if "var episodes = [" in contents:
                    data = contents.split("var episodes = ")[1].split(";")[0]
                    episodes_data.extend(json.loads(data))

            next_episode = info_ids[0][3] if len(info_ids[0]) > 3 else None
            status = soup.select_one("body div div div div div aside p.AnmStts").string

            for episode, _ in episodes_data:
                episodes.append(
                    EpisodeInfo(
                        id=str(episode),
                        anime=id,
                        image_preview=f"{BASE_EPISODE_IMG_URL}{info_ids[0][0]}/{str(episode)}/th_3.jpg",
                    )
                )

        except Exception as exc:
            raise AnimeFLVParseError(exc) from exc

        return AnimeInfo(
            id=id,
            **information,
            genres=genres,
            status=status,
            next_episode=next_episode,
            episodes=episodes,
        )

    def _process_anime_list_info(self, elements: ResultSet[Tag]) -> List[AnimeShortInfo]:
        ret = []

        for element in elements:
            try:
                image = element.select_one("a div.Image figure img").get("src", None) or element.select_one("a div.Image figure img")["data-cfsrc"]
                ret.append(
                    AnimeShortInfo(
                        id=removeprefix(element.select_one("div.Description a.Button")["href"][1:], "anime/"),
                        title=element.select_one("a h3").string,
                        type=element.select_one("div.Description p span.Type").string,
                        rating=element.select_one("div.Description p span.Vts").string,
                        poster=image,
                        banner=image.replace("covers", "banners"),
                        synopsis=safe_strip(element.select("div.Description p")[1].string),
                    )
                )
            except Exception as exc:
                raise AnimeFLVParseError(exc) from exc

        return ret
