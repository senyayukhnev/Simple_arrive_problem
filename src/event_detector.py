from haversine import haversine
import yaml
from pathlib import Path
from datetime import timedelta

def load_config():
    config_path = Path(__file__).parent.parent / "config" / "params.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)

def detect_events(track_points, order_point, city_code, config=None):
    