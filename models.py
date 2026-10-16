from sqlmodel import Field, SQLModel
from typing import Optional
from datetime import date

class Vehicle(SQLModel, table = True):
    id : Optional[int] = Field(default = None , primary_key = True)
    plate_number : str = Field(unique = True, index= True)
    company : str
    model : str
    year : int
    fuel_type : str
    scenario_label : str = Field(description= "Planted test story for this mock car: clean, rollback, flatline or jump. Used only to verify the engine, never as its input" \
    " 1. clean : Honest car, nothing wrong (Eg. : km rises steadily, around 8,000 to 15,000 a year)" \
    " 2. rollback : Meter was turned back (Eg. : km goes up, then drops (60,000 → 85,000 → 40,000))" \
    " 3. flatline : Meter stopped working or was disconnected (Eg. : km stays almost the same for over a year)" \
    " 4. jump : Unrealistic jump (Eg. : +40,000 km in one month)")

class OdometerReading(SQLModel, table= True):
    id : Optional[int] = Field(default = None, primary_key = True)
    vehicle_id : int = Field(foreign_key = "vehicle.id", index= True)
    reading_date : date
    distance_km : int
    source : str = Field(description = "From where did you get the reading?" \
    " 1. service , 2. insurance , 3. inspection")

class Owner(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key = True)
    vehicle_id : int = Field(foreign_key = "vehicle.id", index = True)
    owner_name : str
    city : str
    owned_from_date : date
    owned_to_date : Optional[date] = Field(default = None)

class Challan(SQLModel, table= True):
    id : Optional[int] = Field(default = None, primary_key = True)
    vehicle_id : int = Field(foreign_key = "vehicle.id", index = True)
    challan_date : date
    amount_of_fine : int
    reason_of_challan : str
    is_paid : bool

class Loan(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key = True)
    vehicle_id : int = Field(foreign_key = "vehicle.id", index = True)
    bank_name : str
    loan_amount : int
    is_active : bool 

class ServiceRecord(SQLModel, table = True):
    id : Optional[int] = Field(default = None, primary_key = True)
    vehicle_id : int = Field(foreign_key = "vehicle.id", index = True)
    service_date : date
    work_done : str
    km_at_service : int
