import pandas as pd

def load_routes(path):
    df = pd.read_csv(path, sep=';')
    df['city_prefix'] = df['Trip No_'].apply(lambda x: x[:2] if x.startswith('YR') else x[:3])
    df['route_code'] = df['Trip No_'].apply(lambda x: x[2:] if x.startswith('YR') else x[3:])
    df['Delivery Fact Time'] = pd.to_datetime(df['Delivery Fact Time'], utc=True)
    valid_statuses = [0, 4, 5, 6]
    return df[df['Status'].isin(valid_statuses)]


def load_tracks(path):
    """
    Загружает и подготавливает данные треков из track_info.csv.
    Сортирует по Timestamp и группирует по route_code.

    Args:
        path (str): Путь к файлу track_info.csv.

    Returns:
        pd.core.groupby.DataFrameGroupBy: Сгруппированные треки по route_code, отсортированные по Timestamp.
    """
    df = pd.read_csv(path, sep=';')
    # Проверка наличия необходимых колонок
    required_columns = ['RouteCode', 'Latitude', 'Longitude', 'Timestamp']
    if not all(col in df.columns for col in required_columns):
        missing = [col for col in required_columns if col not in df.columns]
        raise ValueError(f"Отсутствуют столбцы в track_info.csv: {missing}")

    # Удаление строк с пропущенными значениями
    df = df.dropna(subset=required_columns)

    # Преобразование Timestamp в datetime
    df['timestamp'] = pd.to_datetime(df['Timestamp'], errors='coerce')
    df = df.dropna(subset=['timestamp'])

    # Извлечение city_prefix и route_code
    df['city_prefix'] = df['RouteCode'].apply(lambda x: x[:2] if x.startswith('YR') else x[:3] if len(x) >= 3 else '')
    df['route_code'] = df['RouteCode'].apply(lambda x: x[2:] if x.startswith('YR') else x[3:] if len(x) >= 3 else '')

    # Сортировка по timestamp и группировка по route_code
    df = df.sort_values('timestamp')
    grouped_tracks = df.groupby('route_code')

    print(f"Загружено {len(df)} треков, сгруппировано по {len(grouped_tracks.groups)} маршрутам")
    for route_code, group in grouped_tracks:
        print(f"Маршрут {route_code}: {len(group)} точек")

    return grouped_tracks