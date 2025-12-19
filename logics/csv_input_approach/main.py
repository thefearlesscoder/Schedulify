import pandas as pd
import random
import numpy as np
from deap import base, creator, tools, algorithms
import math
import os

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

# ==========================================
# 2. DATA LOADING
# ==========================================

class SchedulerData:
    def __init__(self):
        self.groups = {}
        self.rooms = []
        self.slots = []
        self.lunch_slot_index = -1 
        self.classes_to_schedule = []
        self.constraints = [] # <--- Added Back

    def load_data(self):
        # --- HELPER: SAFE READ ---
        def read_excel_csv(filename):
            return pd.read_csv(filename, encoding='cp1252')
        # -------------------------

        # A. Generate Slots
        self.slots = []
        self.lunch_slot_index = int((LUNCH_START - START_TIME) / SLOT_DURATION_HOURS)
        for day in WORKING_DAYS:
            for i in range(NUM_SLOTS):
                self.slots.append((day, i))

        # B. Load Groups
        print("[Loading] groups.csv...")
        try:
            df_groups = read_excel_csv('groups.csv')
            df_groups.columns = [c.strip() for c in df_groups.columns]
            
            for _, row in df_groups.iterrows():
                g_name = str(row['group name']).strip().upper() 
                sem = str(row['semester']).strip()
                deg = str(row['degree']).strip()
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
        if not os.path.exists('rooms.csv'):
            print(" [Info] rooms.csv not found. Creating a temporary one in memory...")
            self.rooms.append({'id': 'Hall-A', 'capacity': 100, 'dept': 'General'})
            self.rooms.append({'id': 'Hall-B', 'capacity': 100, 'dept': 'General'})
        else:
            df_rooms = read_excel_csv('rooms.csv')
            for _, row in df_rooms.iterrows():
                r_dept = str(row['department']).strip()
                if pd.isna(row['department']) or r_dept.lower() in ['common', 'general', 'nan', '']:
                    final_dept = 'General'
                else:
                    final_dept = r_dept

                self.rooms.append({
                    'id': str(row['room no.']).strip(),
                    'capacity': row['capacity'],
                    'dept': final_dept
                })

        # D. Load Courses
        print("[Loading] courses.csv...")
        try:
            df_courses = read_excel_csv('courses.csv')
            df_courses.dropna(subset=['course_code'], inplace=True)
            self.classes_to_schedule = [] 
            
            for _, row in df_courses.iterrows():
                c_code = str(row['course_code']).strip()
                g_name = str(row['group']).strip().upper()
                sem = str(row['semester']).strip()
                
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
                virtual_teacher_id = f"Fac_{c_code}_{target_group_id}"

                # Lectures
                for _ in range(hours):
                    self.classes_to_schedule.append({
                        'type': 'Lecture',
                        'course': c_code,
                        'group': target_group_id,
                        'teacher_id': virtual_teacher_id, 
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
                        'dept': dept,
                        'slots_required': slots_needed
                    })
            print(f" - Loaded {len(self.classes_to_schedule)} sessions to schedule.")
            
        except FileNotFoundError:
            print(" [Error] courses.csv not found.")

        # E. Load Constraints (ADDED BACK)
        print("[Loading] constraints.csv...")
        if os.path.exists('constraints.csv'):
            try:
                df_cons = read_excel_csv('constraints.csv')
                # Expected columns: constraint_level, entity_name, group_name, preferred_time, preferred_room
                self.constraints = df_cons.to_dict('records')
                print(f" - Loaded {len(self.constraints)} user constraints.")
            except Exception as e:
                print(f" [Warning] Could not load constraints: {e}")
        else:
            print(" [Info] No constraints.csv found (Skipping).")

# ==========================================
# 3. GENETIC ALGORITHM
# ==========================================

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()

def create_individual(classes, n_slots, n_rooms):
    gene_list = [ (random.randint(0, n_slots - 1), random.randint(0, n_rooms - 1)) for _ in classes]
    return creator.Individual(gene_list)

def mutate_individual(individual, indpb, n_slots, n_rooms):
    for i in range(len(individual)):
        if random.random() < indpb:
            old_slot, old_room = individual[i]
            new_slot = random.randint(0, n_slots - 1) if random.random() < 0.5 else old_slot
            new_room = random.randint(0, n_rooms - 1) if random.random() < 0.5 else old_room
            individual[i] = (new_slot, new_room)
    return individual,

def get_time_str(slot_num, slots_req=1):
    start_h = START_TIME + (slot_num * SLOT_DURATION_HOURS)
    end_h = start_h + (slots_req * SLOT_DURATION_HOURS)
    return f"{int(start_h):02d}:{int((start_h%1)*60):02d} - {int(end_h):02d}:{int((end_h%1)*60):02d}"

