import pandas as pd


def load_routes(path):
    df = pd.read_csv(path)
    df['Delivery Fact Time'] = pd.to_datetime(df['Delivery Fact Time'], utc=True)
    valid_statuses = [0, 4, 5, 6]
    return df[df['Status'].isin(valid_statuses)]

def load_tracks(path):
    df = pd.read_csv(path)
    df['timestamp'] = pd.to_datetime(df['Timestamp'])
    df.drop('PosDate', axis=1, inplace=True)
    return df
