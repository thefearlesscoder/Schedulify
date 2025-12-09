# ##########
# from pyngrok import ngrok
# ngrok.set_auth_token("33su88tN16YcXYDQ4afJcEESgAj_3itLTjehwDzJebaoPnGae")
# source venv/bin/activate
# from fastapi import FastAPI, UploadFile, File, Form
# from fastapi.middleware.cors import CORSMiddleware
# import nest_asyncio, uvicorn, pandas as pd, io
# from typing import Optional
# import numpy as np
# import random
# from collections import defaultdict
# from deap import base, creator, tools, algorithms
# ##########

# # FastAPI app setup
# app = FastAPI()
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# # --- Global Data ---
# DATA = {
#     "departments": None,
#     "courses": None,
#     "rooms": None,
#     "teachers": None,
#     "timetable": None
# }

# @app.get("/status")
# async def status():
#     return {
#         "departments_loaded": DATA["departments"] is not None,
#         "courses_loaded": DATA["courses"] is not None,
#         "rooms_loaded": DATA["rooms"] is not None,
#         "teachers_loaded": DATA["teachers"] is not None,
#         "timetable_ready": DATA["timetable"] is not None
#     }

# # --- CSV Upload ---
# @app.post("/upload")
# async def upload_files(
#     departments: Optional[UploadFile] = File(None),
#     courses: Optional[UploadFile] = File(None),
#     rooms: Optional[UploadFile] = File(None),
#     teachers: Optional[UploadFile] = File(None),
# ):
#     def read_csv(file):
#         return pd.read_csv(io.BytesIO(file.file.read())) if file else None

#     if departments: DATA["departments"] = read_csv(departments)
#     if courses: DATA["courses"] = read_csv(courses)
#     if rooms: DATA["rooms"] = read_csv(rooms)
#     if teachers: DATA["teachers"] = read_csv(teachers)

#     return {"message": "Files uploaded successfully."}

# # --- Generate Timetable ---
# @app.post("/generate")
# async def generate_timetable():
#     if not all(df is not None for df in [DATA["courses"], DATA["rooms"], DATA["teachers"]]):
#         return {"error": "Please upload all CSVs first."}

#     courses_df = DATA["courses"]
#     rooms_df = DATA["rooms"]
#     teachers_df = DATA["teachers"]

#     # --- Evolutionary Algorithm (Simplified Example) ---
#     rooms = list(rooms_df["Room Code"])
#     time_slots = [f"Slot {i+1}" for i in range(20)]

#     def generate_individual():
#         return [random.choice(rooms) + "@" + random.choice(time_slots)
#                 for _ in range(len(courses_df))]

#     def evaluate(individual):
#         conflicts = len(individual) - len(set(individual))
#         return (conflicts,)

#     creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
#     creator.create("Individual", list, fitness=creator.FitnessMin)
#     toolbox = base.Toolbox()
#     toolbox.register("individual", tools.initIterate, creator.Individual, generate_individual)
#     toolbox.register("population", tools.initRepeat, list, toolbox.individual)
#     toolbox.register("mate", tools.cxTwoPoint)
#     toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)
#     toolbox.register("select", tools.selTournament, tournsize=3)
#     toolbox.register("evaluate", evaluate)

#     population = toolbox.population(n=30)
#     algorithms.eaSimple(population, toolbox, cxpb=0.7, mutpb=0.2, ngen=30, verbose=False)

#     best = tools.selBest(population, 1)[0]
#     schedule = [
#         {
#             "course": row["Course Code"],
#             "room_slot": best[i],
#             "teacher": random.choice(teachers_df["Teacher Name"].tolist())
#         }
#         for i, row in courses_df.iterrows()
#     ]

#     DATA["timetable"] = pd.DataFrame(schedule)
#     return {"timetable": schedule}


# @app.get("/timetable")
# async def get_timetable():
#     if DATA["timetable"] is None:
#         return {"error": "Timetable not generated yet."}
#     return DATA["timetable"].to_dict(orient="records")

# # --- Run with ngrok ---
# ngrok_tunnel = ngrok.connect(8000)
# print("Public URL:", ngrok_tunnel.public_url)

# nest_asyncio.apply()
# uvicorn.run(app, port=8000)