def check_constraints(individual, data):
    hard = 0
    soft = 0
    
    group_schedule = {}   
    room_schedule = {}    
    lab_course_schedule = {} 

    for idx, (slot_idx, room_idx) in enumerate(individual):
        if slot_idx >= len(data.slots): continue
        
        c_info = data.classes_to_schedule[idx]
        day, start_slot = data.slots[slot_idx]
        room = data.rooms[room_idx]
        
        slots_req = c_info['slots_required']
        if start_slot + slots_req > NUM_SLOTS:
            hard += 5 
        
        occupied = []
        for s in range(slots_req):
            s_num = start_slot + s
            if s_num < NUM_SLOTS:
                occupied.append((day, s_num))
        
        current_time_str = get_time_str(start_slot, slots_req)

        for (d, s_num) in occupied:
            t_key = (d, s_num)
            
            # 1. LUNCH
            if s_num == data.lunch_slot_index: hard += 10
            
            # 2. GROUP CONFLICT
            g_name = c_info['group']
            if g_name not in group_schedule: group_schedule[g_name] = []
            if t_key in group_schedule[g_name]: hard += 1
            group_schedule[g_name].append(t_key)
            
            # 3. LOCATION
            if c_info['type'] == 'Practical':
                lab_key = (c_info['course'], d, s_num)
                if lab_key in lab_course_schedule: hard += 1 
                lab_course_schedule[lab_key] = True
            else:
                r_id = room['id']
                if r_id not in room_schedule: room_schedule[r_id] = []
                if t_key in room_schedule[r_id]: hard += 1
                room_schedule[r_id].append(t_key)
                
                if data.groups[c_info['group']]['strength'] > room['capacity']: hard += 1
                if room['dept'] != 'General' and room['dept'] != c_info['dept']: soft += 1

        # 4. USER CONSTRAINTS (The New Logic)
        for constr in data.constraints:
            # Check Level (Course or Teacher)
            # Since we removed teachers, we focus on Course
            if str(constr.get('constraint_level', '')).strip().lower() == 'course':
                if str(constr.get('entity_name', '')).strip() == c_info['course']:
                    
                    # Optional: Check Group Specificity
                    c_grp = str(constr.get('group_name', ''))
                    if pd.notna(c_grp) and c_grp.strip() != "" and c_grp.strip() != c_info['group']:
                        continue # Constraint applies to a different group of this course

                    # Check Room Preference
                    pref_room = str(constr.get('preferred_room', ''))
                    if pd.notna(constr.get('preferred_room')) and pref_room.strip() != "":
                         if pref_room.strip() != str(room['id']):
                             soft += 5 # Heavy penalty for missing room preference
                    
                    # Check Time Preference (String Matching)
                    # e.g. "Monday" or "09:00"
                    pref_time = str(constr.get('preferred_time', ''))
                    if pd.notna(constr.get('preferred_time')) and pref_time.strip() != "":
                        # Check if Day matches
                        if pref_time.lower() in day.lower():
                            pass # Good
                        # Check if Time matches
                        elif pref_time in current_time_str:
                            pass # Good
                        else:
                            soft += 5 # Penalty for missing time preference

    return hard, soft

# ==========================================
# 4. OUTPUT
# ==========================================

def generate_csvs(best_ind, data):
    master = []
    
    # Grid Headers
    time_headers = []
    for i in range(NUM_SLOTS):
        time_headers.append(get_time_str(i, 1))

    for idx, (slot_idx, room_idx) in enumerate(best_ind):
        if slot_idx >= len(data.slots): continue
        c = data.classes_to_schedule[idx]
        day, s_num = data.slots[slot_idx]
        
        if c['type'] == 'Practical':
            final_room = f"LAB ({c['dept']})"
        else:
            final_room = data.rooms[room_idx]['id']

        master.append({
            'Day': day,
            'StartSlot': s_num,
            'Duration': c['slots_required'],
            'Time': get_time_str(s_num, c['slots_required']),
            'Course': c['course'],
            'Group': c['group'],
            'Room': final_room,
            'Type': c['type'],
            'Department': c['dept']
        })
        
    df = pd.DataFrame(master)
    df.to_csv('Master_Flat_List.csv', index=False)
    print("\n[Success] Master_Flat_List.csv created.")
    
    if not df.empty:
        print("Generating readable grids...")
        unique_groups = df['Group'].unique()
        
        for g in unique_groups:
            grid_df = pd.DataFrame(index=WORKING_DAYS, columns=time_headers)
            grid_df = grid_df.fillna("")
            
            subset = df[df['Group'] == g]
            
            for _, row in subset.iterrows():
                day = row['Day']
                start_slot = row['StartSlot']
                duration = row['Duration']
                
                cell_content = f"{row['Course']}\n{row['Room']}"
                if row['Type'] == 'Practical':
                    cell_content += " (Prac)"
                
                for i in range(duration):
                    current_slot_idx = start_slot + i
                    if 0 <= current_slot_idx < len(time_headers):
                        col_name = time_headers[current_slot_idx]
                        if grid_df.at[day, col_name] == "":
                            grid_df.at[day, col_name] = cell_content
                        else:
                            grid_df.at[day, col_name] += f" / {cell_content}"

            safe_g = "".join([c for c in g if c.isalnum() or c in ('_','-')])
            grid_df.to_csv(f"Grid_Group_{safe_g}.csv")
            
        print(f"[Success] Generated {len(unique_groups)} Group Grid files.")

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
    toolbox.register("mutate", mutate_individual, indpb=0.1, n_slots=len(data.slots), n_rooms=len(data.rooms))
    toolbox.register("select", tools.selTournament, tournsize=3)

    print("\n[Algorithm] Optimizing Schedule...")
    pop = toolbox.population(n=50) 
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("min", np.min, axis=0)
    
    algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=50, stats=stats, verbose=True)
    
    best = tools.selBest(pop, 1)[0]
    print(f"\n[Result] Best Conflicts: Hard={best.fitness.values[0]}, Soft={best.fitness.values[1]}")
    generate_csvs(best, data)