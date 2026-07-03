from src.airplane import Airplane
from main import get_top_n_by_altitude, filter_by_registration_country


def test_get_top_n_sorting_desc_by_altitude():
    """Сортировка по убыванию высоты: самые высокие — в начале."""
    planes = [
        Airplane("P1", "C1", "RU", 100.0, 5000),
        Airplane("P2", "C2", "RU", 120.0, 15000),
        Airplane("P3", "C3", "RU", 90.0, 10000),
    ]
    top_2 = get_top_n_by_altitude(planes, 2)
    assert [p.icao24 for p in top_2] == ["P2", "P3"]


def test_get_top_n_with_none_altitude():
    """None считается самым низким и идёт в конце (или не попадает в топ)."""
    planes = [
        Airplane("P1", "C1", "RU", 100.0, None),
        Airplane("P2", "C2", "RU", 120.0, 15000),
        Airplane("P3", "C3", "RU", 90.0, 10000),
    ]
    # Топ‑2: P2 и P3; P1 с None не должен попасть
    top_2 = get_top_n_by_altitude(planes, 2)
    assert [p.icao24 for p in top_2] == ["P2", "P3"]


def test_get_top_n_empty_list():
    """Если список пуст — возвращается пустой список."""
    assert get_top_n_by_altitude([], 3) == []


def test_get_top_n_n_greater_than_count():
    """Если запрашиваем больше, чем есть — возвращаются все."""
    planes = [Airplane("P1", "C1", "RU", 100.0, 5000)]
    result = get_top_n_by_altitude(planes, 5)
    assert len(result) == 1
    assert result[0].icao24 == "P1"


def test_filter_by_country_case_insensitive():
    """Фильтрация по стране: регистронезависимая."""
    planes = [
        Airplane("X1", "X1CALL", "Brazil", 200.0, 4000),
        Airplane("X2", "X2CALL", "brazil", 210.0, 4500),
        Airplane("X3", "X3CALL", "Argentina", 220.0, 5000),
    ]
    filtered = filter_by_registration_country(planes, "BRAZIL")
    assert len(filtered) == 2
    assert all(p.origin_country.lower() == "brazil" for p in filtered)


def test_filter_by_country_no_matches():
    """Если страна не найдена — пустой список."""
    planes = [Airplane("Y1", "Y1CALL", "Japan", 230.0, 3000)]
    filtered = filter_by_registration_country(planes, "NonExistentCountry")
    assert filtered == []


def test_filter_by_country_empty_input():
    """Пустой входной список — пустой результат."""
    assert filter_by_registration_country([], "Russia") == []
