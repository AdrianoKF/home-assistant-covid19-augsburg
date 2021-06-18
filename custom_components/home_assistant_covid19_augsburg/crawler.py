import datetime
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from bs4 import BeautifulSoup

_log = logging.getLogger(__name__)


def parse_num(s, t=int):
    if len(s):
        return t(s.replace(".", "").replace(",", "."))
    return 0


@dataclass
class IncidenceData:
    location: str
    date: str
    incidence: float
    total_cases: int = 0
    num_infected: int = 0
    num_recovered: int = 0
    num_dead: int = 0


class CovidCrawlerBase(ABC):
    @abstractmethod
    def crawl(self) -> IncidenceData:
        pass


class CovidCrawler(CovidCrawlerBase):
    def __init__(self, hass=None) -> None:
        self.url = (
            "https://www.augsburg.de/umwelt-soziales/gesundheit/coronavirus/fallzahlen"
        )
        self.hass = hass

    async def crawl(self) -> IncidenceData:
        """
        Fetch COVID-19 infection data from the target website.
        """

        _log.info("Fetching COVID-19 data update")

        if self.hass:
            from homeassistant.helpers import aiohttp_client

            result = await aiohttp_client.async_get_clientsession(self.hass).get(
                self.url
            )
            soup = BeautifulSoup(await result.text(), "html.parser")
        else:
            import requests

            result = requests.get(self.url)
            if not result.ok:
                result.raise_for_status()
            soup = BeautifulSoup(result.text, "html.parser")

        match = soup.find(class_="frame--type-textpic")
        text = match.p.text
        _log.debug(f"Infection data text: {text}")

        matches = re.search(r"(\d+,\d+) Neuinfektion", text)
        if not matches:
            raise ValueError("Could not extract incidence from scraped web page")

        incidence = parse_num(matches.group(1), t=float)
        _log.debug(f"Parsed incidence: {incidence}")

        text = match.h2.text
        matches = re.search(r"\((\d+)\. (\w+)\)", text)
        if not matches:
            raise ValueError("Could not extract date from scraped web page")

        months = [
            "Januar",
            "Februar",
            "März",
            "April",
            "Mai",
            "Juni",
            "Juli",
            "August",
            "September",
            "Oktober",
            "November",
            "Dezember",
        ]
        day = parse_num(matches.group(1))
        month_name = matches.group(2)
        date = datetime.date(
            year=datetime.datetime.now().year,
            month=1 + months.index(month_name),
            day=day,
        )
        _log.debug(f"Parsed date: {date}")

        match = match.find_next_sibling(class_="frame--type-textpic")
        text = match.text
        _log.debug(f"Infection counts text: {text}")

        regexes = [
            r"Insgesamt: (?P<total_cases>[0-9.]+)",
            r"genesen: (?P<num_recovered>[0-9.]+)",
            r"infiziert: (?P<num_infected>[0-9.]+)",
            r"verstorben: (?P<num_dead>[0-9.]+)",
        ]
        cases = {}
        for r in regexes:
            matches = re.search(r, text)
            if not matches:
                continue
            cases.update(
                {
                    k: parse_num(v.replace(".", ""))
                    for k, v in matches.groupdict().items()
                }
            )

        result = IncidenceData(
            "Augsburg", incidence=incidence, date=date.strftime("%Y-%m-%d"), **cases
        )
        _log.debug(f"Result data: {result}")

        return result
