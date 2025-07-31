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
    """
    Конвертирует время из UTC в локальное время города.

    Args:
        dt_utc (datetime): Временная метка в UTC.
        city_prefix (str): Префикс города ('NSK', 'YR', 'YSP').

    Returns:
        datetime: Локальное время с учётом часового пояса.
    """
    tz_mapping = {
        'NSK': 'Asia/Novosibirsk',
        'YR': 'Asia/Yekaterinburg',
        'YSP': 'Europe/Saint_Petersburg'
    }

    if not dt_utc.tzinfo:
        dt_utc = pytz.UTC.localize(dt_utc)  # Если время наивное, считаем его UTC

    tz = pytz.timezone(tz_mapping.get(city_prefix, 'UTC'))
    return dt_utc.astimezone(tz)


def detect_events(track_points, order_point, city_code, config=None):
    print(f"\nДетекция событий для {len(track_points)} точек")
    print(f"Центр зоны: {order_point}, радиус: {config['event_params']['radius']}м")

    if not track_points:
        print("Нет точек для анализа!")
        return {'arrival': None, 'departure': None, 'confidence': 0}
    if not config:
        config = load_config()

    params = config['event_params']
    radius = params['radius']

    events = []
    in_zone = False
    enter_time = None
    confirmation_start = None

    for i, point in enumerate(track_points):
        distance = haversine(order_point, (point['lat'], point['lon'])) * 1000

        # Проверка вхождения в зону
        if distance <= radius:
            if not in_zone:
                # Первое обнаружение в зоне
                enter_time = point['timestamp']
                confirmation_start = point['timestamp']
                in_zone = True
            else:
                # Подтверждение нахождения в зоне
                if (point['timestamp'] - confirmation_start) >= timedelta(seconds=params['confirmation_time']):
                    events.append({
                        'type': 'arrival',
                        'time_utc': enter_time,  # Оригинальное время в UTC
                        'time_local': ensure_local_time(enter_time, city_code),  # Локальное время
                        'confidence': min(1.0, 1 - (distance / radius))  # 1.0 в центре, уменьшается к краю
                    })
                    in_zone = False
        else:
            if in_zone:
                stop_duration = (point['timestamp'] - enter_time).total_seconds()
                if stop_duration >= params['min_stop_time']:
                    events.append({
                        'type': 'departure',
                        'time': ensure_local_time(point['timestamp'])
                    })
                in_zone = False

    result = {'arrival': None, 'departure': None, 'confidence': 0.0}

    if events:
        arrivals = [e for e in events if e['type'] == 'arrival']
        departures = [e for e in events if e['type'] == 'departure']

        if arrivals:
            best_arrival = max(arrivals, key=lambda x: x['confidence'])
            result['arrival'] = best_arrival['time']
            result['confidence'] = best_arrival['confidence']

            for dep in departures:
                if dep['time'] > best_arrival['time']:
                    result['departure'] = dep['time']
                    break
    print(f"Найдены события: arrival={result['arrival']}, departure={result['departure']}")
    return result

