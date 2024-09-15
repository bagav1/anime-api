import json
import re
from types import TracebackType
from typing import List, Optional, Type

import cloudscraper
from bs4 import BeautifulSoup

from jkanime.exception import JKAnimeParseError
from jkanime.schema import (
    AnimeInfo,
    AnimeList,
    AnimeShortInfo,
    EpisodeInfo,
    EpisodeVideoUrls,
    LastAnimes,
    LastEpisodes,
    ListSchedule,
    Schedule,
)
from jkanime.utils import removeprefix, safe_strip

BASE_URL = "https://jkanime.net"
DIRECTORY_URL = f"{BASE_URL}/directorio/"
SEARCH_URL = f"{BASE_URL}/buscar/"
PAGINATION_EP = f"{BASE_URL}/ajax/pagination_episodes/"
SCHEDULE_URL = f"{BASE_URL}/horario/"


class JKAnime(object):
    def __init__(self, *args, **kwargs):
        session = kwargs.get("session", None)
        self._scraper = cloudscraper.create_scraper(
            session,
            browser={"browser": "chrome", "platform": "windows", "desktop": True},
        )

    def close(self) -> None:
        self._scraper.close()

    def __enter__(self) -> "JKAnime":
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType],
    ) -> None:
        self.close()

    def list(self, page: int = 1) -> AnimeList:
        url = f"{DIRECTORY_URL}/{page}"

        response = self._scraper.get(url, headers={"Referer": BASE_URL})
        soup = BeautifulSoup(response.text, "lxml")
        try:
            last_page = True
            if soup.select_one("div.navigation a.nav-next"):
                last_page = False

            elements = soup.select("div.page_directorio div.custom_item2")

            animes = []
            for element in elements:
                information = AnimeShortInfo(
                    id=removeprefix(element.select_one("div.custom_thumb2 .card-title a").get("href"), BASE_URL),
                    title=safe_strip(element.select_one("div.custom_thumb2 .card-title a").text),
                    poster=element.select_one("div.custom_thumb2 img").get("src"),
                    type=safe_strip(element.select_one("div.card-body div.card-info p.card-txt").text),
                    status=safe_strip(element.select_one("div.card-body div.card-info p.card-status").text),
                    synopsis=safe_strip(element.select_one("div.card-body p.synopsis").text),
                )

                animes.append(information)

            return AnimeList(current_page=page, last_page=last_page, data=animes)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def search(self, query: str = None, page: int = 1) -> AnimeList:
        url = f"{SEARCH_URL}/{query}/{page}"

        response = self._scraper.get(url, headers={"Referer": BASE_URL})
        soup = BeautifulSoup(response.text, "lxml")

        try:
            last_page = True
            if soup.select_one("div.navigation a.nav-next"):
                last_page = False

            elements = soup.select("section.contenido div.row div.row div.anime__item")

            animes = []
            for element in elements:
                information = AnimeShortInfo(
                    id=removeprefix(element.select_one("div.anime__item__text a").get("href"), BASE_URL).replace("/", ""),
                    title=safe_strip(element.select_one("div#ainfo div.title").text),
                    poster=element.select_one("div.anime__item__pic").get("data-setbg"),
                    type=safe_strip(element.select_one("div.anime__item__text li.anime").text),
                    status=safe_strip(element.select_one("div.anime__item__text ul li").text),
                    synopsis=safe_strip(element.select_one("div#ainfo p").text),
                )

                animes.append(information)

            return AnimeList(current_page=page, last_page=last_page, data=animes)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def get_latest_animes(self) -> LastAnimes:
        url = BASE_URL

        response = self._scraper.get(url)
        soup = BeautifulSoup(response.text, "lxml")

        try:
            elements = soup.select("section.contenido div.trending__anime div.anime__item")

            animes = []
            for element in elements:
                information = AnimeShortInfo(
                    id=removeprefix(element.select_one("div.anime__item__text a").get("href"), BASE_URL).replace("/", ""),
                    title=safe_strip(element.select_one("div.anime__item__text a").text),
                    poster=element.select_one("div.anime__item__pic")["data-setbg"],
                    type=safe_strip(element.select_one("div.anime__item__text ul li.anime").text),
                    status=safe_strip(element.select_one("div.anime__item__text ul li:first-child").text),
                    synopsis=None,
                )

                animes.append(information)

            return LastAnimes(animes=animes)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def get_latest_episodes(self) -> LastEpisodes:
        response = self._scraper.get(BASE_URL)
        soup = BeautifulSoup(response.text, "lxml")

        try:
            elements = soup.select("section.hero div.listadoanime-home a.bloqq")

            episodes = []
            for element in elements:
                anime, _, id = removeprefix(element["href"], BASE_URL)[1:-1].rpartition("/")
                information = EpisodeInfo(
                    id=id,
                    anime_id=anime,
                    image_preview=element.select_one("div.anime__sidebar__comment__item__pic img")["src"],
                )
                episodes.append(information)

            return LastEpisodes(episodes=episodes)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def get_schedule(self) -> ListSchedule:
        response = self._scraper.get(SCHEDULE_URL)
        soup = BeautifulSoup(response.text, "lxml")

        try:
            days = soup.select("section.contenido div.semana:not(div.filtro)")

            schedule = []
            for day in days:
                elements = day.select("div.cajas div.box")
                animes = []
                for element in elements:
                    episode_id = re.findall(r"\d+", element.select_one("div.last span").text)[0]
                    anime_id = removeprefix(element.select_one("a").get("href"), BASE_URL).replace("/", "")
                    information = AnimeShortInfo(
                        id=anime_id,
                        title=safe_strip(element.select_one("a").text),
                        poster=element.select_one("div.boxx img").get("src"),
                        last_episode=EpisodeInfo(
                            id=episode_id,
                            anime_id=anime_id,
                            date=safe_strip(element.select_one("div.last time").text)),
                    )
                    animes.append(information)

                schedule.append(Schedule(day=safe_strip(day.select_one("h2").text), anime=animes))

            return ListSchedule(schedule=schedule)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def get_anime_info(self, id: str) -> AnimeInfo:
        url = f"{BASE_URL}/{id}"

        response = self._scraper.get(url, headers={"Referer": BASE_URL})
        soup = BeautifulSoup(response.text, "lxml")

        try:
            container = soup.select_one("div.anime__details__content div.row")
            anime_details = container.select("div.anime__details__widget div.row ul li")

            type = safe_strip(" ".join(anime_details[0].text.split(":")[1:]))
            if type == "Serie":
                type = "Anime"

            genres = anime_details[1].text.split(":")[1:][0].split(", ")
            languages = anime_details[4].text.split(":")[1:][0].split(", ")

            information = {
                "id": id,
                "unique_id": container.select_one("div#guardar-anime").get("data-anime"),
                "title": safe_strip(container.select_one("div.anime__details__title h3").text),
                "alt_title": safe_strip(container.select_one("div.anime__details__title span").text),
                "poster": container.select_one("div.anime__details__pic").get("data-setbg"),
                "synopsis": safe_strip(container.select_one("p.sinopsis").text),
                "type": type,
                "genres": [safe_strip(genre) for genre in genres],
                "study": safe_strip(" ".join(anime_details[2].text.split(":")[1:])),
                "demographic": safe_strip(" ".join(anime_details[3].text.split(":")[1:])),
                "languages": [language.strip() for language in languages],
                "number_of_episodes": safe_strip(" ".join(anime_details[5].text.split(":")[1:])),
                "duration": safe_strip(" ".join(anime_details[6].text.split(":")[1:])),
                "debut": safe_strip(" ".join(anime_details[7].text.split(":")[1:])),
                "status": safe_strip(" ".join(anime_details[8].text.split(":")[1:])),
                "quality": safe_strip(" ".join(anime_details[9].text.split(":")[1:])),
            }

            pagination_ep = soup.select("div.capitulos div.anime__pagination a")

            episodes = []

            for i in range(len(pagination_ep)):
                resp = self._scraper.get(
                    f"{PAGINATION_EP}/{information['unique_id']}/{i + 1}",
                    headers={"Referer": BASE_URL},
                )
                resp.raise_for_status()

                episodes.extend(
                    [
                        EpisodeInfo(
                            id=e["number"],
                            anime_id=id,
                            image_preview="https://cdn.jkdesu.com/assets/images/animes/video/image_thumb/" + e["image"],
                        )
                        for e in resp.json()
                    ]
                )

            information["episodes"] = episodes

            return AnimeInfo(**information)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def get_video_stream(self, id: str, episode: int = 1) -> EpisodeVideoUrls:
        url = f"{BASE_URL}/{id}/{episode}"

        response = self._scraper.get(url, headers={"Referer": BASE_URL})
        soup = BeautifulSoup(response.text, "lxml")

        try:
            iframe_urls = []
            for script in soup.find_all("script"):
                contents = str(script)
                remote = BASE_URL

                pattern = r"video\[\d+\]\s*=.*?<iframe.*?<\/iframe>"
                matches = re.findall(pattern, contents, re.DOTALL)
                for match in matches:
                    src_pattern = r"src=[\"\']([^\"\']+)[\"\']"
                    src_matches = re.findall(src_pattern, match)
                    iframe_urls.extend([remote + src for src in src_matches])

                pattern_data_ep = r"var servers\s*=\s*(\[\{.*?\}\])"
                match_data_ep = re.search(pattern_data_ep, contents)

                if match_data_ep:
                    caps = json.loads(match_data_ep.group(1))
                    for cap in caps:
                        if cap["server"] != "Mediafire":
                            iframe_urls.append(f"{remote}/c1.php?u={cap['remote']}&s={cap['server'].lower()}")

            urls = []
            src_stream = ["https://jkanime.net/stream/", "https://moodle1.playmudos.com"]
            for url in iframe_urls:
                resp = self._scraper.get(url, headers={"Referer": BASE_URL})
                urls.append(safe_strip(self.__stream_url(resp.text, src_stream)))

            return EpisodeVideoUrls(urls=urls)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def get_links(self, id: str, episode: int = 1) -> EpisodeVideoUrls:
        url = f"{BASE_URL}/{id}/{episode}"

        response = self._scraper.get(url, headers={"Referer": BASE_URL})
        soup = BeautifulSoup(response.text, "lxml")

        try:
            urls = []
            for script in soup.find_all("script"):
                contents = str(script)
                remote = BASE_URL

                pattern_remote = r"var remote\s*=\s*\'([^\']+)\'"
                match_remote = re.search(pattern_remote, contents)
                pattern_data_ep = r"var servers\s*=\s*(\[\{.*?\}\])"
                match_data_ep = re.search(pattern_data_ep, contents)

                if match_remote and match_data_ep:
                    caps = json.loads(match_data_ep.group(1))
                    remote = match_remote.group(1)
                    for cap in caps:
                        urls.append(f"{remote}/d/{cap['slug']}")

            return EpisodeVideoUrls(urls=urls)
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc

    def __stream_url(self, html_content: str, hostnames: List[str]) -> Optional[str]:
        soup = BeautifulSoup(html_content, "lxml")

        try:
            dplayer_pattern = r"DPlayer\({.*?}\);"
            matches = re.findall(dplayer_pattern, html_content, re.DOTALL)
            for match in matches:
                for hostname in hostnames:
                    url_match = re.search(re.escape(hostname) + r'[^\s\'"]+', match)
                    if url_match:
                        return url_match.group(0)

            for script in soup.find_all("script"):
                script_content = script.string
                if script_content:
                    for hostname in hostnames:
                        match = re.search(re.escape(hostname) + r'[^\s\'"]+', script_content)
                        if match:
                            return match.group(0)

            for tag in soup.find_all(["iframe", "source"]):
                return tag.get("src")

            return None
        except Exception as exc:
            raise JKAnimeParseError(exc) from exc
