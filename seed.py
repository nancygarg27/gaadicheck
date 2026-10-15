from sqlmodel import Session
from datetime import date
from database import engine
from models import Vehicle, OdometerReading

with Session(engine) as session:
    car3 = Vehicle(plate_number = "UP14BK4821", company = "Tata", model = "Nexon", year = 2019, fuel_type = "diesel", scenario_label = "rollback")
    session.add(car3)
    session.commit()
    session.refresh(car3)

    session.add(OdometerReading(vehicle_id = car3.id, reading_date = date(2019, 8, 12), distance_km = 400, source = "inspection"))
    session.add(OdometerReading(vehicle_id = car3.id, reading_date = date(2020, 9, 18), distance_km = 13600, source = "service"))
    session.add(OdometerReading(vehicle_id = car3.id, reading_date = date(2021, 10, 5), distance_km = 27900, source = "service"))
    session.add(OdometerReading(vehicle_id = car3.id, reading_date = date(2022, 11, 14), distance_km = 42300, source = "insurance"))
    session.add(OdometerReading(vehicle_id = car3.id, reading_date = date(2023, 12, 2), distance_km = 56800, source = "service"))
    session.add(OdometerReading(vehicle_id = car3.id, reading_date = date(2024, 12, 20), distance_km = 31500, source = "inspection"))
    session.commit()