import pandas as pd
import random
import numpy as np
from deap import base, creator, tools, algorithms
import math
import os

# ==========================================
# 1. CONFIGURATION
# ==========================================
WORKING_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
START_TIME = 8.0   # 8:00 AM
END_TIME = 18.0    # 6:00 PM
NUM_SLOTS = 10     # 10 hours total
LUNCH_START = 13.0 # 1:00 PM
LAB_BATCH_SIZE = 30 

PENALTY_HARD = 10000 
PENALTY_SOFT = 1      

TOTAL_HOURS = END_TIME - START_TIME
SLOT_DURATION_HOURS = TOTAL_HOURS / NUM_SLOTS

print(f"--- Schedulify: Single Run Mode ---")
print(f"Time: {START_TIME}:00 to {END_TIME}:00 | Slots: {NUM_SLOTS}")

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
        self.constraints = []
        self.room_id_map = {} 
        self.room_indices = {} 
        self.room_id_to_idx = {}

    def clean_str(self, s):
        """Standardizes strings to lowercase and stripped."""
        return str(s).strip().lower() if pd.notna(s) else ""

    def load_data(self):
        def read_excel_csv(filename):
            return pd.read_csv(filename, encoding='cp1252')

        self.slots = []
        self.lunch_slot_index = int((LUNCH_START - START_TIME) / SLOT_DURATION_HOURS)
        for day in WORKING_DAYS:
            for i in range(NUM_SLOTS):
                self.slots.append((day, i))

        # --- GROUPS ---
        print("\n[1] Loading groups...")
        try:
            df_groups = read_excel_csv('groups.csv')
            for _, row in df_groups.iterrows():
                if pd.isna(row.get('group name')): continue
                g_raw = str(row['group name'])
                s_raw = str(row['semester'])
                d_raw = str(row['degree'])
                
                unique_id = f"{self.clean_str(d_raw)}_{self.clean_str(s_raw)}_{self.clean_str(g_raw)}"
                try: strength = int(row['strength'])
                except: strength = 50 
                
                num_batches = math.ceil(strength / LAB_BATCH_SIZE)
                self.groups[unique_id] = {
                    'strength': strength, 'dept': self.clean_str(d_raw), 
                    'num_batches': num_batches, 'batch_strength': math.ceil(strength / num_batches)
                }
        except FileNotFoundError: return

        # --- ROOMS ---
        print("[2] Loading rooms...")
        if os.path.exists('rooms.csv'):
            df_rooms = read_excel_csv('rooms.csv')
            col_map = {self.clean_str(c): c for c in df_rooms.columns}
            
            room_col = next((col_map[c] for c in col_map if 'room' in c and 'no' in c), None) or 'room no.'
            type_col = next((col_map[c] for c in col_map if 'type' in c), None)
            dept_col = next((col_map[c] for c in col_map if 'dept' in c or 'department' in c), None)

            for _, row in df_rooms.iterrows():
                if pd.isna(row.get(room_col)): continue
                orig_id = str(row[room_col]).strip()
                clean_id = self.clean_str(orig_id)
                
                r_type = 'classroom'
                if type_col and pd.notna(row.get(type_col)):
                    val = self.clean_str(row[type_col])
                    if 'lab' in val or 'practical' in val: r_type = 'lab'
                
                r_dept = 'general'
                if dept_col and pd.notna(row.get(dept_col)): r_dept = self.clean_str(row[dept_col])

                try: cap = int(row['capacity'])
                except: cap = 0
                
                self.rooms.append({'id': orig_id, 'clean_id': clean_id, 'capacity': cap, 'dept': r_dept, 'type': r_type})
                
            for i, r in enumerate(self.rooms):
                self.room_id_map[r['clean_id']] = r['id']
                self.room_indices[r['clean_id']] = i
                self.room_id_to_idx[r['id']] = i # For output mapping if needed
            print(f" - Loaded {len(self.rooms)} rooms.")

        # --- COURSES ---
        print("[3] Loading courses...")
        try:
            df_courses = read_excel_csv('courses.csv')
            df_courses.dropna(subset=['course_code'], inplace=True)
            self.classes_to_schedule = [] 
            col_map = {self.clean_str(c): c for c in df_courses.columns}
            prac_room_col = next((col_map[c] for c in col_map if 'practical' in c and 'room' in c), None)

            for _, row in df_courses.iterrows():
                c_code = str(row['course_code']).strip()
                g_raw = str(row['group'])
                s_raw = str(row['semester'])
                d_raw = str(row['degree']) if 'degree' in row else 'BTech'
                
                target_group_id = f"{self.clean_str(d_raw)}_{self.clean_str(s_raw)}_{self.clean_str(g_raw)}"
                if target_group_id not in self.groups:
                    if 'degree' not in row: # Try fallback
                         target_group_id = f"btech_{self.clean_str(s_raw)}_{self.clean_str(g_raw)}"
                    if target_group_id not in self.groups: continue

                hours = int(row['no_of_hours'])
                is_practical = self.clean_str(row['is_there_a_practical']) == 'yes'
                c_dept = self.groups[target_group_id]['dept']
                if 'department' in row and pd.notna(row['department']): c_dept = self.clean_str(row['department'])
                
                # Lectures
                for _ in range(hours):
                    self.classes_to_schedule.append({
                        'type': 'lecture', 'course': c_code, 'group': target_group_id,
                        'sub_batch': 'All', 'dept': c_dept, 'slots_required': 1, 'forced_room_idx': None
                    })

                # Practicals
                if is_practical:
                    forced_idx = None
                    if prac_room_col and pd.notna(row.get(prac_room_col)):
                        req_room_clean = self.clean_str(row[prac_room_col])
                        if req_room_clean in self.room_indices: forced_idx = self.room_indices[req_room_clean]

                    num_batches = self.groups[target_group_id]['num_batches']
                    slots_needed = math.ceil(2.0 / SLOT_DURATION_HOURS)
                    for b_idx in range(1, num_batches + 1):
                        self.classes_to_schedule.append({
                            'type': 'practical', 'course': c_code, 'group': target_group_id,
                            'sub_batch': f"B{b_idx}", 'dept': c_dept, 
                            'slots_required': slots_needed, 'forced_room_idx': forced_idx
                        })
            print(f" - Loaded {len(self.classes_to_schedule)} sessions.")
        except FileNotFoundError: pass

        # --- CONSTRAINTS ---
        if os.path.exists('constraints.csv'):
            try:
                df_cons = read_excel_csv('constraints.csv')
                df_cons.columns = [c.strip().lower() for c in df_cons.columns]
                self.constraints = df_cons.to_dict('records')
            except: pass

    # --- VALID ROOM FINDER ---
    def get_valid_rooms(self, c_info):
        if c_info['forced_room_idx'] is not None: return [c_info['forced_room_idx']]
            
        c_type = c_info['type']
        c_dept = c_info['dept']
        g_id = c_info['group']
        needed = self.groups[g_id]['strength'] if c_info['sub_batch'] == 'All' else self.groups[g_id]['batch_strength']
        
        valid = []
        for i, r in enumerate(self.rooms):
            if r['capacity'] < needed: continue
            if c_type == 'practical':
                if r['type'] != 'lab': continue
                if r['dept'] != 'general' and r['dept'] != c_dept: continue
            else:
                if r['type'] == 'lab': continue
            valid.append(i)
            
        if not valid: valid = [i for i, r in enumerate(self.rooms) if r['capacity'] >= needed]
        return valid

