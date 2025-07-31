import pandas as pd
from datetime import datetime
from src.data_loader import load_routes, load_tracks
from src.gps_processor import filter_gps_points
from src.event_detector import detect_events


# from src.utils.time_utils import convert_to_utc

def run_pipeline(config):
    print("Downloading and Preprocessing Data...")
    routes = load_routes(config['data_paths']['route_info'])
    tracks = load_tracks(config['data_paths']['track_info'])

    print("Grouping tracks...")
    grouped_tracks = tracks.groupby('RouteCode')
    print("Уникальные route_code в routes:", routes['route_code'].unique()[:5])
    print("Уникальные route_code в tracks:", tracks['route_code'].unique()[:5])
    results = []
    processed_routes = 0
    for _, route in routes.iterrows():
        route_code = route['route_code']
        order_point = (route['Delivery Order Lat'], route['Delivery Order Lon'])

        print(f"\nОбработка {route_code}...")
        print(f"Координаты заказа: {order_point}")
        if route_code in grouped_tracks.groups:
            track_points = grouped_tracks.get_group(route_code).to_dict('records')
            clean_points = filter_gps_points(
                track_points
                ** config['gps_params']
            )
            order_point = (route['Delivery Order Lat'], route['Delivery Order Lon'])
            events = detect_events(
                clean_points,
                order_point,
                city_code=route['city_prefix'],
                config=config
            )

            results.append({'order_id': route['Source No_'],
                            'customer_id': route['Customer No_'],
                            'arrival_utc': events['arrival'],
                            'departure_utc': events['departure'],
                            'confidence': events['confidence'],
                            'route_code': route_code,
                            })
            processed_routes += 1

    result_df = pd.DataFrame(results)
    print(f"\nИтоговая статистика:")
    print(f"Обработано маршрутов: {processed_routes}/{len(routes)}")
    print(f"Найдено событий: {len(result_df)}")
    if config.get('output_path'):
        if len(results) == 0:
            print("Предупреждение: Нет данных для сохранения!")
            print("Последний обработанный route:", route)
            #print("Количество точек в треке:", len(track_points))
        else:
            result_df.to_csv(config['output_path'], index=False)
        print(f"Wrote to {config['output_path']}")

    return result_df


if __name__ == "__main__":
    import yaml

    with open("config\params.yaml") as f:
        config = yaml.safe_load(f)

    results = run_pipeline(config)
    print(results.head())
