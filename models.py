from sqlmodel import Field, SQLModel
from typing import Optional

class Vehicle(SQLModel, table = True):
    id : Optional[int] = Field(default = None , primary_key = True)
    plate_number : str = Field(unique = True, index= True)
    company : str
    model : str
    year : int
    fuel_type : str
    scenario_label : str = Field(description= "Planted test story for this mock car: clean, rollback, flatline or jump. Used only to verify the engine, never as its input" \
    "1. clean : Honest car, nothing wrong (Eg. : km rises steadily, around 8,000 to 15,000 a year)" \
    "2. rollback : Meter was turned back (Eg. : km goes up, then drops (60,000 → 85,000 → 40,000))" \
    "3. flatline : Meter stopped working or was disconnected (Eg. : km stays almost the same for over a year)" \
    "4. jump : Unrealistic jump (Eg. : +40,000 km in one month)")
    