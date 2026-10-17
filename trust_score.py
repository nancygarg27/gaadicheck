from sqlmodel import Session, select
from database import engine
from models import Challan, Loan
from anomaly import analyze

def calculate_trust_score(vehicle_id):
    score = 100
    reasons = []

    df = analyze(vehicle_id)
    if(df["is_rollback"].sum() > 0):
        score -= 40
        bad = df[df["is_rollback"]].iloc[0]
        before = int(bad["km"]- bad["km_change"])
        after = int(bad["km"])
        reasons.append(f"-40 : Meter rollback : {before} to {after} km")
    
    if(df["is_flatline"].sum() > 0):
        score -= 15
        flat = df[df["is_flatline"]]
        
        total_kms += int(flat["days_gap"].sum())
        total_days += int(flat["km_change"].sum())
        reasons.append(f"-15 : Meter flatline : only {total_km} addded in {total_days} days")
    
    if(df["is_jump"].sum() > 0):
        score -= 20
        jump = df[df["is_jump"]].iloc[0]
        km_added = int(jump["km_change"])
        days = int(jump["days_gap"])
        reasons.append(f"-20 : Unrealistic jump: {km_added} km added in {days} days")

    with Session(engine) as session:
        loans = session.exec(select(Loan).where(Loan.vehicle_id == vehicle_id, Loan.is_active == True)).all()
        for loan in loans:
            score = score -20
            reasons.append(f"-20 : loan is pending in {loan.bank_name}")

        challans = session.exec(select(Challan).where(Challan.vehicle_id == vehicle_id, Challan.is_paid == False)).all()
        for challan in challans:
            score = score - 5
            reasons.append("-5 : Fine/Challan is unpaid")

        score = max(0, score)

        if(score >= 80):
            status = "Green"
        elif(score >= 50):
            status = "Yellow"
        else:
            status = "Red"
    return score, status, reasons

if __name__ == "__main__":
    print(calculate_trust_score(5))        

          
