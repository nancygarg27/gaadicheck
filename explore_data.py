import pandas as pd
import random
from datetime import date

df = pd.read_csv("data/cardekho_dataset.csv")
df = df[df["vehicle_age"] > 0]

row = df.sample(1).iloc[0]

company = row["brand"]
model = row["model"]
age = int(row["vehicle_age"])
year = 2026- row["vehicle_age"]
fuel = row["fuel_type"].lower()
final_km = int(row["km_driven"])

def make_clean_readings(final_km, age, purchase_year):
    readings=[]

    for i in range(1, age+1):
        km = int(final_km*i)/age
        if i < age:
            km += random.randint(-500, 500)
            km = max(km,0)
            readings.append((date(purchase_year + i, 6, 15), km))
    return readings

readings = make_clean_readings(final_km, age, year)
print(readings)