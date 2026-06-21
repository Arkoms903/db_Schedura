import random, csv
import sys, os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))  # so we can import app.py

from app import schedule, Payload  # reuse your existing FastAPI logic directly
from features import extract_features, FEATURE_NAMES

def random_payload():
    sections = random.randint(1, 6)
    periods = random.randint(8, 12)
    days = random.randint(3, 6)
    break_period = random.randint(2, periods - 1)
    section_names = [chr(ord('A') + i) for i in range(sections)]

    num_subjects = random.randint(3, 9)
    subjects = []
    for i in range(num_subjects):
        credit = random.randint(0, 5)
        lab = random.randint(0, 2)
        if credit == 0 and lab == 0:
            credit = 1
        subjects.append({"name": f"SUB{i}", "code": f"S{i}", "credit": credit, "lab": lab})

    theory_rooms = [f"TR{i}" for i in range(random.randint(1, 6))]
    lab_rooms = [f"LR{i}" for i in range(random.randint(1, 4))]

    num_faculty = random.randint(2, 10)
    faculty = [{"name": f"F{i}", "abbr": f"F{i}", "assignments": []} for i in range(num_faculty)]

    # round-robin assign every subject+section to a faculty so coverage is always valid
    theory_room_assignments, lab_room_assignments = [], []
    idx = 0
    for subj in subjects:
        for sec in section_names:
            fac = faculty[idx % num_faculty]
            fac["assignments"].append({
                "subjectName": subj["name"], "sections": [sec],
                "teachesTheory": subj["credit"] > 0, "teachesLab": subj["lab"] > 0,
            })
            if subj["credit"] > 0:
                theory_room_assignments.append({"subjectName": subj["name"], "sectionName": sec,
                                                  "roomName": theory_rooms[idx % len(theory_rooms)]})
            if subj["lab"] > 0:
                lab_room_assignments.append({"subjectName": subj["name"], "sectionName": sec,
                                              "roomName": lab_rooms[idx % len(lab_rooms)]})
            idx += 1

    return {
        "sectionsCount": sections, "theoryRooms": theory_rooms, "labRooms": lab_rooms,
        "theoryRoomAssignments": theory_room_assignments, "labRoomAssignments": lab_room_assignments,
        "subjects": subjects, "faculty": faculty,
        "periodsPerDay": periods, "breakPeriod": break_period, "workingDays": days,
    }

def main(n=500):
    rows = []
    for i in range(n):
        payload_dict = random_payload()
        feasible = 0
        try:
            payload_obj = Payload(**payload_dict)
            schedule(payload_obj)   # calls your real OR-Tools function
            feasible = 1
        except Exception:
            feasible = 0
        rows.append(extract_features(payload_dict) + [feasible])
        print(f"{i+1}/{n} -> {'OK' if feasible else 'FAIL'}")

    with open("training_data.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(FEATURE_NAMES + ["feasible"])
        writer.writerows(rows)

if __name__ == "__main__":
    main()