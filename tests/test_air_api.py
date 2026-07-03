import pytest
from unittest.mock import patch
from src.air_api import AirspaceAPI


@pytest.fixture
def mock_response_json():
    """Возвращает JSON, который реально приходит от Nominatim (список объектов)."""
    return [{"boundingbox": ["50.0", "60.0", "30.0", "40.0"], "display_name": "Russia", "type": "country"}]


@pytest.fixture
def mock_opensky_states():
    """
    Сырые данные от OpenSky: список списков.
    Формат: [icao24, callsign, origin_country, time_position, last_contact,
            longitude, latitude, baro_altitude, on_ground, velocity, heading,
            vertical_rate, ..., geo_altitude, ...]
    """
    return [
        [
            "A1B2C3",
            "FLY123",
            "Russia",
            1700000000,
            1700000100,
            37.61,
            55.75,
            10000.0,
            False,
            250.0,
            90.0,
            -5.0,
            None,
            9800.0,
            None,
            None,
            0,
        ],
        [
            "D4E5F6",
            "FLY456",
            "Germany",
            1700000200,
            1700000300,
            13.40,
            52.52,
            11000.0,
            True,
            270.0,
            180.0,
            0.0,
            None,
            None,
            None,
            None,
            1,
        ],
    ]


# --- Тесты валидации User-Agent (как валидация в Product.__init__) ---


def test_airspace_api_invalid_user_agent_empty():
    with pytest.raises(ValueError, match="не должен содержать пробелов и не может быть пустым"):
        AirspaceAPI(user_agent="")


def test_airspace_api_invalid_user_agent_with_space():
    with pytest.raises(ValueError, match="не должен содержать пробелов и не может быть пустым"):
        AirspaceAPI(user_agent="flight tracker")


def test_airspace_api_valid_user_agent():
    api = AirspaceAPI(user_agent="my-app/1.0")
    assert api.user_agent == "my-app/1.0"
    assert "User-Agent" in api._headers


# --- Тесты get_country_boundingbox ---


@patch.object(AirspaceAPI, "_request_json")
def test_get_country_boundingbox_success(mock_request):
    mock_request.return_value = [{"boundingbox": ["10.0", "20.0", "30.0", "40.0"]}]
    api = AirspaceAPI("test-app/1.0")
    bbox = api.get_country_boundingbox("Russia")

    assert bbox == [10.0, 20.0, 30.0, 40.0]
    mock_request.assert_called_once()


@patch.object(AirspaceAPI, "_request_json")
def test_get_country_boundingbox_empty_response(mock_request):
    mock_request.return_value = []
    api = AirspaceAPI("test-app/1.0")
    assert api.get_country_boundingbox("UnknownCountry") is None


@patch.object(AirspaceAPI, "_request_json")
def test_get_country_boundingbox_invalid_bbox_format(mock_request):
    # boundingbox есть, но не 4 элемента
    mock_request.return_value = [{"boundingbox": ["1", "2", "3"]}]
    api = AirspaceAPI("test-app/1.0")
    assert api.get_country_boundingbox("BadCountry") is None


# --- Тесты get_airplanes_in_bounds (распаковка сырых данных) ---


@patch.object(AirspaceAPI, "_request_json")
def test_get_airplanes_in_bounds_parsing(mock_request, mock_opensky_states):
    mock_request.return_value = {"states": mock_opensky_states}
    api = AirspaceAPI("test-app/1.0")
    planes = api.get_airplanes_in_bounds(50.0, 60.0, 30.0, 40.0)

    assert len(planes) == 2
    p1 = planes[0]
    assert p1["icao24"] == "A1B2C3"
    assert p1["callsign"] == "FLY123"
    assert p1["origin_country"] == "Russia"
    assert p1["latitude"] == 55.75
    assert p1["longitude"] == 37.61
    assert p1["geo_altitude"] == 9800.0
    assert isinstance(p1["on_ground"], bool)  # важно: должно быть bool, а не int/None


@patch.object(AirspaceAPI, "_request_json")
def test_get_airplanes_in_bounds_empty_states(mock_request):
    mock_request.return_value = {"states": []}
    api = AirspaceAPI("test-app/1.0")
    assert api.get_airplanes_in_bounds(0, 1, 0, 1) == []


@patch.object(AirspaceAPI, "_request_json")
def test_get_airplanes_in_bounds_invalid_state_format(mock_request):
    # state — не список или слишком короткий
    mock_request.return_value = {"states": [["short"]]}
    api = AirspaceAPI("test-app/1.0")
    result = api.get_airplanes_in_bounds(0, 1, 0, 1)
    assert result == []  # некорректные строки пропускаются


# --- Тест обёртки get_aeroplanes_in_country ---


@patch.object(AirspaceAPI, "get_country_boundingbox")
@patch.object(AirspaceAPI, "get_airplanes_in_bounds")
def test_get_aeroplanes_in_country_success(mock_bounds, mock_bbox):
    mock_bbox.return_value = [50.0, 60.0, 30.0, 40.0]
    expected_planes = [{"icao24": "TEST"}]
    mock_bounds.return_value = expected_planes

    api = AirspaceAPI("test-app/1.0")
    result = api.get_aeroplanes_in_country("Russia")

    assert result == expected_planes
    mock_bbox.assert_called_once_with("Russia")
    mock_bounds.assert_called_once_with(50.0, 60.0, 30.0, 40.0)


@patch.object(AirspaceAPI, "get_country_boundingbox")
def test_get_aeroplanes_in_country_bbox_not_found(mock_bbox):
    mock_bbox.return_value = None
    api = AirspaceAPI("test-app/1.0")

    with pytest.raises(ValueError, match="Не удалось получить координаты для страны"):
        api.get_aeroplanes_in_country("NoSuchCountry")


# --- Тесты обработки ошибок сети (_request_json) ---


@patch("src.air_api.requests.get")
def test_request_json_network_error(mock_get):
    from requests.exceptions import RequestException

    mock_get.side_effect = RequestException("Connection failed")
    api = AirspaceAPI("test-app/1.0")

    with pytest.raises(RequestException, match="Ошибка запроса к https://nominatim.openstreetmap.org/search"):
        api._request_json("https://nominatim.openstreetmap.org/search")
