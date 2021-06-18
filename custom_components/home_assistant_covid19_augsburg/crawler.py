import datetime
import locale
import logging
import re
from abc import ABC, abstractmethod
from dataclasses import dataclass

from bs4 import BeautifulSoup
from homeassistant import aiohttp_client

_log = logging.getLogger(__name__)


@dataclass
class IncidenceData:
    location: str
    date: datetime.date
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
    def __init__(self, hass) -> None:
        self.url = (
            "https://www.augsburg.de/umwelt-soziales/gesundheit/coronavirus/fallzahlen"
        )
        self.hass = hass

    async def crawl(self) -> IncidenceData:
        """
        Fetch COVID-19 infection data from the target website.
        """

        _log.info("Fetching COVID-19 data update")

        locale.setlocale(locale.LC_ALL, "de_DE.utf8")

        result = await aiohttp_client.async_get_clientsession(self.hass).get(self.url)
        soup = BeautifulSoup(await result.text(), features="html.parser")

        match = soup.find(class_="frame--type-textpic")
        text = match.p.text
        _log.debug(f"Infection data text: {text}")

        matches = re.search(r"(\d+,\d+) Neuinfektion", text)
        if not matches:
            raise ValueError("Could not extract incidence from scraped web page")

        incidence = locale.atof(matches.group(1))
        _log.debug(f"Parsed incidence: {incidence}")

        text = match.h2.text
        matches = re.search(r"\((\d+\. \w+)\)", text)
        if not matches:
            raise ValueError("Could not extract date from scraped web page")

        date = datetime.datetime.strptime(matches.group(1), "%d. %B")
        date = date.replace(year=datetime.datetime.now().year).date()
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
                {k: int(v.replace(".", "")) for k, v in matches.groupdict().items()}
            )

        result = IncidenceData("Augsburg", incidence, date, **cases)
        _log.debug(f"Result data: {result}")

        return result