##########
from pyngrok import ngrok
# keep your token (replace if different)
ngrok.set_auth_token("33su88tN16YcXYDQ4afJcEESgAj_3itLTjehwDzJebaoPnGae")

from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import nest_asyncio, uvicorn, pandas as pd, io, os, tempfile
from typing import Optional, List, Dict, Any
import numpy as np
import random
from collections import defaultdict
from deap import base, creator, tools, algorithms
import traceback
from fastapi.responses import FileResponse
import os
import tempfile
import pandas as pd
from fastapi.responses import JSONResponse
##########

# FastAPI app setup
app = FastAPI(title="GA Timetable Generator")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Global Data ---
DATA = {
    "departments": None,
    "courses": None,
    "rooms": None,
    "teachers": None,
    "timetable": None
}

@app.get("/status")
async def status():
    return {
        "departments_loaded": DATA["departments"] is not None,
        "courses_loaded": DATA["courses"] is not None,
        "rooms_loaded": DATA["rooms"] is not None,
        "teachers_loaded": DATA["teachers"] is not None,
        "timetable_ready": DATA["timetable"] is not None
    }

# --- CSV Upload ---
@app.post("/upload")
async def upload_files(
    departments: Optional[UploadFile] = File(None),
    courses: Optional[UploadFile] = File(None),
    rooms: Optional[UploadFile] = File(None),
    teachers: Optional[UploadFile] = File(None),
):
    """
    Accepts CSVs for departments, courses, rooms, teachers.
    Expected minimal columns (flexible handling implemented):
      - courses: must include Course Code (or course_code), Course Name, Department, Semester, Students, Hours
      - rooms: must include Room Code (or room_code), Capacity
      - teachers: either:
            * rows with Teacher Name and Course Code (one mapping per row), or
            * rows with Teacher Name and Courses (comma-separated course codes)
    """
    def read_csv_file(upfile: UploadFile) -> pd.DataFrame:
        raw = upfile.file.read()
        upfile.file.seek(0)
        try:
            return pd.read_csv(io.BytesIO(raw))
        except Exception:
            # try with pandas default engine fallback
            return pd.read_csv(io.StringIO(raw.decode('utf-8', errors='ignore')))

    if departments:
        DATA["departments"] = read_csv_file(departments)
    if courses:
        DATA["courses"] = read_csv_file(courses)
    if rooms:
        DATA["rooms"] = read_csv_file(rooms)
    if teachers:
        DATA["teachers"] = read_csv_file(teachers)

    return {"message": "Files uploaded successfully."}

# --- Helper: normalize column names ---
def _col_lookup(df: pd.DataFrame, candidates: List[str]) -> Optional[str]:
    if df is None:
        return None
    cols = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols:
            return cols[cand.lower()]
    return None

