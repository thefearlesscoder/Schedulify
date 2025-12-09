import pandas as pd
import random
import numpy as np
from deap import base, creator, tools, algorithms
import math

# ==========================================
# 1. HARDCODED CONFIGURATION (USER INPUTS)
# ==========================================

# Define your grid here
WORKING_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday'] # Add 'Saturday' if needed
START_TIME = 9.0   # 9:00 AM
END_TIME = 18.0    # 6:00 PM (18:00)
NUM_SLOTS = 9      # 9 hours total (9 AM to 6 PM) -> 9 slots
LUNCH_START = 13.0 # 1:00 PM (13:00)

# Auto-calculate slot duration
TOTAL_HOURS = END_TIME - START_TIME
SLOT_DURATION_HOURS = TOTAL_HOURS / NUM_SLOTS
print(f"DEBUG: Configuration set for {START_TIME}:00 to {END_TIME}:00")
print(f"DEBUG: Slot Duration calculated as {SLOT_DURATION_HOURS * 60} minutes.")

# ==========================================
# 2. DATA LOADING & PRE-PROCESSING
# ==========================================

class SchedulerData:
    def __init__(self):
        self.groups = {}
        self.teachers = {} # Not strictly used as dict, extracted from allocations
        self.rooms = []
        self.slots = [] # List of (Day, Slot_Index)
        self.constraints = []
        self.lunch_slot_index = -1 
        self.classes_to_schedule = []

    def load_data(self):
        # ---------------------------------------------------------
        # A. GENERATE SLOTS FROM HARDCODED INPUTS
        # ---------------------------------------------------------
        self.slots = []
        
        # Calculate which slot index is lunch
        # (13.0 - 9.0) / 1.0 = Index 4 (i.e., the 5th slot)
        self.lunch_slot_index = int((LUNCH_START - START_TIME) / SLOT_DURATION_HOURS)
        
        for day in WORKING_DAYS:
            for i in range(NUM_SLOTS):
                self.slots.append((day, i))

        # ---------------------------------------------------------
        # B. LOAD CSV FILES
        # ---------------------------------------------------------
        
        # 1. Load Groups
        # Format: group name, semester, degree, strength
        df_groups = pd.read_csv('groups.csv')
        for _, row in df_groups.iterrows():
            self.groups[row['group name']] = {
                'strength': row['strength'],
                'semester': row['semester'],
                'degree': row['degree'],
                'dept': row['degree'] # Simplification: mapping degree to dept
            }

        # 2. Load Rooms
        # Format: room no., capacity, department
        df_rooms = pd.read_csv('rooms.csv')
        for _, row in df_rooms.iterrows():
            self.rooms.append({
                'id': row['room no.'],
                'capacity': row['capacity'],
                'dept': row['department'] if pd.notna(row['department']) else 'General'
            })

        # 3. Load Allocations
        # Format: course, teacher
        df_alloc = pd.read_csv('teacher_allocated.csv')
        raw_allocs = dict(zip(df_alloc['course'], df_alloc['teacher']))
        
        # 4. Load Courses
        # Format: course_code, name, department, semester, group, no_of_hours, is_there_a_practical
        df_courses = pd.read_csv('courses.csv')
        
        for _, row in df_courses.iterrows():
            c_code = row['course_code']
            grp = row['group']
            hours = int(row['no_of_hours'])
            is_practical = str(row['is_there_a_practical']).lower().strip() == 'yes'
            dept = row['department']
            
            teacher = raw_allocs.get(c_code, "TBD")

            # Create Lecture Blocks (1 slot each)
            for _ in range(hours):
                self.classes_to_schedule.append({
                    'type': 'Lecture',
                    'course': c_code,
                    'group': grp,
                    'teacher': teacher,
                    'dept': dept,
                    'slots_required': 1,
                    'id': f"{c_code}_{grp}_L"
                })

            # Create Practical Block (Auto-generate 2-hour block)
            if is_practical:
                # Calculate slots needed for 2 hours
                slots_needed = math.ceil(2.0 / SLOT_DURATION_HOURS)
                self.classes_to_schedule.append({
                    'type': 'Practical',
                    'course': c_code,
                    'group': grp,
                    'teacher': teacher,
                    'dept': dept,
                    'slots_required': slots_needed,
                    'id': f"{c_code}_{grp}_P"
                })

        # 5. Load Constraints (Optional)
        try:
            self.constraints = pd.read_csv('constraints.csv').to_dict('records')
        except FileNotFoundError:
            print("No constraints.csv found. Skipping user constraints.")
            self.constraints = []