# ==========================================
# 3. GENETIC ALGORITHM
# ==========================================

creator.create("FitnessMin", base.Fitness, weights=(-1.0, -1.0))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()

def create_individual(classes, n_slots, data):
    gene = []
    for c in classes:
        slot = random.randint(0, n_slots - 1)
        valid = data.get_valid_rooms(c)
        room = random.choice(valid) if valid else random.randint(0, len(data.rooms)-1)
        gene.append((slot, room))
    return creator.Individual(gene)

def mutate_individual(individual, indpb, n_slots, data):
    for i in range(len(individual)):
        if random.random() < indpb:
            c = data.classes_to_schedule[i]
            if c['forced_room_idx']:
                new_room = c['forced_room_idx']
            else:
                valid = data.get_valid_rooms(c)
                new_room = random.choice(valid) if valid else individual[i][1]
            new_slot = random.randint(0, n_slots - 1)
            individual[i] = (new_slot, new_room)
    return individual,

def check_constraints(individual, data, report_mode=False):
    hard = 0
    soft = 0
    group_occ = {} 
    room_occ = {}
    report_lines = []
    
    for idx, (slot_idx, room_idx) in enumerate(individual):
        c = data.classes_to_schedule[idx]
        
        # 1. Bounds
        if slot_idx + c['slots_required'] > NUM_SLOTS:
            hard += PENALTY_HARD
            if report_mode: report_lines.append(f"Hard: {c['course']} exceeds day bounds.")
            continue 
            
        time_range = range(slot_idx, slot_idx + c['slots_required'])
        day = data.slots[slot_idx][0]
        
        # User Time Constraint Check
        has_time_constraint = False
        for constr in data.constraints:
             if str(constr.get('constraint_level', '')).strip().lower() == 'course' and \
                str(constr.get('entity_name', '')).strip() == c['course']:
                     if pd.notna(constr.get('preferred_time')): has_time_constraint = True

        # 2. Lunch
        if data.lunch_slot_index in time_range and not has_time_constraint:
             hard += PENALTY_HARD

        # 3. Group Conflicts
        g_id = c['group']
        batch = c['sub_batch']
        t_keys = [(day, t) for t in time_range]
        
        if g_id not in group_occ: group_occ[g_id] = {'All': set(), 'Batches': {}}
        
        for t_key in t_keys:
            if batch == 'All':
                if t_key in group_occ[g_id]['All']: hard += PENALTY_HARD
                for b_set in group_occ[g_id]['Batches'].values():
                    if t_key in b_set: hard += PENALTY_HARD
                group_occ[g_id]['All'].add(t_key)
            else:
                if t_key in group_occ[g_id]['All']: hard += PENALTY_HARD
                if batch not in group_occ[g_id]['Batches']: group_occ[g_id]['Batches'][batch] = set()
                if t_key in group_occ[g_id]['Batches'][batch]: hard += PENALTY_HARD
                group_occ[g_id]['Batches'][batch].add(t_key)

        # 4. Room Conflicts
        r_id = room_idx
        if r_id not in room_occ: room_occ[r_id] = set()
        for t_key in t_keys:
            if t_key in room_occ[r_id]: hard += PENALTY_HARD
            room_occ[r_id].add(t_key)
            
        # 5. Lock Verification
        if c['forced_room_idx'] is not None:
            if room_idx != c['forced_room_idx']:
                hard += PENALTY_HARD
                if report_mode: report_lines.append(f"Hard: {c['course']} not in locked room.")

        # Constraints
        current_time_str = get_time_str(slot_idx, c['slots_required'])
        for constr in data.constraints:
            if str(constr.get('constraint_level', '')).lower() == 'course' and str(constr.get('entity_name', '')).strip() == c['course']:
                pref_time = str(constr.get('preferred_time', ''))
                if pd.notna(constr.get('preferred_time')) and pref_time.strip() != "":
                    if pref_time.lower() not in day.lower() and pref_time not in current_time_str:
                         hard += PENALTY_HARD

    if report_mode: return hard, soft, report_lines
    return hard, soft

