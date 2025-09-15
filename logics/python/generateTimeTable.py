from ortools.sat.python import cp_model
# Problem data
days = ["Mon", "Tue", "Wed", "Thu", "Fri"]
time_slots = ["9-11", "11-13", "13-15", "15-17"]  # 2-hour blocks
sections = ["A", "B", "C", "D"]
rooms = ["Room1", "Room2", "Room3", "Room4"]

subjects = ["Math", "Physics", "Chemistry", "Biology", "CS", "English"]

# 12 teachers: 2 teachers per subject
teachers = {
    "T1": "Math",   "T2": "Math",
    "T3": "Physics","T4": "Physics",
    "T5": "Chemistry","T6": "Chemistry",
    "T7": "Biology","T8": "Biology",
    "T9": "CS",    "T10": "CS",
    "T11": "English","T12": "English"
}
teacher_list = list(teachers.keys())

# Each teacher will teach exactly 2 sections of their subject.
# We split sections so that for each subject:
#   teacher1 -> sections A,B
#   teacher2 -> sections C,D
teacher_sections = {}
for si, subj in enumerate(subjects):
    t1 = teacher_list[2 * si]
    t2 = teacher_list[2 * si + 1]
    teacher_sections[t1] = ["A", "B"]
    teacher_sections[t2] = ["C", "D"]

# Hours per subject per section (in hours)

hours_per_subject = {s: 4 for s in subjects}
slots_required = {s: hours_per_subject[s] // 2 for s in subjects}
# Model
model = cp_model.CpModel()

# Create variables:
# x[d, t, sec, room, teacher] = 1 if teacher teaches (their subject) to section 'sec'
# at day d and time t in room.
slots = {}
for d in days:
    for t in time_slots:
        for sec in sections:
            for room in rooms:
                for teacher in teacher_list:
                    # Only create var if teacher is allowed to teach this section
                    if sec in teacher_sections[teacher]:
                        subj = teachers[teacher]
                        name = f"{d}_{t}_{sec}_{room}_{teacher}_{subj}"
                        slots[(d, t, sec, room, teacher)] = model.NewBoolVar(name)

# Constraints

# 1) Each section can have at most 1 class in a given (day, time)
for d in days:
    for t in time_slots:
        for sec in sections:
            terms = []
            for room in rooms:
                for teacher in teacher_list:
                    key = (d, t, sec, room, teacher)
                    if key in slots:
                        terms.append(slots[key])
            model.Add(sum(terms) <= 1)

# 2) A teacher can teach at most 1 class at a given (day, time)
for d in days:
    for t in time_slots:
        for teacher in teacher_list:
            terms = []
            for sec in sections:
                # teacher may only teach certain sections, but check presence
                for room in rooms:
                    key = (d, t, sec, room, teacher)
                    if key in slots:
                        terms.append(slots[key])
            model.Add(sum(terms) <= 1)

# 3) A room can host at most 1 class at a given (day, time)
for d in days:
    for t in time_slots:
        for room in rooms:
            terms = []
            for sec in sections:
                for teacher in teacher_list:
                    key = (d, t, sec, room, teacher)
                    if key in slots:
                        terms.append(slots[key])
            model.Add(sum(terms) <= 1)

# 4) Each subject must get the required number of 2-hour slots per section per week
for sec in sections:
    for subj in subjects:
        terms = []
        for d in days:
            for t in time_slots:
                for room in rooms:
                    for teacher in teacher_list:
                        # only include variables where this teacher teaches subj and can teach this section
                        if teachers[teacher] == subj:
                            key = (d, t, sec, room, teacher)
                            if key in slots:
                                terms.append(slots[key])
        # equality ensures exact required slots (e.g., 2)
        model.Add(sum(terms) == slots_required[subj])

# 5) Prevent same subject twice for same section on same day

for sec in sections:
    for subj in subjects:
        for d in days:
            terms = []
            for t in time_slots:
                for room in rooms:
                    for teacher in teacher_list:
                        if teachers[teacher] == subj:
                            key = (d, t, sec, room, teacher)
                            if key in slots:
                                terms.append(slots[key])
            model.Add(sum(terms) <= 1)

# 6) No consecutive classes for a teacher on same day (teacher needs a break)
#    For each adjacent pair of time slots (t_i, t_{i+1}) ensure teacher not assigned in both.
for d in days:
    for teacher in teacher_list:
        for i in range(len(time_slots) - 1):
            t1 = time_slots[i]
            t2 = time_slots[i + 1]
            terms = []
            for sec in sections:
                for room in rooms:
                    k1 = (d, t1, sec, room, teacher)
                    k2 = (d, t2, sec, room, teacher)
                    if k1 in slots:
                        terms.append(slots[k1])
                    if k2 in slots:
                        terms.append(slots[k2])
            # at most one of the adjacent slots for this teacher on this day
            model.Add(sum(terms) <= 1)

# Solve
solver = cp_model.CpSolver()
solver.parameters.max_time_in_seconds = 60
solver.parameters.num_search_workers = 8

status = solver.Solve(model)

# Output
if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
    print("Solution found.\n")
    for sec in sections:
        print(f"--- Timetable for Section {sec} ---")
        # Header row
        header = f"{'Day':<8}"
        for t in time_slots:
            header += f"{t:^25}"
        print(header)
        print("-" * len(header))

        for d in days:
            row = f"{d:<8}"
            for t in time_slots:
                found = False
                cell_text = "Free"
                for room in rooms:
                    for teacher in teacher_list:
                        key = (d, t, sec, room, teacher)
                        if key in slots and solver.Value(slots[key]) == 1:
                            subj = teachers[teacher]
                            cell_text = f"{subj} ({teacher}) {room}"
                            found = True
                            break
                    if found:
                        break
                row += f"{cell_text:^25}"
            print(row)
        print("\n")
else:
    print("No feasible solution found. Status:", solver.StatusName(status))