# ==========================================
# 3. FITNESS FUNCTION
# ==========================================

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0)) # Minimize Hard & Soft conflicts
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

def create_individual(classes, n_slots, n_rooms):
    # Gene = (Start Slot Index, Room Index)
    return [ (random.randint(0, n_slots - 1), random.randint(0, n_rooms - 1)) for _ in classes]

def check_constraints(individual, data):
    hard_conflicts = 0
    soft_conflicts = 0

    teacher_schedule = {} # {TeacherName: [List of (Day, Slot)]}
    group_schedule = {}   # {GroupName: [List of (Day, Slot)]}
    room_schedule = {}    # {RoomID: [List of (Day, Slot)]}
    
    teacher_daily_hours = {} # {TeacherName: {Day: Hours}}

    for idx, (slot_idx, room_idx) in enumerate(individual):
        class_info = data.classes_to_schedule[idx]
        
        # 1. Bounds Check
        if slot_idx >= len(data.slots): 
            hard_conflicts += 10
            continue

        day, start_slot_num = data.slots[slot_idx]
        room = data.rooms[room_idx]
        
        required_slots = class_info['slots_required']
        occupied_time_keys = []

        # 2. Day Boundary Check
        # If class starts at slot 8 (5pm) and needs 2 slots, it ends at 7pm (invalid)
        if start_slot_num + required_slots > NUM_SLOTS:
            hard_conflicts += 5 
        else:
            for s in range(required_slots):
                occupied_time_keys.append((day, start_slot_num + s))

        # Check collisions for every slot this class occupies
        for (d, s_num) in occupied_time_keys:
            
            # 3. Lunch Collision
            if s_num == data.lunch_slot_index:
                hard_conflicts += 10 # Strict penalty
            
            time_key = (d, s_num)

            # 4. Teacher Conflicts (Double booking)
            t_name = class_info['teacher']
            if t_name != "TBD":
                if t_name not in teacher_schedule: teacher_schedule[t_name] = []
                if time_key in teacher_schedule[t_name]:
                    hard_conflicts += 1
                teacher_schedule[t_name].append(time_key)

                # Track Daily Load
                if t_name not in teacher_daily_hours: teacher_daily_hours[t_name] = {}
                teacher_daily_hours[t_name][d] = teacher_daily_hours[t_name].get(d, 0) + SLOT_DURATION_HOURS

            # 5. Group Conflicts (Students in two places)
            g_name = class_info['group']
            if g_name not in group_schedule: group_schedule[g_name] = []
            if time_key in group_schedule[g_name]:
                hard_conflicts += 1
            group_schedule[g_name].append(time_key)

            # 6. Room Conflicts (Double booking)
            r_id = room['id']
            if r_id not in room_schedule: room_schedule[r_id] = []
            if time_key in room_schedule[r_id]:
                hard_conflicts += 1
            room_schedule[r_id].append(time_key)

        # 7. Room Capacity Check
        grp_strength = data.groups.get(class_info['group'], {}).get('strength', 0)
        if grp_strength > room['capacity']:
            hard_conflicts += 1

        # 8. Department Room Preference (Soft)
        if room['dept'] != 'General' and room['dept'] != class_info['dept']:
            soft_conflicts += 1
            
        # 9. User Constraints (Simple implementation)
        # Check constraints.csv logic if exists
        for constr in data.constraints:
             if constr['constraint_level'] == 'Course' and constr['entity_name'] == class_info['course']:
                 # Example: Check if assigned room matches preference
                 if pd.notna(constr['preferred_room']) and str(constr['preferred_room']) != str(room['id']):
                     soft_conflicts += 1

    # 10. Teacher Daily Limit Check (> 4 hours)
    for t in teacher_daily_hours:
        for d in teacher_daily_hours[t]:
            if teacher_daily_hours[t][d] > 4.0: 
                hard_conflicts += (teacher_daily_hours[t][d] - 4) * 2

    return hard_conflicts, soft_conflicts

