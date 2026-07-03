import pytest
from src.airplane import Airplane


def test_airplane_creation_valid():
    """Обычная корректная инициализация."""
    plane = Airplane(
        icao24="A1B2C3",
        callsign="FLY123",
        origin_country="Russia",
        velocity=250.0,
        geo_altitude=10000,
        latitude=55.75,
        longitude=37.61,
        on_ground=False,
        heading=90.0,
        baro_altitude=9800
    )
    assert plane.icao24 == "A1B2C3"
    assert plane.callsign == "FLY123"


def test_airplane_icao24_required_and_non_empty():
    """icao24 — обязательный непустой строковый атрибут."""
    with pytest.raises(ValueError, match="Атрибут icao24 должен быть непустой строкой"):
        Airplane(
            icao24="",
            callsign="TEST",
            origin_country="RU",
            velocity=0.0,
            geo_altitude=0,
            latitude=0.0,
            longitude=0.0,
            on_ground=False,
            heading=0.0,
            baro_altitude=0
        )

    with pytest.raises(ValueError, match="Атрибут icao24 должен быть непустой строкой"):
        Airplane(
            icao24=None,  # type: ignore
            callsign="TEST",
            origin_country="RU",
            velocity=0.0,
            geo_altitude=0,
            latitude=0.0,
            longitude=0.0,
            on_ground=False,
            heading=0.0,
            baro_altitude=0
        )


def test_airplane_callsign_validation():
    """callsign должен быть непустой строкой — проверяем ошибку."""
    with pytest.raises(ValueError, match="Атрибут callsign должен быть непустой строкой"):
        Airplane(
            icao24="X999",
            callsign=None,  # type: ignore
            origin_country="RU",
            velocity=0.0,
            geo_altitude=0,
            latitude=0.0,
            longitude=0.0,
            on_ground=False,
            heading=0.0,
            baro_altitude=0
        )

    with pytest.raises(ValueError, match="Атрибут callsign должен быть непустой строкой"):
        Airplane(
            icao24="X999",
            callsign="",
            origin_country="RU",
            velocity=0.0,
            geo_altitude=0,
            latitude=0.0,
            longitude=0.0,
            on_ground=False,
            heading=0.0,
            baro_altitude=0
        )


def test_airplane_str_representation():
    """Проверка __str__."""
    plane = Airplane("A1B2C3", "FLY123", "Russia", 250.0, 10000, 55.75, 37.61, False, 90.0, 9800)
    s = str(plane)
    assert isinstance(s, str)
    assert "A1B2C3" in s
    assert "FLY123" in s or "Russia" in s


def test_airplane_repr_representation():
    """Проверка __repr__."""
    plane = Airplane("A1B2C3", "FLY123", "RU", 200.0, 8000, 50.0, 30.0, False, 45.0, 7500)
    r = repr(plane)
    assert isinstance(r, str)
    assert "Airplane" in r
    assert "A1B2C3" in r


def test_airplane_equality():
    """Равенство объектов (если реализован __eq__)."""
    p1 = Airplane("A1B2C3", "FLY1", "RU", 200.0, 10000, 0.0, 0.0, False, 0.0, 0)
    p2 = Airplane("A1B2C3", "FLY1", "RU", 200.0, 10000, 0.0, 0.0, False, 0.0, 0)

    if hasattr(Airplane, "__eq__"):
        assert p1 == p2
        assert not (p1 != p2)
    else:
        # Без __eq__ объекты не равны по умолчанию
        assert p1 is not p2


def test_airplane_different_icao_not_equal():
    """Разные icao24 → не равны."""
    p1 = Airplane("A1B2C3", "FLY1", "RU", 200.0, 10000, 0.0, 0.0, False, 0.0, 0)
    p2 = Airplane("D4E5F6", "FLY2", "DE", 210.0, 11000, 0.0, 0.0, True, 0.0, 0)

    if hasattr(Airplane, "__eq__"):
        assert p1 != p2
    else:
        assert p1 is not p2
