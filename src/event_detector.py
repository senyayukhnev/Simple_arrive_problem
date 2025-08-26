# from haversine import haversine
# import yaml
# from pathlib import Path
# from datetime import timedelta
# import pytz
#
#
# def load_config():
#     config_path = Path(__file__).parent.parent / "config" / "params.yaml"
#     with open(config_path) as f:
#         return yaml.safe_load(f)
#
#
# def ensure_local_time(dt_utc, city_prefix):
#     """
#     Конвертирует время из UTC в локальное время города.
#
#     Args:
#         dt_utc (datetime): Временная метка в UTC.
#         city_prefix (str): Префикс города ('NSK', 'YR', 'YSP').
#
#     Returns:
#         datetime: Локальное время с учётом часового пояса.
#     """
#     tz_mapping = {
#         'NSK': 'Asia/Novosibirsk',
#         'YR': 'Europe/Moscow',
#         'YSP': 'Europe/Moscow'
#     }
#
#     if not dt_utc.tzinfo:
#         dt_utc = pytz.UTC.localize(dt_utc)  # Если время наивное, считаем его UTC
#
#     tz = pytz.timezone(tz_mapping.get(city_prefix, 'UTC'))
#     return dt_utc.astimezone(tz)
#
#
# def detect_events(track_points, order_point, city_code, config=None):
#     print(f"\nДетекция событий для {len(track_points)} точек")
#     print(f"Центр зоны: {order_point}, радиус: {config['event_params']['radius']}м")
#
#     if not track_points:
#         print("Нет точек для анализа!")
#         return {'arrival': None, 'departure': None, 'confidence': 0}
#     if not config:
#         config = load_config()
#
#     params = config['event_params']
#     radius = params['radius']
#
#     events = []
#     in_zone = False
#     enter_time = None
#     confirmation_start = None
#
#     for i, point in enumerate(track_points):
#         distance = haversine(order_point, (float(point['Latitude']), float(point['Longitude']))) * 1000
#
#         # Проверка вхождения в зону
#         if distance <= radius:
#             if not in_zone:
#                 # Первое обнаружение в зоне
#                 enter_time = point['timestamp']
#                 confirmation_start = point['timestamp']
#                 in_zone = True
#             else:
#                 # Подтверждение нахождения в зоне
#                 if (point['timestamp'] - confirmation_start) >= timedelta(seconds=params['confirmation_time']):
#                     events.append({
#                         'type': 'arrival',
#                         'time_utc': enter_time,  # Оригинальное время в UTC
#                         'time_local': ensure_local_time(enter_time, city_code),  # Локальное время
#                         'confidence': min(1.0, 1 - (distance / radius))  # 1.0 в центре, уменьшается к краю
#                     })
#                     in_zone = False
#         else:
#             if in_zone:
#                 stop_duration = (point['timestamp'] - enter_time).total_seconds()
#                 if stop_duration >= params['min_stop_time']:
#                     events.append({
#                         'type': 'departure',
#                         'time': ensure_local_time(point['timestamp'], city_code)
#                     })
#                 in_zone = False
#
#     result = {'arrival': None, 'departure': None, 'confidence': 0.0}
#
#     if events:
#         arrivals = [e for e in events if e['type'] == 'arrival']
#         departures = [e for e in events if e['type'] == 'departure']
#
#         if arrivals:
#             best_arrival = max(arrivals, key=lambda x: x['confidence'])
#             result['arrival'] = best_arrival['time_local']
#             result['confidence'] = best_arrival['confidence']
#
#             for dep in departures:
#                 if dep['time'] > best_arrival['time_local']:
#                     result['departure'] = dep['time']
#                     break
#     print(f"Найдены события: arrival={result['arrival']}, departure={result['departure']}")
#     return result
#
from haversine import haversine
import yaml
from pathlib import Path
from datetime import timedelta
import pytz

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "params.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def ensure_local_time(dt_utc, city_prefix):

    tz_mapping = {
        'NSK': 'Asia/Novosibirsk',
        'YR': 'Europe/Moscow',
        'YSP': 'Europe/Moscow'
    }
    if not dt_utc.tzinfo:
        dt_utc = pytz.UTC.localize(dt_utc)
    tz = pytz.timezone(tz_mapping.get(city_prefix, 'UTC'))
    return dt_utc.astimezone(tz)

