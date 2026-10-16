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
        reasons.append("-40 : Meter rolback detected")
    if(df["is_flatline"].sum() > 0):
        score -= 15
        reasons.append("-15 : Meter flatline detected")
    if(df["is_jump"].sum() > 0):
        score -= 20
        reasons.append("-20 : Unrealistic km jump detected")

    with Session(engine) as session:
        loans = session.exec(select(Loan).where(Loan.vehicle_id == vehicle_id, Loan.is_active == True)).all()
        for loan in loans:
            score = score -20
            reasons.append(f"loan is pending in {loan.bank_name}")

        challans = session.exec(select(Challan).where(Challan.vehicle_id == vehicle_id, Challan.is_paid == False)).all()
        for challan in challans:
            score = score - 5
            reasons.append("Fine/Challan is unpaid")

        score = max(0, score)

        if(score >= 80):
            status = "Green"
        elif(score >= 50):
            status = "Yellow"
        else:
            status = "Red"
    return score

if __name__ == "__main__":
    print(calculate_trust_score(5))        

          
