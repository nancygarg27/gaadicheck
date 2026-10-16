from sqlmodel import Session
from datetime import date
from database import engine
from models import Vehicle, OdometerReading, Challan, Loan, ServiceRecord, Owner

with Session(engine) as session :
    result = Challan(vehicle_id = 2, challan_date = date(2024, 8, 22), amount_of_fine= 500, reason_of_challan= "over-speeding", is_paid = True)
    session.add(result)
    result1 = Challan(vehicle_id = 3, challan_date = date(2024, 1, 22), amount_of_fine= 800, reason_of_challan= "red-light break", is_paid = True)
    session.add(result1)
    result2 = Challan(vehicle_id = 3, challan_date = date(2024, 12, 18), amount_of_fine= 1500, reason_of_challan= "drink and drive", is_paid = False)
    session.add(result2)
    session.commit()
    
