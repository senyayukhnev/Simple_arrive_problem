import pandas as pd


df = pd.read_csv("data/raw/route_info.csv", sep=';')
print("Столбцы:", df.columns.tolist())  # Добавь эту строку
# Далее — убедись, что имя верное
df['city_prefix'] = df['Trip No_'].str[:3]


