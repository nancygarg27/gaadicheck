from sqlmodel import Session, select
from database import engine
from models import Vehicle
from anomaly import analyze

def evaluate():
    caught= 0
    false_alarms =0
    missed_frauds =0 
    wrong =0

    with Session(engine) as session:
        vehicles= session.exec(select(Vehicle)).all()

        for v in vehicles:
            df = analyze(v.id)

            if(df["is_rollback"].sum()  > 0):
                scenario_predicted = "rollback"
            elif(df["is_flatline"].sum() > 0):
                scenario_predicted = "flatline"
            elif(df["is_jump"].sum() > 0):
                scenario_predicted = "jump"
            else:
                scenario_predicted = "clean"

            if(scenario_predicted ==  v.scenario_label):
                caught += 1
            else :
                if((v.scenario_label == "clean") & (scenario_predicted != "clean")):
                    false_alarms += 1
                elif((v.scenario_label != "clean") & (scenario_predicted == "clean")):
                    missed_frauds += 1
                else:
                    wrong += 1
                
                print(v.plate_number, "real:", v.scenario_label, "engine:", scenario_predicted)
    print(false_alarms, caught, missed_frauds, wrong)


if __name__ == "__main__":
    evaluate()

        

