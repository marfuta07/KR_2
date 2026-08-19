import pytest
from src.airplane import Airplane
from src.files_red import JsonStorage, StorageConnector
from main import get_top_n_by_altitude, filter_by_registration_country
from typing import Generator, List
from pathlib import Path

@pytest.fixture
def tmp_storage(tmp_path: Path) -> Generator[StorageConnector, None, None]:
    """
    Фикстура: создаёт чистое хранилище во временной папке.
    Гарантирует, что каждый тест начинается с пустого JSON и пустой памяти.
    """
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Создаём объект БЕЗ аргументов (как требует конструктор JsonStorage)
    storage = JsonStorage()

    # Подменяем атрибуты, чтобы писать в тестовую временную папку
    storage.filename = "test_planes.json"
    storage.base_dir = str(data_dir)

    # ВАЖНО: сразу очищаем хранилище, чтобы не было мусора от предыдущих запусков
    # Это решает проблему, когда в списке оказывалось 3 объекта вместо 1
    storage.clear_all()

    yield storage


def test_airplane_validation_raises_on_empty_callsign()->None:
    """Валидация: пустой callsign должен вызывать ValueError."""
    with pytest.raises(ValueError, match="callsign"):
        Airplane(
            icao24="TEST123",
            callsign="",
            origin_country="Russia",
            velocity=200.0,
            geo_altitude=10000,
        )


def test_airplane_validation_allows_none_altitude()->None:
    """Валидация: geo_altitude может быть None."""
    plane = Airplane(
        icao24="TEST456",
        callsign="FLY",
        origin_country="Germany",
        velocity=250.0,
        geo_altitude=None,
    )
    assert plane.geo_altitude is None


def test_json_storage_add_and_get(tmp_storage: StorageConnector)->None:
    """Добавление и получение самолётов работают корректно."""
    p1 = Airplane("A1", "CALL1", "USA", 300.0, 11000)
    p2 = Airplane("A2", "CALL2", "Canada", 280.0, 9000)

    # Используем add_airplane (обёртка), который внутри вызывает add_airplanes
    tmp_storage.add_airplane(p1)
    tmp_storage.add_airplane(p2)

    all_planes = tmp_storage.get_all()
    assert len(all_planes) == 2
    assert any(p.icao24 == "A1" for p in all_planes)
    assert any(p.icao24 == "A2" for p in all_planes)


def test_json_storage_duplicate_prevention(tmp_storage: StorageConnector)->None:
    """Защита от дублей по icao24 работает."""
    p = Airplane("DUPE", "DUPECALL", "UK", 200.0, 8000)

    tmp_storage.add_airplane(p)
    tmp_storage.add_airplane(p)  # Повторное добавление того же объекта

    # Должен остаться только 1 уникальный самолёт
    assert len(tmp_storage.get_all()) == 1


def test_json_storage_remove_and_clear(tmp_storage: StorageConnector)->None:
    """Удаление по icao24 и полная очистка работают."""
    p = Airplane("REMOVE", "REMOVECALL", "France", 220.0, 7000)
    tmp_storage.add_airplane(p)

    removed = tmp_storage.remove_by_icao24("REMOVE")
    assert removed is True
    assert len(tmp_storage.get_all()) == 0

    # Проверка clear_all
    p2 = Airplane("CLEAR", "CLEARCALL", "Italy", 210.0, 6000)
    tmp_storage.add_airplane(p2)
    tmp_storage.clear_all()
    assert len(tmp_storage.get_all()) == 0


def test_top_n_sorting_desc_by_altitude()->None:
    """Топ‑N по высоте: сортировка по убыванию, None считается самым низким."""
    planes = [
        Airplane("P1", "C1", "Spain", 100.0, 5000),
        Airplane("P2", "C2", "Spain", 120.0, 15000),
        Airplane("P3", "C3", "Spain", 90.0, None),  # None — самый низкий
        Airplane("P4", "C4", "Spain", 110.0, 10000),
    ]

    top_2 = get_top_n_by_altitude(planes, 2)
    # Должны быть P2 (15000) и P4 (10000)
    assert [p.icao24 for p in top_2] == ["P2", "P4"]


def test_filter_by_country_case_insensitive()->None:
    """Фильтрация по стране: регистронезависимая."""
    planes = [
        Airplane("X1", "X1CALL", "Brazil", 200.0, 4000),
        Airplane("X2", "X2CALL", "brazil", 210.0, 4500),
        Airplane("X3", "X3CALL", "Argentina", 220.0, 5000),
    ]

    filtered = filter_by_registration_country(planes, "BRAZIL")
    assert len(filtered) == 2
    assert all(p.origin_country.lower() == "brazil" for p in filtered)


def test_empty_filter_returns_empty_list()->None:
    """Фильтрация: если страна не найдена, возвращается пустой список."""
    planes = [Airplane("Y1", "Y1CALL", "Japan", 230.0, 3000)]
    filtered = filter_by_registration_country(planes, "NonExistentCountry")
    assert filtered == []
