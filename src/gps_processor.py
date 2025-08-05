from datetime import datetime
import yaml
from collections import defaultdict
from haversine import haversine
from pathlib import Path
import numpy as np
from sklearn.cluster import DBSCAN

def load_gps_config():
    config_path = Path(__file__).parent.parent / "config" / "params.yaml"
    with open(config_path) as f:
        config = yaml.safe_load(f)
    return config["gps_params"]


def filter_gps_points(points, max_speed=None, max_accel=None, min_cluster_ratio=None, warmup_points=None,
                      stability_threshold=None):
    """
    :param points: list[dict] - Список точек с ключами ['lat', 'lon', 'timestamp']
    """
    print(f"\nФильтрация {len(points)} точек с параметрами:")
    print(f"max_speed={max_speed}, min_cluster_ratio={min_cluster_ratio}")
    if any(p is None for p in [max_speed, max_accel, min_cluster_ratio, warmup_points, stability_threshold]):
        config = load_gps_config()
        max_speed = config["max_speed"] or max_speed
        max_accel = config["max_accel"] or max_accel
        min_cluster_ratio = config["min_cluster_ratio"] or min_cluster_ratio
        warmup_points = config["warmup_points"] or warmup_points
        stability_threshold = config["stability_threshold"] or stability_threshold

    if not points:
        print("Нет точек для фильтрации!")
        return []
    #points = sorted(points, key=lambda x: x['timestamp'])
    init_cluster = _find_initial_cluster(
        points[:warmup_points],
        min_cluster_ratio,
        stability_threshold
    )
    if not init_cluster:
        return []

    valid_points = []
    for i in range(1, len(points)):
        prev = points[i-1]
        curr = points[i]

        dist = haversine((float(prev['Latitude']), float(prev['Longitude'])), (float(curr['Latitude']), float(curr['Longitude']))) * 1000
        time_diff = (curr['timestamp'] - prev['timestamp']).total_seconds()
        if time_diff > 0:
            speed = (dist / time_diff) * 3.6
            accel = abs(speed - prev.get('accel', 0)) / time_diff if time_diff > 0 else 0
            if speed <= max_speed and accel <= max_accel:
                curr['speed'] = speed
                valid_points.append(curr)
    return init_cluster + valid_points

def _find_initial_cluster(points, min_cluster_ratio, stability_threshold):
    if len(points) < stability_threshold:
        return None
    clusters = defaultdict(list)
    for p in points:
        key = (round(float(p['Latitude']), 4), round(float(p['Longitude']), 4))
        clusters[key].append(p)
    if clusters:
        main_cluster = max(clusters.values(), key=len)
        if len(main_cluster) / len(points) >= min_cluster_ratio:
            return main_cluster
    return None