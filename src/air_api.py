from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
import requests
from requests.exceptions import RequestException


class BaseAirspaceAPI(ABC):
    @abstractmethod
    def get_country_boundingbox(self, country: str) -> Optional[List[float]]:
        pass

    @abstractmethod
    def get_airplanes_in_bounds(self, lamin: float, lamax: float, lomin: float, lomax: float) -> List[Dict[str, Any]]:
        pass

    def get_aeroplanes_in_country(self, country: str) -> List[Dict[str, Any]]:
        bbox = self.get_country_boundingbox(country)
        if bbox is None:
            raise ValueError(f"Не удалось получить координаты для страны: '{country}'")
        min_lat, max_lat, min_lon, max_lon = bbox
        return self.get_airplanes_in_bounds(min_lat, max_lat, min_lon, max_lon)


class AirspaceAPI(BaseAirspaceAPI):
    NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
    OPENSKY_URL = "https://opensky-network.org/api/states/all"

    def __init__(self, user_agent: str = "flight-tracker/1.0", timeout: int = 10) -> None:
        if not user_agent or " " in user_agent:
            raise ValueError("User-Agent не должен содержать пробелов и не может быть пустым.")
        self.user_agent = user_agent
        self.timeout = timeout
        self._headers = {"User-Agent": self.user_agent}

    def _request_json(self, url: str, params: Optional[Dict[str, Any]] = None) -> Any:
        try:
            resp = requests.get(url, headers=self._headers, params=params, timeout=self.timeout)
            resp.raise_for_status()
            return resp.json()
        except RequestException as e:
            raise RequestException(f"Ошибка запроса к {url}: {e}") from e

    def get_country_boundingbox(self, country: str) -> Optional[List[float]]:
        params = {"country": country, "format": "json", "limit": 1}
        data = self._request_json(self.NOMINATIM_URL, params)
        if not isinstance(data, list) or len(data) == 0:
            return None
        first = data[0]
        bbox = first.get("boundingbox")
        if not bbox or len(bbox) != 4:
            return None
        try:
            return [float(x) for x in bbox]
        except ValueError, TypeError:
            return None

    def get_airplanes_in_bounds(self, lamin: float, lamax: float, lomin: float, lomax: float) -> List[Dict[str, Any]]:
        params = {
            "lamin": lamin,
            "lamax": lamax,
            "lomin": lomin,
            "lomax": lomax,
        }
        data = self._request_json(self.OPENSKY_URL, params)
        states_raw = data.get("states", [])
        if not isinstance(states_raw, list):
            return []

        result = []
        for state in states_raw:
            if not isinstance(state, list) or len(state) < 17:
                continue
            result.append(
                {
                    "icao24": state[0],
                    "callsign": state[1].strip() if isinstance(state[1], str) else state[1],
                    "origin_country": state[2],
                    "latitude": state[6],
                    "longitude": state[5],
                    "baro_altitude": state[7],
                    "geo_altitude": state[13],
                    "on_ground": bool(state[8]) if state[8] is not None else None,
                    "velocity": state[9],
                    "heading": state[10],
                    "vertical_rate": state[11],
                    "time_position": state[3],
                    "last_contact": state[4],
                    "squawk": state[14],
                    "spi": state[15],
                    "position_source": state[16],
                }
            )
        return result
