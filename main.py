import sys
from typing import List, Optional
from src.air_api import AirspaceAPI
from src.airplane import Airplane
from src.files_red import JsonStorage, StorageConnector


def fetch_planes_from_api(api: AirspaceAPI, country: str) -> List[Airplane]:
    """
    Получает сырые данные из API и превращает их в валидированные объекты Airplane.
    Как в твоих банковских задачах: одна «битая» запись не ломает весь процесс.
    """
    print(f"Запрос самолётов для страны '{country}' из OpenSky...")
    try:
        raw_planes = api.get_aeroplanes_in_country(country)
        print(f"Получено сырых записей от API: {len(raw_planes)}")
    except Exception as e:
        print(f"Ошибка при запросе к API: {e}")
        return []

    planes: List[Airplane] = []
    for r in raw_planes:
        try:
            plane = Airplane.from_raw_state(r)
            planes.append(plane)
        except ValueError as e:
            # Как в load_data_from_xlsx: логируем и идём дальше
            print(f"[Пропущено] Ошибка валидации самолёта: {e}")

    print(f"Успешно создано валидных объектов Airplane: {len(planes)}")
    return planes


def save_planes_to_storage(storage: StorageConnector, planes: List[Airplane]) -> None:
    """Сохраняет список самолётов в хранилище (абстрактный коннектор)."""
    if not planes:
        print("Нет самолётов для сохранения.")
        return
    storage.add_airplanes(planes)
    print(f"Сохранено {len(planes)} самолётов в хранилище '{storage.__class__.__name__}'.")


def get_top_n_by_altitude(planes: List[Airplane], n: int) -> List[Airplane]:
    """
    Возвращает топ‑N самолётов по геометрической высоте.
    None трактуется как «неизвестно» и считается ниже всех.
    Сортировка устойчивая, порядок среди равных высот сохраняется.
    """

    def altitude_key(p: Airplane):
        # Если высоты нет — считаем её минимально возможной
        return p.geo_altitude if p.geo_altitude is not None else -1

    # sorted по убыванию высоты
    return sorted(planes, key=altitude_key, reverse=True)[:n]


def filter_by_registration_country(planes: List[Airplane], country: str) -> List[Airplane]:
    """Фильтрует самолёты по стране регистрации (регистронезависимо)."""
    country_lower = country.lower()
    return [p for p in planes if p.origin_country.lower() == country_lower]


def print_planes(planes: List[Airplane]) -> None:
    if not planes:
        print("Самолётов для отображения нет.")
        return

    for i, p in enumerate(planes, start=1):
        print(f"{i}. {p}")


def user_interaction(storage: StorageConnector) -> None:
    """
    Функция взаимодействия с пользователем через консоль.
    Реализует требуемый функционал + дополнительные удобные возможности.
    """
    api = AirspaceAPI(user_agent="flight-tracker-cli/1.0")

    while True:
        print("\n--- МЕНЮ ---")
        print("1. Получить самолёты по стране из OpenSky и сохранить в хранилище")
        print("2. Показать топ‑N самолётов по высоте полёта")
        print("3. Показать самолёты по стране регистрации")
        print("4. Показать все самолёты из хранилища")
        print("5. Очистить хранилище")
        print("6. Выход")

        choice = input("Выберите действие (1–6): ").strip()

        if choice == "1":
            country = input("Введите название страны (например, Canada): ").strip()
            if not country:
                print("Название страны не может быть пустым.")
                continue
            planes = fetch_planes_from_api(api, country)
            save_planes_to_storage(storage, planes)

        elif choice == "2":
            try:
                n = int(input("Введите N — количество самолётов для топа по высоте: ").strip())
                if n <= 0:
                    print("N должно быть положительным числом.")
                    continue
            except ValueError:
                print("Некорректное число.")
                continue

            all_planes = storage.get_all()
            top_n = get_top_n_by_altitude(all_planes, n)
            print(f"\nТоп-{n} самолётов по высоте:")
            print_planes(top_n)

        elif choice == "3":
            country = input("Введите страну регистрации для фильтрации: ").strip()
            if not country:
                print("Страна не может быть пустой.")
                continue
            filtered = filter_by_registration_country(storage.get_all(), country)
            print(f"\nСамолёты, зарегистрированные в '{country}':")
            print_planes(filtered)

        elif choice == "4":
            all_planes = storage.get_all()
            print("\nВсе самолёты из хранилища:")
            print_planes(all_planes)

        elif choice == "5":
            confirm = input("Вы уверены, что хотите полностью очистить хранилище? (да/нет): ").strip().lower()
            if confirm == "да":
                storage.clear_all()
                print("Хранилище очищено.")
            else:
                print("Очистка отменена.")

        elif choice == "6":
            print("Выход из программы.")
            break

        else:
            print("Неверный выбор. Пожалуйста, введите число от 1 до 6.")


if __name__ == "__main__":
    # Теперь файл будет создан в папке data/airplanes.json
    storage: StorageConnector = JsonStorage()
    user_interaction(storage)
