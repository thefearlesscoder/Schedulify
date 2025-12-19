import pandas as pd
import random
import numpy as np
from deap import base, creator, tools, algorithms
import math

# ==========================================
# 1. CONFIGURATION
# ==========================================
WORKING_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']
START_TIME = 9.0   # 9:00 AM
END_TIME = 18.0    # 6:00 PM
NUM_SLOTS = 9      # 9 hours total
LUNCH_START = 13.0 # 1:00 PM

# Calculate slot duration
TOTAL_HOURS = END_TIME - START_TIME
SLOT_DURATION_HOURS = TOTAL_HOURS / NUM_SLOTS

print(f"--- Schedulify: Optimization Mode ---")
print(f"Time: {START_TIME}:00 to {END_TIME}:00 | Lunch @ {LUNCH_START}:00")
print(f"Logic: Teachers are allocated post-scheduling (Infinite availability assumed).")

# ==========================================
# 2. DATA LOADING (No Teacher CSV)
# ==========================================

class SchedulerData:
    def __init__(self):
        self.groups = {}
        self.rooms = []
        self.slots = []
        self.lunch_slot_index = -1 
        self.classes_to_schedule = []

    def load_data(self):
        # A. Generate Slots
        self.slots = []
        self.lunch_slot_index = int((LUNCH_START - START_TIME) / SLOT_DURATION_HOURS)
        for day in WORKING_DAYS:
            for i in range(NUM_SLOTS):
                self.slots.append((day, i))

        # B. Load Groups
        print("[Loading] groups.csv...")
        try:
            df_groups = pd.read_csv('groups.csv')
            df_groups.columns = [c.strip() for c in df_groups.columns]
            
            for _, row in df_groups.iterrows():
                g_name = str(row['group name']).strip().upper() 
                sem = str(row['semester']).strip()
                deg = str(row['degree']).strip()
                
                # Unique ID: BTech_1_A
                unique_id = f"{deg}_{sem}_{g_name}"
                
                self.groups[unique_id] = {
                    'strength': row['strength'],
                    'semester': sem,
                    'degree': deg,
                    'dept': deg
                }
        except FileNotFoundError:
            print(" [Error] groups.csv not found.")
            return

        # C. Load Rooms
        print("[Loading] rooms.csv...")
        try:
            df_rooms = pd.read_csv('rooms.csv')
            for _, row in df_rooms.iterrows():
                r_dept = str(row['department']).strip()
                # Treat "Common", Empty, Nan as General
                if pd.isna(row['department']) or r_dept.lower() in ['common', 'general', 'nan', '']:
                    final_dept = 'General'
                else:
                    final_dept = r_dept

                self.rooms.append({
                    'id': str(row['room no.']).strip(),
                    'capacity': row['capacity'],
                    'dept': final_dept
                })
        except FileNotFoundError:
            print(" [Warning] rooms.csv not found. Using dummy infinite room.")
            self.rooms.append({'id': 'VirtRoom', 'capacity': 9999, 'dept': 'General'})

        # D. Load Courses (Teacher CSV Removed)
        print("[Loading] courses.csv...")
        try:
            df_courses = pd.read_csv('courses.csv')
            df_courses.dropna(subset=['course_code'], inplace=True)
            self.classes_to_schedule = [] 
            
            for _, row in df_courses.iterrows():
                c_code = str(row['course_code']).strip()
                g_name = str(row['group']).strip().upper()
                sem = str(row['semester']).strip()
                
                # Degree check
                if 'degree' in row and pd.notna(row['degree']):
                    deg = str(row['degree']).strip()
                    if deg == 'Btech': deg = 'BTech'
                else:
                    deg = "BTech"
                
                target_group_id = f"{deg}_{sem}_{g_name}"
                
                if target_group_id not in self.groups:
                    continue

                hours = int(row['no_of_hours'])
                is_practical = str(row['is_there_a_practical']).lower().strip() == 'yes'
                dept = row['department']
                
                # VIRTUAL TEACHER ASSIGNMENT
                # We assign a unique ID per class tuple so conflicts never occur
                # The output CSV will just say "Department Faculty"
                virtual_teacher_id = f"Fac_{c_code}_{target_group_id}"

                # Lectures
                for _ in range(hours):
                    self.classes_to_schedule.append({
                        'type': 'Lecture',
                        'course': c_code,
                        'group': target_group_id,
                        'teacher_id': virtual_teacher_id, # Unique ID for logic
                        'teacher_display': "Dept Faculty", # Pretty name for CSV
                        'dept': dept,
                        'slots_required': 1
                    })

                # Practicals
                if is_practical:
                    slots_needed = math.ceil(2.0 / SLOT_DURATION_HOURS)
                    self.classes_to_schedule.append({
                        'type': 'Practical',
                        'course': c_code,
                        'group': target_group_id,
                        'teacher_id': virtual_teacher_id,
                        'teacher_display': "Dept Faculty",
                        'dept': dept,
                        'slots_required': slots_needed
                    })
            print(f" - Loaded {len(self.classes_to_schedule)} sessions.")
            
        except FileNotFoundError:
            print(" [Error] courses.csv not found.")

