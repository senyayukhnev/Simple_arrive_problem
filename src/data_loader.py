import pandas as pd


def load_routes(path):
    df = pd.read_csv(path, sep=';')
    df['city_prefix'] = df['Trip No_'].str[:3]
    df['route_code'] = df['Trip No_'].str[3:]
    df['Delivery Fact Time'] = pd.to_datetime(df['Delivery Fact Time'], utc=True)
    valid_statuses = [0, 4, 5, 6]
    return df[df['Status'].isin(valid_statuses)]

def load_tracks(path):
    df = pd.read_csv(path, sep=';')
    df['city_prefix'] = df['RouteCode'].str[:3]
    df['route_code'] = df['RouteCode'].str[3:]
    df['timestamp'] = pd.to_datetime(df['Timestamp'])
    df.drop('PosDate', axis=1, inplace=True)
    return df
