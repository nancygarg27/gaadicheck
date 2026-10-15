from sqlmodel import Session
from datetime import date
from database import engine
from models import Vehicle, OdometerReading

with Session(engine) as session:
    car5 = Vehicle(plate_number = "GJ05EF2917", company = "Mahindra", model = "XUV300", year = 2018, fuel_type = "diesel", scenario_label = "flatline")
    session.add(car5)
    car6 = Vehicle(plate_number = "KA03MN6642", company = "Toyota", model = "Innova", year = 2016, fuel_type = "diesel", scenario_label = "jump")
    session.add(car6)
    session.commit()
    session.refresh(car5)
    session.refresh(car6)

    session.add(OdometerReading(vehicle_id = car5.id, reading_date = date(2018, 4, 12), distance_km = 450, source = "inspection"))
    session.add(OdometerReading(vehicle_id = car5.id, reading_date = date(2019, 5, 20), distance_km = 12900, source = "service"))
    session.add(OdometerReading(vehicle_id = car5.id, reading_date = date(2020, 6, 18), distance_km = 25600, source = "service"))
    session.add(OdometerReading(vehicle_id = car5.id, reading_date = date(2021, 7, 9), distance_km = 38200, source = "insurance"))
    session.add(OdometerReading(vehicle_id = car5.id, reading_date = date(2022, 8, 14), distance_km = 38350, source = "service"))
    session.add(OdometerReading(vehicle_id = car5.id, reading_date = date(2023, 9, 21), distance_km = 38420, source = "service"))
    session.add(OdometerReading(vehicle_id = car5.id, reading_date = date(2024, 10, 5), distance_km = 38500, source = "inspection"))
    session.add(OdometerReading(vehicle_id = car6.id, reading_date = date(2016, 3, 15), distance_km = 700, source = "inspection"))
    session.add(OdometerReading(vehicle_id = car6.id, reading_date = date(2017, 4, 22), distance_km = 14200, source = "service"))
    session.add(OdometerReading(vehicle_id = car6.id, reading_date = date(2018, 5, 30), distance_km = 28100, source = "service"))
    session.add(OdometerReading(vehicle_id = car6.id, reading_date = date(2019, 6, 12), distance_km = 41500, source = "insurance"))
    session.add(OdometerReading(vehicle_id = car6.id, reading_date = date(2019, 7, 10), distance_km = 82300, source = "service"))
    session.add(OdometerReading(vehicle_id = car6.id, reading_date = date(2020, 8, 18), distance_km = 95800, source = "service"))   
    session.commit()