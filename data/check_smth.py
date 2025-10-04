import pandas as pd


df = pd.read_csv("data/raw/route_info.csv", sep=';')
print("Столбцы:", df.columns.tolist())  # Добавь эту строку
# Далее — убедись, что имя верное
df['city_prefix'] = df['Trip No_'].str[:3]
print(df['Trip No_'].str[:3])

# 1-6. 8:50 9:28
# 7-9. 10:06 10:30
# 10. 10:38 10:50
# 11-20. 11:01 11:21
# 21-23. 11:25 11:48
# 24. 11:49 12:04
# 25. 12:28 12:34
# 26. 12:38 13:00
# 27. 13:08 13:30
# 28. 13:31 13:42



