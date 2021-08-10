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


def parse_date(
    day: int, month: str, year=datetime.datetime.now().year
) -> datetime.date:
    """Parse a German medium-form date, e.g. 17. August into a datetime.date"""
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
    date = datetime.date(
        year=int(year),
        month=1 + months.index(month),
        day=parse_num(day),
    )
    return date


@dataclass
class IncidenceData:
    location: str
    date: str
    incidence: float
    total_cases: int = 0
    num_infected: int = 0
    num_recovered: int = 0
    num_dead: int = 0


@dataclass
class VaccinationData:
    date: str

    total_vaccinations: int = 0
    num_vaccinated_once: int = 0
    num_vaccinated_full: int = 0

    ratio_vaccinated_once: float = 0.0
    ratio_vaccinated_full: float = 0.0


class CovidCrawlerBase(ABC):
    @abstractmethod
    def crawl_incidence(self) -> IncidenceData:
        pass

    @abstractmethod
    def crawl_vaccination(self) -> VaccinationData:
        pass


class CovidCrawler(CovidCrawlerBase):
    def __init__(self, hass=None) -> None:
        self.hass = hass

    async def crawl_incidence(self) -> IncidenceData:
        """
        Fetch COVID-19 infection data from the target website.
        """

        _log.info("Fetching COVID-19 data update")

        url = (
            "https://www.augsburg.de/umwelt-soziales/gesundheit/coronavirus/fallzahlen"
        )
        if self.hass:
            from homeassistant.helpers import aiohttp_client

            result = await aiohttp_client.async_get_clientsession(self.hass).get(url)
            soup = BeautifulSoup(await result.text(), "html.parser")
        else:
            import requests

            result = requests.get(url)
            if not result.ok:
                result.raise_for_status()
            soup = BeautifulSoup(result.text, "html.parser")

        match = soup.find(class_="frame--type-textpic")
        text = match.p.text
        _log.debug(f"Infection data text: {text}")

        matches = re.search(r"(\d+,\d+)\sNeuinfektion", text)
        if not matches:
            raise ValueError(
                f"Could not extract incidence from scraped web page, {text=}"
            )

        incidence = parse_num(matches.group(1), t=float)
        _log.debug(f"Parsed incidence: {incidence}")

        text = match.h2.text
        matches = re.search(r"\((\d+)\. (\w+).*\)", text)
        if not matches:
            raise ValueError(f"Could not extract date from scraped web page, {text=}")

        date = parse_date(matches.group(1), matches.group(2))
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

    async def crawl_vaccination(self) -> VaccinationData:
        _log.info("Fetching COVID-19 vaccination data update")
        url = "https://www.augsburg.de/umwelt-sozgcoiales/gesundheit/coronavirus/impfzentrum"
        container_id = "c1088140"

        if self.hass:
            from homeassistant.helpers import aiohttp_client

            result = await aiohttp_client.async_get_clientsession(self.hass).get(url)
            soup = BeautifulSoup(await result.text(), "html.parser")
        else:
            import requests

            result = requests.get(url)
            if not result.ok:
                result.raise_for_status()
            soup = BeautifulSoup(result.text, "html.parser")

        result = soup.find(id=container_id)
        text = re.sub(r"\s+", " ", result.text)
        regexes = [
            r"(?P<total_vaccinations>\d+[.]\d+) Impfdosen",
            r"Weitere (?P<num_vaccinated_once>\d+[.]\d+) Personen haben die Erstimpfung erhalten",
            r"(?P<num_vaccinated_full>\d+[.]\d+) Personen sind bereits vollständig geimpft",
        ]
        values = {}
        for r in regexes:
            matches = re.search(r, text)
            if not matches:
                continue
            values.update(
                {
                    k: parse_num(v.replace(".", ""))
                    for k, v in matches.groupdict().items()
                }
            )

        matches = re.search(r"Stand (?P<day>\d+)\. (?P<month>\w+) (?P<year>\d+)", text)
        if not matches:
            raise ValueError(f"Could not extract date from scraped web page, {text=}")

        values["date"] = parse_date(**matches.groupdict()).strftime("%Y-%m-%d")
        result = VaccinationData(**values)

        # Total population in Augsburg as of 2020
        # https://www.augsburg.de/fileadmin/user_upload/buergerservice_rathaus/rathaus/statisiken_und_geodaten/statistiken/Monitoring/Demografiemonitoring_der_Stadt_Augsburg_2021.pdf
        population = 299021

        result.ratio_vaccinated_full = result.num_vaccinated_full / population
        result.ratio_vaccinated_once = result.num_vaccinated_once / population
        _log.debug(f"Result data: {result}")

        return result
