import pandas as pd
from sqlmodel import select, Session
from database import engine
from models import OdometerReading

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

if __name__ == "__main__":
    print(get_readings(3))