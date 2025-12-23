import pandas as pd
import math
import os
from ortools.sat.python import cp_model

# ==========================================
# 1. CONFIGURATION
# ==========================================
WORKING_DAYS = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']
START_TIME = 8.0   # 8:00 AM
END_TIME = 18.0    # 6:00 PM
NUM_SLOTS = 10     # 10 hours total
LUNCH_START = 13.0 # 1:00 PM
LAB_BATCH_SIZE = 30 

print(f"--- Schedulify: Final Corrected Mode (Subgroup Naming Fix) ---")

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
        self.room_indices = {} 
        self.room_id_to_idx = {}

    def clean_str(self, s):
        """Standardizes strings to lowercase and stripped."""
        return str(s).strip().lower() if pd.notna(s) else ""

    def load_data(self):
        def read_excel_csv(filename):
            try: return pd.read_csv(filename, encoding='cp1252')
            except: return pd.read_csv(filename)

        # Slots
        self.slots = []
        total_hours = END_TIME - START_TIME
        slot_duration = total_hours / NUM_SLOTS
        self.lunch_slot_index = int((LUNCH_START - START_TIME) / slot_duration)
        for d in WORKING_DAYS:
            for s in range(NUM_SLOTS):
                self.slots.append((d, s))

        # --- GROUPS (Infer if missing) ---
        print("\n[1] Loading groups...")
        try:
            df_groups = read_excel_csv('groups.csv')
            for _, row in df_groups.iterrows():
                if pd.isna(row.get('group name')): continue
                g_raw = str(row['group name'])
                s_raw = str(row['semester'])
                d_raw = str(row['degree'])
                uid = f"{self.clean_str(d_raw)}_{self.clean_str(s_raw)}_{self.clean_str(g_raw)}"
                try: strength = int(row['strength'])
                except: strength = 50 
                num_batches = math.ceil(strength / LAB_BATCH_SIZE)
                self.groups[uid] = {'strength': strength, 'dept': self.clean_str(d_raw), 
                                    'num_batches': num_batches, 'batch_strength': math.ceil(strength / num_batches)}
        except FileNotFoundError: pass

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
                self.room_indices[r['clean_id']] = i
                self.room_id_to_idx[r['id']] = i

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
                g_raw = str(row['group']) # Keep raw name for display (e.g. "A")
                s_raw = str(row['semester'])
                d_raw = str(row['degree']) if 'degree' in row else 'BTech'
                target_group_id = f"{self.clean_str(d_raw)}_{self.clean_str(s_raw)}_{self.clean_str(g_raw)}"
                
                # Auto-create group if missing (Robustness)
                if target_group_id not in self.groups:
                    self.groups[target_group_id] = {'strength': 60, 'dept': 'general', 'num_batches': 2, 'batch_strength': 30}

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

                # Practicals (With Corrected Naming Logic)
                if is_practical:
                    forced_idx = None
                    if prac_room_col and pd.notna(row.get(prac_room_col)):
                        req_room_clean = self.clean_str(row[prac_room_col])
                        if req_room_clean in self.room_indices: forced_idx = self.room_indices[req_room_clean]

                    num_batches = self.groups[target_group_id]['num_batches']
                    slots_needed = math.ceil(2.0 / slot_duration)
                    
                    # Capture the group label for naming (e.g., "A", "MCA1")
                    g_label = g_raw.strip() 
                    
                    for b_idx in range(1, num_batches + 1):
                        self.classes_to_schedule.append({
                            'type': 'practical', 'course': c_code, 'group': target_group_id,
                            'sub_batch': f"{g_label}{b_idx}", # FIX: Use Parent Group Name
                            'dept': c_dept, 
                            'slots_required': slots_needed, 'forced_room_idx': forced_idx
                        })
        except FileNotFoundError: pass

    # --- ROBUST ROOM FINDER ---
    def get_valid_rooms(self, c_info):
        if c_info['forced_room_idx'] is not None: return [c_info['forced_room_idx']]
        c_type = c_info['type']
        c_dept = c_info['dept']
        g_id = c_info['group']
        needed = self.groups[g_id]['strength'] if c_info['sub_batch'] == 'All' else self.groups[g_id]['batch_strength']
        
        # 1. Strict Search
        valid = []
        for i, r in enumerate(self.rooms):
            if r['capacity'] < needed: continue
            if c_type == 'practical':
                if r['type'] != 'lab': continue
                if r['dept'] != 'general' and r['dept'] != c_dept: continue
            else:
                if r['type'] == 'lab': continue
            valid.append(i)
        
        # 2. Relaxed Search (Safety Valve)
        if not valid and c_type == 'practical':
            # Look for ANY lab big enough, ignore dept
            valid = [i for i, r in enumerate(self.rooms) if r['type'] == 'lab' and r['capacity'] >= needed]
            
        return valid

# ==========================================
# 3. SOLVER
# ==========================================

