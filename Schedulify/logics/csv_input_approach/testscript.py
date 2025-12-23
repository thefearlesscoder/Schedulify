import sys
import os

print("--- DIAGNOSTIC CHECK ---")

# 1. Check Libraries
try:
    import pandas as pd
    print("[PASS] Pandas is installed.")
except ImportError:
    print("[FAIL] Pandas is NOT installed. Run: pip install pandas")
    sys.exit()

try:
    import deap
    print("[PASS] DEAP is installed.")
except ImportError:
    print("[FAIL] DEAP is NOT installed. Run: pip install deap")
    sys.exit()

# 2. Check Files Existence
files = ['courses.csv', 'groups.csv', 'rooms.csv']
for f in files:
    if os.path.exists(f):
        print(f"[PASS] {f} found.")
    else:
        print(f"[FAIL] {f} is MISSING.")
        if f == 'rooms.csv':
            print("       -> Creating dummy rooms.csv for you...")
            with open('rooms.csv', 'w') as temp:
                temp.write("room no.,capacity,department\n101,60,General\n102,60,CSE\n")

# 3. Check Data Matching
try:
    df_c = pd.read_csv('courses.csv')
    df_g = pd.read_csv('groups.csv')
    
    # Normalize
    df_c.columns = [c.strip() for c in df_c.columns]
    df_g.columns = [c.strip() for c in df_g.columns]
    
    print("\n[INFO] Loaded Courses:", len(df_c))
    print("[INFO] Loaded Groups:", len(df_g))
    
    # Check Headers
    if 'degree' not in df_c.columns:
        print("[FAIL] 'degree' column missing in courses.csv")
    else:
        print("[PASS] 'degree' column exists.")

except Exception as e:
    print(f"\n[CRITICAL ERROR] Could not read CSV files: {e}")
    print("Hint: Close these files if they are open in Excel!")