# --- Generate Timetable (upgraded GA using uploaded CSVs + constraints) ---
@app.post("/generate")
async def generate_timetable(
    pop_size: int = 300,
    cxpb: float = 0.8,
    mutpb: float = 0.2,
    ngen: int = 200,
    randseed: Optional[int] = None
):
    """
    Generates a timetable using a GA (DEAP).
    You can pass GA parameters as query params. This runs synchronously and returns
    the generated timetable as JSON along with a penalty/fintess score.
    """
    if randseed is not None:
        random.seed(randseed)
        np.random.seed(randseed)

    # Basic validation of uploads
    if not all(df is not None for df in [DATA["courses"], DATA["rooms"], DATA["teachers"]]):
        return {"error": "Please upload courses, rooms and teachers CSVs first."}

    try:
        courses_df: pd.DataFrame = DATA["courses"].copy()
        rooms_df: pd.DataFrame = DATA["rooms"].copy()
        teachers_df: pd.DataFrame = DATA["teachers"].copy()
    except Exception as e:
        return {"error": "Failed to read uploaded CSVs.", "detail": str(e)}

    # --- Normalize required column names (flexible) ---
    # Courses columns
    col_course_code = _col_lookup(courses_df, ["Course Code", "course_code", "courseid", "course id", "code"])
    col_course_name = _col_lookup(courses_df, ["Course Name", "course_name", "name", "title"])
    col_dept = _col_lookup(courses_df, ["Department", "department", "dept"])
    col_sem = _col_lookup(courses_df, ["Semester", "semester", "sem"])
    col_students = _col_lookup(courses_df, ["Students", "students", "enrollment", "capacity"])
    col_hours = _col_lookup(courses_df, ["Hours", "hours", "lecture_hours", "hrs"])

    required_course_cols = [col_course_code, col_course_name, col_dept, col_sem, col_students, col_hours]
    if any(c is None for c in required_course_cols):
        return {"error": "Courses CSV missing required columns. Required: Course Code, Course Name, Department, Semester, Students, Hours."}

    # Rooms columns
    col_room_code = _col_lookup(rooms_df, ["Room Code", "room_code", "room", "code"])
    col_room_capacity = _col_lookup(rooms_df, ["Capacity", "capacity", "cap", "seats"])
    if col_room_code is None or col_room_capacity is None:
        return {"error": "Rooms CSV missing required columns. Required: Room Code, Capacity."}

    # Teachers columns - be flexible
    col_teacher_name = _col_lookup(teachers_df, ["Teacher Name", "teacher_name", "name", "teacher"])
    col_teacher_courses = _col_lookup(teachers_df, ["Courses", "courses", "course_codes", "course code", "course_code", "Course Code", "Course_Code"])
    col_teacher_course_single = _col_lookup(teachers_df, ["Course Code", "course_code", "course", "course_code_mapping"])

    if col_teacher_name is None:
        return {"error": "Teachers CSV must include a Teacher Name column."}

    # --- Build dictionaries used by the GA ---
    # COURSES dict
    COURSES: Dict[str, Dict[str, Any]] = {}
    for _, r in courses_df.iterrows():
        cid = str(r[col_course_code]).strip()
        try:
            students = int(r[col_students])
        except Exception:
            students = int(float(r[col_students])) if pd.notna(r[col_students]) else 0
        try:
            hours = int(r[col_hours])
        except Exception:
            hours = int(float(r[col_hours])) if pd.notna(r[col_hours]) else 1
        COURSES[cid] = {
            "name": str(r[col_course_name]) if pd.notna(r[col_course_name]) else cid,
            "dept": str(r[col_dept]) if pd.notna(r[col_dept]) else "",
            "semester": int(r[col_sem]) if pd.notna(r[col_sem]) else 1,
            "students": max(1, students),
            "hours": max(1, hours)
        }

    # ROOMS dict
    ROOMS: Dict[str, Dict[str, Any]] = {}
    for _, r in rooms_df.iterrows():
        rid = str(r[col_room_code]).strip()
        try:
            cap = int(r[col_room_capacity])
        except Exception:
            cap = int(float(r[col_room_capacity])) if pd.notna(r[col_room_capacity]) else 0
        ROOMS[rid] = {"capacity": max(0, cap)}

    # TEACHERS dict (map teacher -> list of courses they can teach)
    TEACHERS: Dict[str, Dict[str, Any]] = defaultdict(lambda: {"courses": []})
    # Case 1: teachers_df has a column with multiple courses comma-separated
    if col_teacher_courses is not None:
        for _, r in teachers_df.iterrows():
            tname = str(r[col_teacher_name]).strip()
            raw = r[col_teacher_courses]
            if pd.isna(raw):
                continue
            if isinstance(raw, str):
                codes = [c.strip() for c in raw.split(",") if c.strip()]
            elif isinstance(raw, (list, tuple)):
                codes = [str(x).strip() for x in raw]
            else:
                codes = [str(raw).strip()]
            for c in codes:
                if c:
                    TEACHERS[tname]["courses"].append(c)
    # Case 2: teachers_df has one mapping per row (Teacher Name + Course Code)
    elif col_teacher_course_single is not None:
        for _, r in teachers_df.iterrows():
            tname = str(r[col_teacher_name]).strip()
            raw = r[col_teacher_course_single]
            if pd.isna(raw):
                continue
            TEACHERS[tname]["courses"].append(str(raw).strip())
    else:
        # If no course mapping found, assume teacher CSV contains only names.
        # We'll allow any teacher to be assigned to any course (fallback).
        for _, r in teachers_df.iterrows():
            tname = str(r[col_teacher_name]).strip()
            TEACHERS[tname]["courses"] = list(COURSES.keys())

    # If TEACHERS is empty, generate placeholder teachers from teacher names column
    if not TEACHERS:
        for _, r in teachers_df.iterrows():
            tname = str(r[col_teacher_name]).strip()
            TEACHERS[tname]["courses"] = list(COURSES.keys())

    # --- TIMESLOTS and LECTURE LIST ---
    # Standard weekly slots (Mon-Fri) 9-13, 14-18 (skip 13-14). Generate flexible labels.
    DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri']
    HOURS = [9,10,11,12,14,15,16,17]  # 8 slots per day -> 40 total
    TIMESLOTS = [f"{d}_{h:02d}-{h+1:02d}" for d in DAYS for h in HOURS]

    # Flatten lectures: each course appears 'hours' times (each hour is a separate lecture entity)
    LECTURE_LIST: List[str] = []
    for cid, details in COURSES.items():
        for _ in range(details['hours']):
            LECTURE_LIST.append(cid)

    if len(LECTURE_LIST) == 0:
        return {"error": "No lectures to schedule (check 'Hours' column in courses CSV)."}

    # --- Fitness function with hard/soft constraints ---
    def evaluate_timetable(individual):
        """
        Individual: list of tuples (course_id, teacher, room, timeslot)
        Returns: (penalty,)
        Hard violations multiply by large factor.
        """
        hard_violations = 0
        soft_violations = 0

        teacher_schedule = defaultdict(set)
        room_schedule = defaultdict(set)
        student_group_schedule = defaultdict(set)

        for gene in individual:
            course_id, teacher, room, timeslot = gene
            if course_id not in COURSES:
                # heavy penalty for completely invalid course assignment
                hard_violations += 10
                continue
            c = COURSES[course_id]

            # H1: teacher conflict (same teacher two lectures same timeslot)
            if timeslot in teacher_schedule[teacher]:
                hard_violations += 1
            teacher_schedule[teacher].add(timeslot)

            # H2: room conflict
            if timeslot in room_schedule[room]:
                hard_violations += 1
            room_schedule[room].add(timeslot)

            # H3: student group conflict (dept+sem)
            student_group = (c['dept'], c['semester'])
            if timeslot in student_group_schedule[student_group]:
                hard_violations += 1
            student_group_schedule[student_group].add(timeslot)

            # H4: room capacity
            if room not in ROOMS or c['students'] > ROOMS[room]['capacity']:
                hard_violations += 1

            # Soft: prefer teacher assigned to courses they can teach (if teacher-course mapping exists)
            if teacher in TEACHERS and c['name'] is not None:
                if c['name'] and course_id not in TEACHERS[teacher]['courses']:
                    # If teacher cannot teach this course, small penalty (but allow)
                    soft_violations += 1

        total_penalty = hard_violations * 1000 + soft_violations
        return (total_penalty,)

    # --- DEAP setup (guard against re-creation of creator names) ---
    try:
        # if these were already created in the interpreter, this will raise; ignore then
        creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    except Exception:
        pass
    try:
        creator.create("Individual", list, fitness=creator.FitnessMin)
    except Exception:
        pass

    toolbox = base.Toolbox()

    # gene creator for a specific lecture (course_id)
    def create_gene(course_id: str):
        # valid teachers for this course (from TEACHERS mapping)
        valid_teachers = [t for t, d in TEACHERS.items() if course_id in d['courses']]
        if not valid_teachers:
            # fallback: any teacher
            valid_teachers = list(TEACHERS.keys()) or ["TBD"]
        teacher = random.choice(valid_teachers)

        # choose a room that can potentially fit (prefer rooms with capacity >= students, but allow any)
        suitable_rooms = [r for r, info in ROOMS.items() if info['capacity'] >= COURSES[course_id]['students']]
        if not suitable_rooms:
            suitable_rooms = list(ROOMS.keys()) or ["UNKWN"]
        room = random.choice(suitable_rooms)

        timeslot = random.choice(TIMESLOTS)
        return (course_id, teacher, room, timeslot)

    # Build gene creators list: a function per lecture in LECTURE_LIST
    gene_creators = [ (lambda c=c: create_gene(c)) for c in LECTURE_LIST ]

    toolbox.register("individual", tools.initCycle, creator.Individual, gene_creators, n=1)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)

    toolbox.register("evaluate", evaluate_timetable)
    toolbox.register("mate", tools.cxTwoPoint)
    toolbox.register("select", tools.selTournament, tournsize=3)

    # custom mutate: change teacher/room/timeslot for some genes
    def mutate_timetable(individual, indpb):
        for i in range(len(individual)):
            if random.random() < indpb:
                cid, teacher, room, slot = individual[i]
                choice = random.random()
                if choice < 0.33:
                    # change room (prefer suitable rooms)
                    suitable_rooms = [r for r, info in ROOMS.items() if info['capacity'] >= COURSES[cid]['students']]
                    if suitable_rooms:
                        room = random.choice(suitable_rooms)
                    else:
                        room = random.choice(list(ROOMS.keys()))
                elif choice < 0.66:
                    # change timeslot
                    slot = random.choice(TIMESLOTS)
                else:
                    # change teacher (if alternatives exist)
                    valid_teachers = [t for t, d in TEACHERS.items() if cid in d['courses']]
                    if len(valid_teachers) > 1:
                        teacher = random.choice([t for t in valid_teachers if t != teacher])
                    else:
                        # pick any teacher occasionally
                        teacher = random.choice(list(TEACHERS.keys()))
                individual[i] = (cid, teacher, room, slot)
        return (individual,)

    toolbox.register("mutate", mutate_timetable, indpb=0.1)

    # --- Run the GA ---
    try:
        pop = toolbox.population(n=pop_size)
        hof = tools.HallOfFame(1)
        stats = tools.Statistics(lambda ind: ind.fitness.values)
        stats.register("avg", np.mean)
        stats.register("min", np.min)
        stats.register("max", np.max)

        # Run evolution (silent)
        algorithms.eaSimple(pop, toolbox, cxpb=cxpb, mutpb=mutpb, ngen=ngen, stats=stats, halloffame=hof, verbose=False)

        if len(hof) == 0:
            # fallback: pick best from population
            best = tools.selBest(pop, 1)[0]
        else:
            best = hof[0]

        fitness = best.fitness.values[0]
    except Exception as e:
        traceback_str = traceback.format_exc()
        return {"error": "GA failed", "detail": str(e), "trace": traceback_str}

    # --- Convert best individual into structured timetable (list of dicts) ---
    timetable_list = []
    for gene in best:
        cid, teacher, room, timeslot = gene
        if cid not in COURSES:
            continue
        c = COURSES[cid]
        timetable_list.append({
            "course_code": cid,
            "course_name": c["name"],
            "department": c["dept"],
            "semester": c["semester"],
            "students": c["students"],
            "teacher": teacher,
            "room": room,
            "timeslot": timeslot
        })

    # Save into DATA for /timetable endpoint
    try:
        DATA["timetable"] = pd.DataFrame(timetable_list)
    except Exception:
        DATA["timetable"] = None

    # Return compact response
    return {
        "message": "Timetable generated.",
        "fitness_penalty_score": float(fitness),
        "num_lectures_scheduled": len(timetable_list),
        "example_timetable_rows": timetable_list[:200],  # limit size for response
    }

