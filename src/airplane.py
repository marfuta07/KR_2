from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, List


@dataclass
class Airplane:
    icao24: str
    callsign: str
    origin_country: str
    velocity: float
    geo_altitude: Optional[float]
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    on_ground: Optional[bool] = None
    heading: Optional[float] = None
    baro_altitude: Optional[float] = None

    def __post_init__(self) -> None:
        if not self.icao24 or not isinstance(self.icao24, str):
            raise ValueError("Атрибут icao24 должен быть непустой строкой.")
        if self.callsign is None or (isinstance(self.callsign, str) and not self.callsign.strip()):
            raise ValueError("Атрибут callsign должен быть непустой строкой.")
        if not self.origin_country or not isinstance(self.origin_country, str):
            raise ValueError("Атрибут origin_country должен быть непустой строкой.")
        if self.velocity is None or self.velocity < 0:
            raise ValueError("Атрибут velocity должен быть неотрицательным числом.")
        if self.geo_altitude is not None and (
            not isinstance(self.geo_altitude, (int, float)) or self.geo_altitude < 0
        ):
            raise ValueError("Атрибут geo_altitude должен быть неотрицательным числом или None.")

    @classmethod
    def from_raw_state(cls, raw: dict) -> "Airplane":
        required_keys = ["icao24", "callsign", "origin_country", "velocity", "geo_altitude"]
        missing = [k for k in required_keys if k not in raw]
        if missing:
            raise ValueError(f"В сырых данных отсутствуют обязательные поля: {missing}")

        return cls(
            icao24=raw["icao24"],
            callsign=raw["callsign"],
            origin_country=raw["origin_country"],
            velocity=float(raw["velocity"]) if raw["velocity"] is not None else 0.0,
            geo_altitude=float(raw["geo_altitude"]) if raw["geo_altitude"] is not None else None,
            latitude=float(raw["latitude"]) if raw.get("latitude") is not None else None,
            longitude=float(raw["longitude"]) if raw.get("longitude") is not None else None,
            on_ground=raw.get("on_ground"),
            heading=float(raw["heading"]) if raw.get("heading") is not None else None,
            baro_altitude=float(raw["baro_altitude"]) if raw.get("baro_altitude") is not None else None,
        )

    # Сравнение по скорости (для sorted)
    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Airplane):
            return NotImplemented
        return self.velocity < other.velocity

    # Равенство по уникальному идентификатору
    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Airplane):
            return NotImplemented
        return self.icao24 == other.icao24

    # Сравнение по высоте (явный метод)
    def compare_by_altitude(self, other: "Airplane") -> int:
        if self.geo_altitude is None and other.geo_altitude is None:
            return 0
        if self.geo_altitude is None:
            return -1
        if other.geo_altitude is None:
            return 1
        if self.geo_altitude < other.geo_altitude:
            return -1
        elif self.geo_altitude > other.geo_altitude:
            return 1
        else:
            return 0

    def to_dict(self) -> dict:
        """Сериализация в dict для сохранения в JSON."""
        return {
            "icao24": self.icao24,
            "callsign": self.callsign,
            "origin_country": self.origin_country,
            "velocity": self.velocity,
            "geo_altitude": self.geo_altitude,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "on_ground": self.on_ground,
            "heading": self.heading,
            "baro_altitude": self.baro_altitude,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Airplane":
        """Десериализация из dict (для чтения из JSON)."""
        return cls(**data)

    def __str__(self) -> str:
        status = "на земле" if self.on_ground else "в полёте"
        alt_str = f"{self.geo_altitude:.1f} м" if self.geo_altitude is not None else "высота неизвестна"
        return (
            f"Airplane(ICAO24={self.icao24}, callsign={self.callsign}, "
            f"country={self.origin_country}, velocity={self.velocity:.1f} м/с, "
            f"{alt_str}, статус={status})"
        )
