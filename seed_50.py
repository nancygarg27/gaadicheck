import random
from datetime import date

import pandas as pd
from faker import Faker
from sqlmodel import Session, select

from database import engine
from models import Vehicle, OdometerReading, Owner, Loan, Challan

fake = Faker("en_IN")

CSV_PATH = "data/cardekho_dataset.csv" 
BANKS = ["HDFC Bank", "ICICI Bank", "SBI", "Axis Bank", "Kotak Mahindra"]
STATES = ["MH", "DL", "KA", "HR", "UP", "TN", "GJ", "TS"]
VIOLATIONS = ["over-speeding", "red-light break", "wrong parking", "no seatbelt", "drink and drive"]
SOURCES = ["service", "insurance", "inspection"]


def generate_plate(used):
    while True:
        plate = (
            random.choice(STATES)
            + f"{random.randint(1, 99):02d}"
            + chr(random.randint(65, 90))
            + chr(random.randint(65, 90))
            + str(random.randint(1000, 9999))
        )
        if plate not in used:
            used.add(plate)
            return plate


def make_clean_readings(final_km, age, purchase_year):
    readings = []
    prev = 0
    for i in range(1, age + 1):
        km = int(final_km * i / age)
        if i < age:
            km += random.randint(-300, 300)
            km = max(km, prev + 100)  # kabhi ulta nahi
        readings.append([date(purchase_year + i, random.randint(1, 12), random.randint(1, 28)), km])
        prev = km

    readings.sort(key=lambda r: r[0])
    return readings


def apply_scenario(readings, scenario):
    n = len(readings)
    if scenario == "rollback" and n >= 3:
        readings[-1][1] = int(readings[-2][1] * random.uniform(0.5, 0.85))
    
    elif scenario == "flatline" and n >= 4:
        base = readings[-4][1]
        for j in range(-3, 0):
            base += random.randint(50, 300)
            readings[j][1] = base
    
    elif scenario == "jump" and n >= 3:
        prev_date, prev_km = readings[-2]
        readings[-1][0] = date(prev_date.year, prev_date.month, min(prev_date.day + 20, 28))
        readings[-1][1] = prev_km + random.randint(20000, 45000)
    
    return readings


def main():
    df = pd.read_csv(CSV_PATH)
    df = df[(df["vehicle_age"] >= 4) & (df["vehicle_age"] <= 10)].copy()
    df = df[df["km_driven"] / df["vehicle_age"] < 40000]

    scenarios = ["clean"] * 35 + ["rollback"] * 5 + ["flatline"] * 5 + ["jump"] * 5
    random.shuffle(scenarios)
    used_plates = set(session_plates()) if False else set()

    with Session(engine) as session:
        used_plates = set(session.exec(select(Vehicle.plate_number)).all())

        for scenario in scenarios:
            row = df.sample(1).iloc[0]
            age = int(row["vehicle_age"])
            year = 2026 - age

            car = Vehicle(
                plate_number=generate_plate(used_plates),
                company=row["brand"],
                model=row["model"],
                year=year,
                fuel_type=row["fuel_type"].lower(),
                scenario_label=scenario,
            )
            session.add(car)
            session.commit()
            session.refresh(car)

            readings = make_clean_readings(int(row["km_driven"]), age, year)
            readings = apply_scenario(readings, scenario)
            for d, km in readings:
                session.add(OdometerReading(
                    vehicle_id=car.id, reading_date=d, distance_km=km,
                    source=random.choice(SOURCES),
                ))

            session.add(Owner(
                vehicle_id=car.id, owner_name=fake.name(), city=fake.city(),
                owned_from_date=date(year, random.randint(1, 6), random.randint(1, 28)),
                owned_to_date=None,
            ))

            if random.random() < 0.3:
                session.add(Loan(
                    vehicle_id=car.id, bank_name=random.choice(BANKS),
                    loan_amount=random.choice([300000, 500000, 700000, 800000]),
                    is_active=random.choice([True, False]),
                ))

            if random.random() < 0.25:
                session.add(Challan(
                    vehicle_id=car.id,
                    challan_date=date(random.choice([2022, 2023, 2024, 2025]), random.randint(1, 12), random.randint(1, 28)),
                    amount_of_fine=random.choice([500, 1000, 1500, 2000]),
                    reason_of_challan=random.choice(VIOLATIONS),
                    is_paid=random.choice([True, False]),
                ))

            session.commit()

    print("50 cars added.")


if __name__ == "__main__":
    main()