def get_time_str(slot_num, slots_req=1):
    start_h = START_TIME + (slot_num * SLOT_DURATION_HOURS)
    end_h = start_h + (slots_req * SLOT_DURATION_HOURS)
    return f"{int(start_h):02d}:{int((start_h%1)*60):02d} - {int(end_h):02d}:{int((end_h%1)*60):02d}"

# ==========================================
# 4. RUNNER
# ==========================================
if __name__ == "__main__":
    data = SchedulerData()
    data.load_data()
    
    if not data.classes_to_schedule:
        print("No classes loaded.")
        exit()
        
    toolbox.register("individual", create_individual, data.classes_to_schedule, len(data.slots), data)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("evaluate", check_constraints, data=data)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("mutate", mutate_individual, indpb=0.1, n_slots=len(data.slots), data=data)
    toolbox.register("select", tools.selTournament, tournsize=3)

    print("\n[Algorithm] Optimizing (Single Run - 500 Gens)...")
    
    # SINGLE ITERATION CONFIG
    MAX_ATTEMPTS = 1
    GENERATIONS = 500
    
    best_overall = None
    
    for attempt in range(1, MAX_ATTEMPTS + 1):
        print(f" Attempt {attempt}...", end="\r")
        pop = toolbox.population(n=300)
        
        # Use simple EA loop or custom? Using algorithms.eaSimple for standard approach
        pop, log = algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.3, ngen=GENERATIONS, verbose=True)
        
        best = tools.selBest(pop, 1)[0]
        score = best.fitness.values[0]
        best_overall = best
        
        if score == 0:
            print(f"\n[Success] 0-Conflict Schedule Found!")
            break
        else:
            print(f"\n[Finished] Run completed with {int(score/PENALTY_HARD)} hard conflicts.")

    # Export
    # Generate CSVs
    h, s, logs = check_constraints(best_overall, data, report_mode=True)
    with open("Conflicts_Report.txt", "w") as f:
        if h == 0: f.write("SUCCESS.\n")
        else:
            f.write(f"FAILURE: {int(h/PENALTY_HARD)} Conflicts.\n")
            for line in logs: f.write(line + "\n")
    
    master = []
    for idx, (slot, room_idx) in enumerate(best_overall):
        c = data.classes_to_schedule[idx]
        if slot >= len(data.slots): continue
        
        day = data.slots[slot][0]
        s_num = data.slots[slot][1]
        
        room_obj = data.rooms[room_idx]
        c_name = c['course']
        if c['sub_batch'] != 'All': c_name += f" ({c['sub_batch']})"
        
        master.append({
            'Day': day, 'Time': get_time_str(s_num, c['slots_required']),
            'Course': c_name, 'Group': c['group'].split('_')[-1], 
            'Room': room_obj['id'], 'Type': c['type'], 'StartSlot': s_num, 'Duration': c['slots_required']
        })
        
    df = pd.DataFrame(master)
    df.to_csv('Master_Schedule.csv', index=False)
    
    time_headers = [get_time_str(i, 1) for i in range(NUM_SLOTS)]
    grid_map = {g: pd.DataFrame(index=WORKING_DAYS, columns=time_headers).fillna("") for g in data.groups}
    
    for _, row in df.iterrows():
        g_id = list(data.groups.keys())[0] # Need correct full group ID for map key
        # Find matching group key based on simple name in row?
        # Actually, let's just loop through groups and match
        for k in grid_map:
            if k.endswith(f"_{row['Group'].lower()}") or k.endswith(f"_{row['Group'].upper()}"):
                g_id = k
                break
        
        if g_id in grid_map:
            t_df = grid_map[g_id]
            content = f"{row['Course']} [{row['Room']}]"
            for i in range(row['Duration']):
                c_idx = row['StartSlot'] + i
                if c_idx < len(time_headers):
                    col = time_headers[c_idx]
                    if t_df.at[row['Day'], col] == "": t_df.at[row['Day'], col] = content
                    else: t_df.at[row['Day'], col] += f" / {content}"
    
    for g, df in grid_map.items():
        safe = "".join([x for x in g if x.isalnum() or x in ('_','-')])
        df.to_csv(f"Grid_{safe}.csv")
    print("Files Generated.") 