def solve_schedule(data):
    model = cp_model.CpModel()
    total_slots = len(data.slots)
    class_vars = {} 
    
    print("Building Constraints...")

    # 1. Create Variables
    for c_idx, c in enumerate(data.classes_to_schedule):
        class_vars[c_idx] = []
        valid_rooms = data.get_valid_rooms(c)
        if not valid_rooms: continue 
        
        duration = c['slots_required']
        
        for s in range(total_slots):
            day_slot = s % NUM_SLOTS
            if day_slot + duration > NUM_SLOTS: continue 
            
            # Lunch Check
            overlaps_lunch = False
            for d in range(duration):
                if (day_slot + d) == data.lunch_slot_index: overlaps_lunch = True
            if overlaps_lunch: continue
            
            for r in valid_rooms:
                v = model.NewBoolVar(f"c{c_idx}_{s}_{r}")
                class_vars[c_idx].append((s, r, v))
        
        if class_vars[c_idx]:
            model.Add(sum(v for s, r, v in class_vars[c_idx]) == 1)

    # 2. Constraints
    room_time_map = {}
    group_time_map = {} 
    
    for c_idx, options in class_vars.items():
        c = data.classes_to_schedule[c_idx]
        g_id = c['group']
        batch = c['sub_batch']
        duration = c['slots_required']
        
        for (start_s, r, v) in options:
            for d in range(duration):
                active_s = start_s + d
                
                # Room
                if (active_s, r) not in room_time_map: room_time_map[(active_s, r)] = []
                room_time_map[(active_s, r)].append(v)
                
                # Group
                if (active_s, g_id) not in group_time_map: group_time_map[(active_s, g_id)] = {'All': [], 'Batches': {}}
                target = group_time_map[(active_s, g_id)]
                if batch == 'All': target['All'].append(v)
                else:
                    if batch not in target['Batches']: target['Batches'][batch] = []
                    target['Batches'][batch].append(v)

    # Apply
    for vars_list in room_time_map.values():
        if len(vars_list) > 1: model.Add(sum(vars_list) <= 1)

    for buckets in group_time_map.values():
        l_vars = buckets['All']
        if len(l_vars) > 1: model.Add(sum(l_vars) <= 1)
        for b_vars in buckets['Batches'].values():
            if l_vars or b_vars: model.Add(sum(l_vars) + sum(b_vars) <= 1)
            if len(b_vars) > 1: model.Add(sum(b_vars) <= 1)

    # 3. Solve
    print("Solving... (Max 120s)")
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = 120
    status = solver.Solve(model)
    
    if status in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        print("✅ Solution Found!")
        return extract_solution(solver, class_vars, data)
    else:
        print("❌ No Solution Found.")
        return None

def extract_solution(solver, class_vars, data):
    master = []
    for c_idx, options in class_vars.items():
        c = data.classes_to_schedule[c_idx]
        for (s, r, v) in options:
            if solver.Value(v) == 1:
                day_name = data.slots[s][0]
                s_num = data.slots[s][1]
                start_h = START_TIME + (s_num * (END_TIME-START_TIME)/NUM_SLOTS)
                end_h = start_h + (c['slots_required'] * (END_TIME-START_TIME)/NUM_SLOTS)
                time_str = f"{int(start_h):02d}:{int((start_h%1)*60):02d} - {int(end_h):02d}:{int((end_h%1)*60):02d}"
                
                c_name = c['course']
                if c['sub_batch'] != 'All': c_name += f" ({c['sub_batch']})"
                
                master.append({
                    'Day': day_name, 'Time': time_str, 'Course': c_name,
                    'Group_ID': c['group'], 
                    'Group': c['group'].split('_')[-1], 
                    'Room': data.rooms[r]['id'],
                    'StartSlot': s_num, 'Duration': c['slots_required']
                })
                break
    return master

if __name__ == "__main__":
    data = SchedulerData()
    data.load_data()
    result = solve_schedule(data)
    
    if result:
        df = pd.DataFrame(result)
        df.to_csv('Master_Schedule.csv', index=False)
        print("Generated 'Master_Schedule.csv'")
        
        # --- GROUP GRID GENERATION ---
        print("Generating Group Grids...")
        
        # 1. Create Empty Grids for ALL groups
        time_headers = []
        for i in range(NUM_SLOTS):
            start_h = START_TIME + (i * (END_TIME-START_TIME)/NUM_SLOTS)
            end_h = start_h + (1 * (END_TIME-START_TIME)/NUM_SLOTS)
            time_headers.append(f"{int(start_h):02d}:{int((start_h%1)*60):02d}")

        grid_map = {gid: pd.DataFrame(index=WORKING_DAYS, columns=time_headers).fillna("") for gid in data.groups}
        
        # 2. Fill Grids
        for _, row in df.iterrows():
            gid = row['Group_ID']
            if gid not in grid_map:
                grid_map[gid] = pd.DataFrame(index=WORKING_DAYS, columns=time_headers).fillna("")
            
            t_df = grid_map[gid]
            content = f"{row['Course']} [{row['Room']}]"
            
            for i in range(row['Duration']):
                c_idx = row['StartSlot'] + i
                if c_idx < len(time_headers):
                    col = time_headers[c_idx]
                    if t_df.at[row['Day'], col] == "":
                        t_df.at[row['Day'], col] = content
                    else:
                        t_df.at[row['Day'], col] += f" / {content}"
        
        # 3. Save Files
        count = 0
        for gid, df in grid_map.items():
            safe_name = "".join([c for c in gid if c.isalnum() or c in ('_','-')])
            df.to_csv(f"Grid_Group_{safe_name}.csv")
            count += 1
            
        print(f"✅ Successfully generated {count} Group-Wise Timetables.")