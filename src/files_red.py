import json
from abc import ABC, abstractmethod
from pathlib import Path
from typing import List

from src.airplane import Airplane


class StorageConnector(ABC):
    @abstractmethod
    def add_airplane(self, airplane: Airplane) -> None:
        pass

    @abstractmethod
    def add_airplanes(self, airplanes: List[Airplane]) -> None:
        pass

    @abstractmethod
    def get_all(self) -> List[Airplane]:
        pass

    @abstractmethod
    def get_by_country(self, country: str) -> List[Airplane]:
        pass

    @abstractmethod
    def remove_by_icao24(self, icao24: str) -> bool:
        pass

    @abstractmethod
    def clear_all(self) -> None:
        pass


class JsonStorage(StorageConnector):
    def __init__(self):
        self.filename = "airplanes.json"
        self.base_dir = "data"
        self._data: List[Airplane] = []
        # При инициализации пытаемся загрузить данные
        self._load()

    def _load(self) -> None:
        """Загружает данные из JSON в список _data."""
        file_path = Path(self.base_dir) / self.filename

        if not file_path.exists():
            self._data = []
            return

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                raw_list = json.load(f)
                self._data = [
                    Airplane(
                        icao24=r["icao24"],
                        callsign=r.get("callsign", ""),
                        origin_country=r.get("origin_country", ""),
                        velocity=r.get("velocity", 0.0),
                        geo_altitude=r.get("geo_altitude"),
                        latitude=r.get("latitude"),
                        longitude=r.get("longitude"),
                        on_ground=r.get("on_ground"),
                        heading=r.get("heading"),
                        baro_altitude=r.get("baro_altitude"),
                    )
                    for r in raw_list
                ]
        except json.JSONDecodeError, FileNotFoundError, KeyError:
            # Если файл битый или пустой — начинаем с чистого листа
            self._data = []

    def _save(self) -> None:
        """Сохраняет текущий список _data в JSON."""
        file_path = Path(self.base_dir) / self.filename
        file_path.parent.mkdir(parents=True, exist_ok=True)

        serialized = [
            {
                "icao24": p.icao24,
                "callsign": p.callsign,
                "origin_country": p.origin_country,
                "velocity": p.velocity,
                "geo_altitude": p.geo_altitude,
                "latitude": p.latitude,
                "longitude": p.longitude,
                "on_ground": p.on_ground,
                "heading": p.heading,
                "baro_altitude": p.baro_altitude,
            }
            for p in self._data
        ]

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(serialized, f, indent=2, ensure_ascii=False)

    # --- РЕАЛИЗАЦИЯ ВСЕХ АБСТРАКТНЫХ МЕТОДОВ (ОБЯЗАТЕЛЬНО) ---

    def add_airplane(self, airplane: Airplane) -> None:
        """Добавляет один самолёт (обёртка)."""
        self.add_airplanes([airplane])

    def add_airplanes(self, airplanes: List[Airplane]) -> None:
        """Добавляет список самолётов, игнорируя дубли по icao24."""
        for plane in airplanes:
            if any(p.icao24 == plane.icao24 for p in self._data):
                continue
            self._data.append(plane)
        self._save()

    def get_all(self) -> List[Airplane]:
        """Возвращает копию списка всех самолётов."""
        return list(self._data)

    def get_by_country(self, country: str) -> List[Airplane]:
        """Фильтрует самолёты по стране (регистронезависимо)."""
        country_lower = country.lower()
        return [p for p in self._data if p.origin_country.lower() == country_lower]

    def remove_by_icao24(self, icao24: str) -> bool:
        """Удаляет самолёт по icao24. Возвращает True, если удаление произошло."""
        initial_len = len(self._data)
        self._data = [p for p in self._data if p.icao24 != icao24]
        removed = len(self._data) < initial_len
        if removed:
            self._save()
        return removed

    def clear_all(self) -> None:
        """Очищает хранилище полностью."""
        self._data.clear()
        self._save()


# Заглушки для других форматов (оставляем как есть)
class CsvStorage(StorageConnector):
    def __init__(self, filepath: str = "airplanes.csv") -> None:
        self.filepath = filepath

    def add_airplane(self, airplane: Airplane) -> None:
        raise NotImplementedError

    def add_airplanes(self, airplanes: List[Airplane]) -> None:
        raise NotImplementedError

    def get_all(self) -> List[Airplane]:
        raise NotImplementedError

    def get_by_country(self, country: str) -> List[Airplane]:
        raise NotImplementedError

    def remove_by_icao24(self, icao24: str) -> bool:
        raise NotImplementedError

    def clear_all(self) -> None:
        raise NotImplementedError


class ExcelStorage(StorageConnector):
    def __init__(self, filepath: str = "airplanes.xlsx") -> None:
        self.filepath = filepath

    def add_airplane(self, airplane: Airplane) -> None:
        raise NotImplementedError

    def add_airplanes(self, airplanes: List[Airplane]) -> None:
        raise NotImplementedError

    def get_all(self) -> List[Airplane]:
        raise NotImplementedError

    def get_by_country(self, country: str) -> List[Airplane]:
        raise NotImplementedError

    def remove_by_icao24(self, icao24: str) -> bool:
        raise NotImplementedError

    def clear_all(self) -> None:
        raise NotImplementedError


class TxtStorage(StorageConnector):
    def __init__(self, filepath: str = "airplanes.txt") -> None:
        self.filepath = filepath

    def add_airplane(self, airplane: Airplane) -> None:
        raise NotImplementedError

    def add_airplanes(self, airplanes: List[Airplane]) -> None:
        raise NotImplementedError

    def get_all(self) -> List[Airplane]:
        raise NotImplementedError

    def get_by_country(self, country: str) -> List[Airplane]:
        raise NotImplementedError

    def remove_by_icao24(self, icao24: str) -> bool:
        raise NotImplementedError

    def clear_all(self) -> None:
        raise NotImplementedError
