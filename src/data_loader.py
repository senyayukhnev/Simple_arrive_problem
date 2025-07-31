import pandas as pd

def load_routes(path):
    df = pd.read_csv(path, sep=';')
    df['city_prefix'] = df['Trip No_'].apply(lambda x: x[:2] if x.startswith('YR') else x[:3])
    df['route_code'] = df['Trip No_'].apply(lambda x: x[2:] if x.startswith('YR') else x[3:])
    df['Delivery Fact Time'] = pd.to_datetime(df['Delivery Fact Time'], utc=True)
    valid_statuses = [0, 4, 5, 6]
    return df[df['Status'].isin(valid_statuses)]

def load_tracks(path):
    df = pd.read_csv(path, sep=';')
    df['city_prefix'] = df['RouteCode'].apply(lambda x: x[:2] if x.startswith('YR') else x[:3])
    df['route_code'] = df['RouteCode'].apply(lambda x: x[2:] if x.startswith('YR') else x[3:])
    df['timestamp'] = pd.to_datetime(df['Timestamp'])
    df.drop('PosDate', axis=1, inplace=True)
    return df