# ==========================================
# 3. GENETIC ALGORITHM
# ==========================================

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()

def create_individual(classes, n_slots, n_rooms):
    return [ (random.randint(0, n_slots - 1), random.randint(0, n_rooms - 1)) for _ in classes]

def check_constraints(individual, data):
    hard = 0
    soft = 0
    
    group_schedule = {}   
    room_schedule = {}    
    lab_course_schedule = {} 

    # NOTE: We removed the "Teacher Schedule" dictionary check
    # because we assume infinite/perfect teacher allocation capability.

    for idx, (slot_idx, room_idx) in enumerate(individual):
        if slot_idx >= len(data.slots): continue
        
        c_info = data.classes_to_schedule[idx]
        day, start_slot = data.slots[slot_idx]
        room = data.rooms[room_idx]
        
        # Duration Boundary Check
        slots_req = c_info['slots_required']
        if start_slot + slots_req > NUM_SLOTS:
            hard += 5 
        
        # Calculate occupied slots
        occupied = []
        for s in range(slots_req):
            s_num = start_slot + s
            if s_num < NUM_SLOTS:
                occupied.append((day, s_num))
        
        for (d, s_num) in occupied:
            t_key = (d, s_num)
            
            # 1. LUNCH (Universal)
            if s_num == data.lunch_slot_index: hard += 10
            
            # 2. GROUP CONFLICT (Students can't be in 2 places)
            g_name = c_info['group']
            if g_name not in group_schedule: group_schedule[g_name] = []
            if t_key in group_schedule[g_name]: hard += 1
            group_schedule[g_name].append(t_key)
            
            # 3. LOCATION LOGIC
            if c_info['type'] == 'Practical':
                # Constraint: Subject Lab (e.g. Physics) can only handle 1 group at a time
                lab_key = (c_info['course'], d, s_num)
                if lab_key in lab_course_schedule:
                    hard += 1 
                lab_course_schedule[lab_key] = True
            else:
                # Lecture Room Logic
                r_id = room['id']
                
                # Double Booking
                if r_id not in room_schedule: room_schedule[r_id] = []
                if t_key in room_schedule[r_id]: hard += 1
                room_schedule[r_id].append(t_key)
                
                # Capacity
                if data.groups[c_info['group']]['strength'] > room['capacity']: hard += 1
                
                # Dept Preference (Soft)
                if room['dept'] != 'General' and room['dept'] != c_info['dept']: soft += 1

    return hard, soft

# ==========================================
# 4. OUTPUT
# ==========================================

def get_time_str(slot_num, slots_req):
    start_h = START_TIME + (slot_num * SLOT_DURATION_HOURS)
    end_h = start_h + (slots_req * SLOT_DURATION_HOURS)
    return f"{int(start_h):02d}:{int((start_h%1)*60):02d} - {int(end_h):02d}:{int((end_h%1)*60):02d}"

def generate_csvs(best_ind, data):
    master = []
    for idx, (slot_idx, room_idx) in enumerate(best_ind):
        if slot_idx >= len(data.slots): continue
        c = data.classes_to_schedule[idx]
        day, s_num = data.slots[slot_idx]
        
        # Smart Room Naming
        if c['type'] == 'Practical':
            final_room = f"LAB ({c['dept']})"
        else:
            final_room = data.rooms[room_idx]['id']

        master.append({
            'Day': day,
            'Time': get_time_str(s_num, c['slots_required']),
            'Course': c['course'],
            'Group': c['group'],
            'Teacher': "To Be Assigned", # Placeholder
            'Room': final_room,
            'Type': c['type'],
            'Department': c['dept']
        })
        
    df = pd.DataFrame(master)
    df.to_csv('Master_Timetable.csv', index=False)
    print("\n[Success] Master_Timetable.csv created.")
    
    if not df.empty:
        # Generate Group-wise Files
        for g in df['Group'].unique():
            df[df['Group']==g].sort_values(['Day','Time']).to_csv(f"Group_{g}.csv", index=False)
        print("[Success] Individual Group files generated.")

# ==========================================
# MAIN
# ==========================================
if __name__ == "__main__":
    data = SchedulerData()
    data.load_data()
    
    if not data.classes_to_schedule:
        print("No classes to schedule.")
        exit()

    toolbox.register("individual", create_individual, data.classes_to_schedule, len(data.slots), len(data.rooms))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", check_constraints, data=data)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(data.slots)-1, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)

    print("\n[Algorithm] Optimizing Schedule (No Teacher Constraints)...")
    pop = toolbox.population(n=100)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min, axis=0)
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=120, stats=stats, verbose=True)
    
    best = tools.selBest(pop, 1)[0]
    print(f"\n[Result] Best Conflicts: Hard={best.fitness.values[0]}, Soft={best.fitness.values[1]}")
    generate_csvs(best, data)