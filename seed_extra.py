from sqlmodel import Session
from datetime import date
from database import engine
from models import Vehicle, OdometerReading, Challan, Loan, ServiceRecord, Owner

with Session(engine) as session :
    loan_car3 = Loan(vehicle_id = 3, bank_name = "HDFC Bank", loan_amount = 450000, is_active = True)
    loan_car5 = Loan(vehicle_id = 5, bank_name = "SBI", loan_amount = 600000, is_active = False)
    loan_car6 = Loan(vehicle_id = 6, bank_name = "ICICI Bank", loan_amount = 900000, is_active = True)
    session.add(loan_car3)
    session.add(loan_car5)
    session.add(loan_car6)
    session.commit()
    