def detect_events(track_points, order_point, city_code, config=None):
    print(f"\nДетекция событий для {len(track_points)} точек")
    print(f"Центр зоны: {order_point}, радиус: {config['event_params']['radius']} м")

    if not track_points:
        print("Нет точек для анализа!")
        return {'arrival': None, 'departure': None, 'confidence': 0}

    if not config:
        config = load_config()

    params = config['event_params']
    radius = params['radius']
    confirmation_time = params.get('confirmation_time', 60)  # По умолчанию 60 сек
    max_speed_in_zone = params.get('max_speed_in_zone', float('inf'))
    reentry_window = params.get('reentry_window', 300)  # Окно для проверки reentry (по умолчанию 5 мин)

    events = []
    in_zone = False
    enter_time = None
    last_in_zone_time = None
    arrival_registered = False

    for i, point in enumerate(track_points):
        distance = haversine(order_point, (float(point['Latitude']), float(point['Longitude']))) * 1000
        speed = point.get('speed', 0)
        print(f"Точка {i}: расстояние={distance:.2f} м, скорость={speed:.2f} км/ч, время={point['timestamp']}")

        # Проверка вхождения в зону
        if distance <= radius and speed <= max_speed_in_zone:
            if not in_zone:
                print(f"Вход в зону: {point['timestamp']}")
                enter_time = point['timestamp']
                in_zone = True
            last_in_zone_time = point['timestamp']

            # Регистрация arrival, если транспорт в зоне достаточно долго
            if not arrival_registered and enter_time and (point['timestamp'] - enter_time).total_seconds() >= confirmation_time:
                events.append({
                    'type': 'arrival',
                    'time_utc': enter_time,
                    'time_local': ensure_local_time(enter_time, city_code),
                    'confidence': min(1.0, 1 - (distance / radius))
                })
                print(f"Зарегистрировано arrival: {ensure_local_time(enter_time, city_code)}")
                arrival_registered = True
        else:
            if in_zone:
                stop_duration = (point['timestamp'] - enter_time).total_seconds() if enter_time else 0
                print(f"Выход из зоны: {point['timestamp']}, время в зоне: {stop_duration:.2f} сек")
                if arrival_registered:
                    events.append({
                        'type': 'departure',
                        'time_local': ensure_local_time(last_in_zone_time, city_code),
                        'confidence': min(1.0, 1 - (distance / radius))
                    })
                    print(f"Зарегистрировано departure: {ensure_local_time(last_in_zone_time, city_code)}")
                in_zone = False
                enter_time = None
                last_in_zone_time = None
                arrival_registered = False  # Новое: сброс флага при выходе, чтобы позволить новый arrival при reentry

    # Проверка последнего пребывания в зоне
    if in_zone and last_in_zone_time and arrival_registered:
        stop_duration = (track_points[-1]['timestamp'] - enter_time).total_seconds()
        print(f"Конец трека, время в зоне: {stop_duration:.2f} сек")
        events.append({
            'type': 'departure',
            'time_local': ensure_local_time(last_in_zone_time, city_code),
            'confidence': min(1.0, 1 - (haversine(order_point, (float(track_points[-1]['Latitude']), float(track_points[-1]['Longitude']))) * 1000 / radius))
        })
        print(f"Зарегистрировано departure (конец трека): {ensure_local_time(last_in_zone_time, city_code)}")

    result = {'arrival': None, 'departure': None, 'confidence': 0.0}

    if events:
        arrivals = [e for e in events if e['type'] == 'arrival']
        departures = [e for e in events if e['type'] == 'departure']

        if arrivals:
            best_arrival = max(arrivals, key=lambda x: x['confidence'])
            result['arrival'] = best_arrival['time_local']
            result['confidence'] = best_arrival['confidence']

            # Пост-обработка: ищем истинный departure, игнорируя ложные (с reentry в окне)
            potential_departures = [dep for dep in departures if dep['time_local'] > best_arrival['time_local']]
            dep_index = 0
            while dep_index < len(potential_departures):
                current_dep = potential_departures[dep_index]
                reentry_time_limit = current_dep['time_local'] + timedelta(seconds=reentry_window)

                # Проверяем, есть ли reentry (другой arrival) в следующие 5 мин
                has_reentry = any(
                    arr['time_local'] > current_dep['time_local'] and arr['time_local'] <= reentry_time_limit
                    for arr in arrivals
                )

                if not has_reentry:
                    result['departure'] = current_dep['time_local']
                    result['confidence'] = max(result['confidence'], current_dep['confidence'])
                    break
                dep_index += 1  # Переходим к следующему departure

    print(f"Найдены события: arrival={result['arrival']}, departure={result['departure']}, confidence={result['confidence']:.2f}")
    return result