# ==========================================
# 4. OUTPUT GENERATION
# ==========================================

def get_time_string(slot_num, duration_slots):
    # Convert slot index to actual time string
    start_h = START_TIME + (slot_num * SLOT_DURATION_HOURS)
    end_h = start_h + (duration_slots * SLOT_DURATION_HOURS)
    
    def fmt(h):
        mins = int((h % 1) * 60)
        hours = int(h)
        return f"{hours:02d}:{mins:02d}"
    
    return f"{fmt(start_h)} - {fmt(end_h)}"

def generate_csvs(best_ind, data):
    master_schedule = []

    for idx, (slot_idx, room_idx) in enumerate(best_ind):
        c_info = data.classes_to_schedule[idx]
        
        if slot_idx >= len(data.slots): continue
            
        day, slot_num = data.slots[slot_idx]
        room = data.rooms[room_idx]
        
        time_str = get_time_string(slot_num, c_info['slots_required'])

        master_schedule.append({
            'Day': day,
            'Time': time_str,
            'Course Code': c_info['course'],
            'Group': c_info['group'],
            'Teacher': c_info['teacher'],
            'Room': room['id'],
            'Department': c_info['dept'],
            'Type': c_info['type'],
            'Semester': data.groups.get(c_info['group'], {}).get('semester', 'N/A')
        })

    df_master = pd.DataFrame(master_schedule)
    df_master.to_csv('Master_Timetable.csv', index=False)
    print("Generated: Master_Timetable.csv")
    
    if not df_master.empty:
        # Teacher-wise Files
        for t in df_master['Teacher'].unique():
            if t != "TBD":
                fname = f'Teacher_{t}.csv'
                df_master[df_master['Teacher'] == t].sort_values(['Day', 'Time']).to_csv(fname, index=False)
                print(f"Generated: {fname}")
        
        # Group-wise Files
        for g in df_master['Group'].unique():
            fname = f'Group_{g}.csv'
            df_master[df_master['Group'] == g].sort_values(['Day', 'Time']).to_csv(fname, index=False)
            print(f"Generated: {fname}")

# ==========================================
# MAIN EXECUTION BLOCK
# ==========================================
if __name__ == "__main__":
    # 1. Initialize
    data = SchedulerData()
    print("Loading Data...")
    
    # We try to load data. If CSVs are missing, we warn the user.
    try:
        data.load_data()
        print(f"Loaded {len(data.classes_to_schedule)} class sessions to schedule.")
    except Exception as e:
        print(f"\n[Error] Could not load data: {e}")
        print("Ensure 'groups.csv', 'rooms.csv', 'courses.csv', and 'teacher_allocated.csv' are in this folder.")
        exit()

    if not data.classes_to_schedule:
        print("[Error] No classes loaded. Check your CSV content.")
        exit()

    # 2. Setup GA
    toolbox.register("individual", create_individual, data.classes_to_schedule, len(data.slots), len(data.rooms))
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", check_constraints, data=data)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", tools.mutUniformInt, low=0, up=len(data.slots)-1, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # 3. Run Algorithm
    pop = toolbox.population(n=100) # Size of population
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min, axis=0)
    
    print("Running optimization...")
    # ngen=100 generations
    result, log = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=100, stats=stats, verbose=True)

    # 4. Export Results
    best_ind = tools.selBest(result, 1)[0]
    print(f"\nFinal Conflict Score (Hard, Soft): {best_ind.fitness.values}")
    generate_csvs(best_ind, data)