@app.get("/timetable")
async def get_timetable():
    if DATA["timetable"] is None:
        return {"error": "Timetable not generated yet."}
    return DATA["timetable"].to_dict(orient="records")

@app.get("/download")
async def download_timetable():
    if DATA["timetable"] is None:
        return {"error": "Timetable not generated yet."}
    
    # Save the current timetable to a temporary CSV file
    temp_dir = tempfile.gettempdir()
    csv_path = os.path.join(temp_dir, "generated_timetable.csv")
    DATA["timetable"].to_csv(csv_path, index=False)
    
    # Return the file for download
    return FileResponse(
        csv_path,
        media_type="text/csv",
        filename="timetable.csv"
    )


@app.get("/timetable-json")
async def get_timetable_json():
    if DATA["timetable"] is None:
        return {"error": "Timetable not generated yet."}
    
    # Convert DataFrame to JSON
    return JSONResponse(content=DATA["timetable"].to_dict(orient="records"))

# --- Run with ngrok ---
if __name__ == "__main__":
    try:
        ngrok_tunnel = ngrok.connect(8000)
        print("Public URL:", ngrok_tunnel.public_url)
    except Exception as e:
        print("ngrok failed to start:", e)
    # nest_asyncio lets uvicorn.run work inside notebooks / interactive shells
    nest_asyncio.apply()
    uvicorn.run(app, host="0.0.0.0", port=8000)

