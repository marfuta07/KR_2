import json
import os
from abc import ABC, abstractmethod
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
    def __init__(self, filename: str = "airplanes.json", base_dir: str = "data") -> None:
        self.base_dir = base_dir
        self.filename = filename

        # Создаём папку data, если её нет (как в load_data_from_xlsx — не ломаем программу из-за отсутствия папки)
        try:
            os.makedirs(self.base_dir, exist_ok=True)
        except OSError as e:
            raise RuntimeError(f"Не удалось создать директорию '{self.base_dir}': {e}") from e

        self.filepath = os.path.join(self.base_dir, self.filename)
        self._data: List[dict] = []
        self._load()

    def _load(self) -> None:
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                self._data = json.load(f)
            if not isinstance(self._data, list):
                self._data = []
        except FileNotFoundError:
            self._data = []
        except json.JSONDecodeError:
            print(f"[Предупреждение] Файл '{self.filepath}' повреждён или невалидный JSON. Начинаем с пустого хранилища.")
            self._data = []

    def _save(self) -> None:
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(self._data, f, ensure_ascii=False, indent=2)

    def add_airplane(self, airplane: Airplane) -> None:
        for item in self._data:
            if item.get("icao24") == airplane.icao24:
                return
        self._data.append(airplane.to_dict())
        self._save()

    def add_airplanes(self, airplanes: List[Airplane]) -> None:
        for a in airplanes:
            self.add_airplane(a)

    def get_all(self) -> List[Airplane]:
        return [Airplane.from_dict(item) for item in self._data]

    def get_by_country(self, country: str) -> List[Airplane]:
        country_lower = country.lower()
        return [
            Airplane.from_dict(item)
            for item in self._data
            if item.get("origin_country", "").lower() == country_lower
        ]

    def remove_by_icao24(self, icao24: str) -> bool:
        initial_len = len(self._data)
        self._data = [item for item in self._data if item.get("icao24") != icao24]
        changed = len(self._data) != initial_len
        if changed:
            self._save()
        return changed

    def clear_all(self) -> None:
        self._data = []
        self._save()


# Заглушки для других форматов (CSV/Excel/TXT) — без изменений
class CsvStorage(StorageConnector):
    def __init__(self, filepath: str = "airplanes.csv") -> None:
        self.filepath = filepath
    def add_airplane(self, airplane: Airplane) -> None: raise NotImplementedError("CSV-реализация не готова")
    def add_airplanes(self, airplanes: List[Airplane]) -> None: raise NotImplementedError("CSV-реализация не готова")
    def get_all(self) -> List[Airplane]: raise NotImplementedError("CSV-реализация не готова")
    def get_by_country(self, country: str) -> List[Airplane]: raise NotImplementedError("CSV-реализация не готова")
    def remove_by_icao24(self, icao24: str) -> bool: raise NotImplementedError("CSV-реализация не готова")
    def clear_all(self) -> None: raise NotImplementedError("CSV-реализация не готова")


class ExcelStorage(StorageConnector):
    def __init__(self, filepath: str = "airplanes.xlsx") -> None:
        self.filepath = filepath
    def add_airplane(self, airplane: Airplane) -> None: raise NotImplementedError("Excel-реализация не готова")
    def add_airplanes(self, airplanes: List[Airplane]) -> None: raise NotImplementedError("Excel-реализация не готова")
    def get_all(self) -> List[Airplane]: raise NotImplementedError("Excel-реализация не готова")
    def get_by_country(self, country: str) -> List[Airplane]: raise NotImplementedError("Excel-реализация не готова")
    def remove_by_icao24(self, icao24: str) -> bool: raise NotImplementedError("Excel-реализация не готова")
    def clear_all(self) -> None: raise NotImplementedError("Excel-реализация не готова")


class TxtStorage(StorageConnector):
    def __init__(self, filepath: str = "airplanes.txt") -> None:
        self.filepath = filepath
    def add_airplane(self, airplane: Airplane) -> None: raise NotImplementedError("TXT-реализация не готова")
    def add_airplanes(self, airplanes: List[Airplane]) -> None: raise NotImplementedError("TXT-реализация не готова")
    def get_all(self) -> List[Airplane]: raise NotImplementedError("TXT-реализация не готова")
    def get_by_country(self, country: str) -> List[Airplane]: raise NotImplementedError("TXT-реализация не готова")
    def remove_by_icao24(self, icao24: str) -> bool: raise NotImplementedError("TXT-реализация не готова")
    def clear_all(self) -> None: raise NotImplementedError("TXT-реализация не готова")
