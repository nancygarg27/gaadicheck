import pandas as pd
from sqlmodel import select, Session
from database import engine
from models import OdometerReading, Vehicle

FLATLINE_MIN_DAYS = 180
FLATLINE_MAX_KM = 500
JUMP_MAX_DAYS = 60
JUMP_MIN_KM = 10000

def get_vehicle_id_by_plate_number(plate):
    plate = plate.upper()
    plate = plate.replace(" ", "")
    with Session(engine) as session:
        vehicle_id = session.exec(select(Vehicle.id).where(Vehicle.plate_number == plate)).first()
    return vehicle_id

def get_vehicle_details(vehicle_id):
    with Session(engine) as session:
        row_data= session.get(Vehicle, vehicle_id)
        return row_data

def get_readings(vehicle_id):
    with Session(engine) as session:
        statement = select(OdometerReading).where(OdometerReading.vehicle_id == vehicle_id)
        rows = session.exec(statement).all()
        data = []
        for r in rows :
            data.append({"date" : r.reading_date, "km" : r.distance_km, "source" : r.source})  
        df = pd.DataFrame(data)
        df= df.sort_values("date")
        return df


def find_rollback(df):
    df["km_change"]= df["km"].diff()
    df["is_rollback"] = df["km_change"] < 0
    return df

def find_flatline(df):
    df["days_gap"]= pd.to_datetime(df["date"]).diff().dt.days
    df["is_flatline"] = (df["days_gap"] > FLATLINE_MIN_DAYS) & (df["km_change"] >= 0)& (df["km_change"] < FLATLINE_MAX_KM )
    return df

def find_jump(df):
    df["is_jump"] = (df["days_gap"] <= JUMP_MAX_DAYS) & (df["km_change"] >= JUMP_MIN_KM)
    return df

def analyze(vehicle_id):
    df = get_readings(vehicle_id)
    df = find_rollback(df)
    df = find_flatline(df)
    df = find_jump(df)
    return df

if __name__ == "__main__":
    print(get_vehicle_id_by_plate_number("mh 12 ab 1234"))