import random
import numpy as np
from collections import defaultdict

# DEAP: Distributed Evolutionary Algorithms in Python
from deap import base, creator, tools, algorithms

# --- 1. Define Your Data Structures (Fully updated from PDF Schedule) ---

# Departments and the semesters running in each
DEPARTMENTS = {
    'BT': {'semesters': [1, 3, 5, 7], 'name': 'Biotechnology'},
    'CH': {'semesters': [1, 3, 5, 7], 'name': 'Chemical Engg.'},
    'CV': {'semesters': [1, 3, 5, 7], 'name': 'Civil Engg.'},
    'CS': {'semesters': [1, 3, 5, 7], 'name': 'Computer Science & Engg.'},
    'EE': {'semesters': [1, 3, 5, 7], 'name': 'Electrical Engg.'},
    'EC': {'semesters': [1, 3, 5, 7], 'name': 'Electronics & Communication Engg.'},
    'ME': {'semesters': [1, 3, 5, 7], 'name': 'Mechanical Engg.'},
    'PI': {'semesters': [1, 3, 5, 7], 'name': 'Production and Industrial Engg.'},
    'AM': {'semesters': [1, 3, 5], 'name': 'Engineering & Computational Mechanics'},
    'MT': {'semesters': [1, 3], 'name': 'Materials Engineering'}
}

# All courses to be scheduled, fully derived from the PDF
COURSES = {
    # SEMESTER 1
    'CYN11502': {'name': 'Engineering Chemistry-II', 'dept': 'BT', 'semester': 1, 'students': 70, 'hours': 4},
    'PHN11501': {'name': 'Engineering Physics-I', 'dept': 'CS', 'semester': 1, 'students': 70, 'hours': 4},
    'EEN11102': {'name': 'Electrical Measurement', 'dept': 'EE', 'semester': 1, 'students': 70, 'hours': 3},
    'IDN11600': {'name': 'Environment & Climate Change', 'dept': 'CV', 'semester': 1, 'students': 70, 'hours': 3},
    'CSN11102': {'name': 'Intro to Computer Organization', 'dept': 'CS', 'semester': 1, 'students': 70, 'hours': 4},
    'HSN11600': {'name': 'Professional Communication', 'dept': 'CH', 'semester': 1, 'students': 70, 'hours': 3},
    'CSN11103': {'name': 'Discrete Mathematics', 'dept': 'CS', 'semester': 1, 'students': 70, 'hours': 4},
    'BTN11101': {'name': 'Basics of Bio Manufacturing', 'dept': 'BT', 'semester': 1, 'students': 70, 'hours': 3},
    'CHN11101': {'name': 'Chemical Process Principles', 'dept': 'CH', 'semester': 1, 'students': 70, 'hours': 4},
    'CEN11101': {'name': 'Building Engineering', 'dept': 'CV', 'semester': 1, 'students': 70, 'hours': 4},
    'CSN11101': {'name': 'Computer Programming', 'dept': 'CS', 'semester': 1, 'students': 70, 'hours': 4},
    'EEN11101': {'name': 'Essentials of Electrical Engg', 'dept': 'EE', 'semester': 1, 'students': 70, 'hours': 4},
    'BTN11102': {'name': 'Intro Cell & Molecular Biology', 'dept': 'BT', 'semester': 1, 'students': 70, 'hours': 3},
    'CHN11102': {'name': 'Engg Thermodynamics (Chem)', 'dept': 'CH', 'semester': 1, 'students': 70, 'hours': 4},
    'CEN11102': {'name': 'Plumbing and Sanitation', 'dept': 'CV', 'semester': 1, 'students': 70, 'hours': 3},
    'CSN11601': {'name': 'Intro to AI & ML', 'dept': 'CS', 'semester': 1, 'students': 70, 'hours': 3},
    'MEN11602': {'name': 'Workshop & Mfg Process', 'dept': 'ME', 'semester': 1, 'students': 70, 'hours': 3},
    'EAN11700': {'name': 'Professional Ethics', 'dept': 'CS', 'semester': 1, 'students': 70, 'hours': 2},
    'MAN11101': {'name': 'Mathematics-I', 'dept': 'CS', 'semester': 1, 'students': 70, 'hours': 5},
    'MEN11101': {'name': 'Engg Thermodynamics (Mech)', 'dept': 'ME', 'semester': 1, 'students': 70, 'hours': 4},
    'PIN11101': {'name': 'Fluids & Thermal Engineering', 'dept': 'PI', 'semester': 1, 'students': 70, 'hours': 4},
    'AMN11102': {'name': 'Engineering Mechanics', 'dept': 'AM', 'semester': 1, 'students': 70, 'hours': 4},
    'ECN11102': {'name': 'Digital Electronics', 'dept': 'EC', 'semester': 1, 'students': 70, 'hours': 4},
    'ECN11103': {'name': 'Electronics Workshop', 'dept': 'EC', 'semester': 1, 'students': 70, 'hours': 3},
    'ECN11101': {'name': 'Basic Electronics', 'dept': 'EC', 'semester': 1, 'students': 70, 'hours': 4},
    'AMN11101': {'name': 'Materials Science & Engg', 'dept': 'ME', 'semester': 1, 'students': 70, 'hours': 4},
    'AMN11103': {'name': 'Intro to Materials Engg', 'dept': 'MT', 'semester': 1, 'students': 70, 'hours': 4},
    
    # SEMESTER 3
    'MAN13102': {'name': 'Biostatics', 'dept': 'BT', 'semester': 3, 'students': 65, 'hours': 4},
    'MAN13101': {'name': 'Numerical Methods', 'dept': 'CH', 'semester': 3, 'students': 65, 'hours': 4},
    'AMN13102': {'name': 'Solid Mechanics', 'dept': 'CV', 'semester': 3, 'students': 65, 'hours': 4},
    'CSN13101': {'name': 'Object Oriented Programming', 'dept': 'CS', 'semester': 3, 'students': 65, 'hours': 4},
    'CSN13404': {'name': 'Data Structure & OS (ECE)', 'dept': 'EC', 'semester': 3, 'students': 65, 'hours': 4},
    'AMN13101': {'name': 'Mechanics of Materials', 'dept': 'ME', 'semester': 3, 'students': 65, 'hours': 4},
    'AMN13107': {'name': 'Mechanics of Solids', 'dept': 'AM', 'semester': 3, 'students': 65, 'hours': 4},
    'BTN13103': {'name': 'Biochemical Engineering', 'dept': 'BT', 'semester': 3, 'students': 65, 'hours': 3},
    'AMN13103': {'name': 'Fluid Mechanics & Hydraulics', 'dept': 'CV', 'semester': 3, 'students': 65, 'hours': 4},
    'ECN13401': {'name': 'Analog & Digital Electronics', 'dept': 'EE', 'semester': 3, 'students': 65, 'hours': 4},
    'EEN13401': {'name': 'Network & System', 'dept': 'EE', 'semester': 3, 'students': 65, 'hours': 4},
    'MEN13102': {'name': 'Heat & Mass Transfer', 'dept': 'ME', 'semester': 3, 'students': 65, 'hours': 4},
    'PIN13103': {'name': 'Operation Research', 'dept': 'PI', 'semester': 3, 'students': 65, 'hours': 4},
    'MAN13103': {'name': 'Linear Algebra & Discrete Math', 'dept': 'AM', 'semester': 3, 'students': 65, 'hours': 4},
    'CHN13103': {'name': 'Chem Engg Thermodynamics', 'dept': 'CH', 'semester': 3, 'students': 65, 'hours': 4},
    'CSN13400': {'name': 'Analysis of Algorithms', 'dept': 'CS', 'semester': 3, 'students': 65, 'hours': 4},
    'ECN13103': {'name': 'Microprocessor & App', 'dept': 'EC', 'semester': 3, 'students': 65, 'hours': 4},
    'AMN13109': {'name': 'Thermo Fluids Engineering', 'dept': 'AM', 'semester': 3, 'students': 65, 'hours': 4},
    'BTN13101': {'name': 'Microbiology', 'dept': 'BT', 'semester': 3, 'students': 65, 'hours': 3},
    'CHN13104': {'name': 'Heat Transfer Operation', 'dept': 'CH', 'semester': 3, 'students': 65, 'hours': 4},
    'CEN13103': {'name': 'Surveying', 'dept': 'CV', 'semester': 3, 'students': 65, 'hours': 3},
    'CSN13401': {'name': 'Computer Architecture', 'dept': 'CS', 'semester': 3, 'students': 65, 'hours': 4},
    'EEN13102': {'name': 'Simulation Tools for EE', 'dept': 'EE', 'semester': 3, 'students': 65, 'hours': 3},
    'ECN13102': {'name': 'Signals & Systems (ECE)', 'dept': 'EC', 'semester': 3, 'students': 65, 'hours': 4},
    'AMN13104': {'name': 'Fluid Mech & Hydraulic Machines', 'dept': 'ME', 'semester': 3, 'students': 65, 'hours': 4},
    'HSN13601': {'name': 'Management Concept', 'dept': 'ME', 'semester': 3, 'students': 65, 'hours': 3},
    'HSN13602': {'name': 'Business Economics', 'dept': 'EE', 'semester': 3, 'students': 65, 'hours': 3},
    'EEN13101': {'name': 'Signals & Systems (EEE)', 'dept': 'EE', 'semester': 3, 'students': 65, 'hours': 4},
    'ECN13101': {'name': 'Electromagnetic Theory', 'dept': 'EC', 'semester': 3, 'students': 65, 'hours': 4},
    'MEN13101': {'name': 'Energy Conversion Tech', 'dept': 'ME', 'semester': 3, 'students': 65, 'hours': 3},

    # SEMESTER 5
    'BTN15101': {'name': 'Bioinformatics', 'dept': 'BT', 'semester': 5, 'students': 60, 'hours': 4},
    'CHN15110': {'name': 'Mass Transfer Operations-II', 'dept': 'CH', 'semester': 5, 'students': 60, 'hours': 4},
    'AMN15101': {'name': 'Structural Analysis-II', 'dept': 'CV', 'semester': 5, 'students': 60, 'hours': 4},
    'EEN15102': {'name': 'Control System-II', 'dept': 'EE', 'semester': 5, 'students': 60, 'hours': 4},
    'CSN15401': {'name': 'Database Management System', 'dept': 'CS', 'semester': 5, 'students': 60, 'hours': 4},
    'ECN15101': {'name': 'Digital Signal Processing', 'dept': 'EC', 'semester': 5, 'students': 60, 'hours': 4},
    'MEN15102': {'name': 'Computer Aided Manufacturing', 'dept': 'ME', 'semester': 5, 'students': 60, 'hours': 3},
    'PIN15101': {'name': 'Comp Aided Manufacturing (PI)', 'dept': 'PI', 'semester': 5, 'students': 60, 'hours': 3},
    'BTN15102': {'name': 'Microbial Biotechnology', 'dept': 'BT', 'semester': 5, 'students': 60, 'hours': 3},
    'CEN15101': {'name': 'Pavement Engineering', 'dept': 'CV', 'semester': 5, 'students': 60, 'hours': 3},
    'EEN15104': {'name': 'Power Electronics', 'dept': 'EE', 'semester': 5, 'students': 60, 'hours': 4},
    'CSN15400': {'name': 'Computer Networks', 'dept': 'CS', 'semester': 5, 'students': 60, 'hours': 4},
    'BTN15103': {'name': 'Genetic Engineering', 'dept': 'BT', 'semester': 5, 'students': 60, 'hours': 3},
    'EEN15103': {'name': 'Power System II', 'dept': 'EE', 'semester': 5, 'students': 60, 'hours': 4},
    'CSN15402': {'name': 'Embedded System', 'dept': 'CS', 'semester': 5, 'students': 60, 'hours': 3},
    'MEN15103': {'name': 'Design of Machine Elements', 'dept': 'ME', 'semester': 5, 'students': 60, 'hours': 4},
    'CSN15101': {'name': 'Software Engg & PM', 'dept': 'CS', 'semester': 5, 'students': 60, 'hours': 3},
    'ECN15104': {'name': 'Electronic Circuit Design', 'dept': 'EC', 'semester': 5, 'students': 60, 'hours': 4},
    'CSN15403': {'name': 'Cryptography & Network Security', 'dept': 'CS', 'semester': 5, 'students': 60, 'hours': 3},
    'MEN15101': {'name': 'Automobile Engineering', 'dept': 'ME', 'semester': 5, 'students': 60, 'hours': 3},

    # SEMESTER 7
    'BTN17101': {'name': 'Quality Assurance', 'dept': 'BT', 'semester': 7, 'students': 50, 'hours': 3},
    'CHN17272': {'name': 'Plant Wide Control', 'dept': 'CH', 'semester': 7, 'students': 50, 'hours': 3},
    'CEN17101': {'name': 'Railway & Airport Engineering', 'dept': 'CV', 'semester': 7, 'students': 50, 'hours': 3},
    'EEN17250': {'name': 'Power System Protection', 'dept': 'EE', 'semester': 7, 'students': 50, 'hours': 4},
    'CSN17101': {'name': 'Image Processing', 'dept': 'CS', 'semester': 7, 'students': 50, 'hours': 3},
    'ECN17102': {'name': 'Nano Electronics', 'dept': 'EC', 'semester': 7, 'students': 50, 'hours': 3},
    'MEN17101': {'name': 'Renewable Energy', 'dept': 'ME', 'semester': 7, 'students': 50, 'hours': 3},
    'PIN17101': {'name': 'Supply Chain Management', 'dept': 'PI', 'semester': 7, 'students': 50, 'hours': 3},
    'CSN17400': {'name': 'Formal Methods', 'dept': 'CS', 'semester': 7, 'students': 50, 'hours': 3},
    'ECN17101': {'name': 'Mobile & Wireless Comm', 'dept': 'EC', 'semester': 7, 'students': 50, 'hours': 3},
    'HSN17602': {'name': 'Business Economics (7th)', 'dept': 'ME', 'semester': 7, 'students': 50, 'hours': 3},
    'CHN17115': {'name': 'Plant Design & Economics', 'dept': 'CH', 'semester': 7, 'students': 50, 'hours': 3},
    'CHN17116': {'name': 'Hazards and Safety', 'dept': 'CH', 'semester': 7, 'students': 50, 'hours': 3},
    'CSN17600': {'name': 'Machine Learning with Python', 'dept': 'CS', 'semester': 7, 'students': 50, 'hours': 3},
    'CEN17102': {'name': 'Earthquake Resistant Design', 'dept': 'CV', 'semester': 7, 'students': 50, 'hours': 3},
}

# Rooms and their capacity (Updated from seating_arrangement.pdf)
ROOMS = {
    'GS-3': {'capacity': 85},
    'GS-4': {'capacity': 86},
    'GS-5': {'capacity': 86},
    'GS-6': {'capacity': 87},
    'GS-7': {'capacity': 88},
    'GS-8': {'capacity': 87},
    'NLHC-1': {'capacity': 202},
    'NLHC-2': {'capacity': 204},
    'FC-5': {'capacity': 90},
    'FEW-1': {'capacity': 79},
    'FEW-15': {'capacity': 68},
    'SEW-1': {'capacity': 77},
    'SEW-7': {'capacity': 146},
    'SEW-8': {'capacity': 143},
    'SEW-9': {'capacity': 56},
    'SEW-10': {'capacity': 66},
    'FN-1': {'capacity': 108},
    'FN-3': {'capacity': 63},
    'FN-4': {'capacity': 63},
    'FE-16': {'capacity': 60},
    'FE-17': {'capacity': 60},
    'FE-18': {'capacity': 61},
    'CSED-NB-2': {'capacity': 60},
    'LHC-2': {'capacity': 49},
    'LHC-5': {'capacity': 45},
    'LHC-6': {'capacity': 45},
    'LHC-7': {'capacity': 45},
    'LHC-8': {'capacity': 45},
    'GW-3': {'capacity': 36},
    'GW-4': {'capacity': 16}
}

# Teachers and the courses they can teach (Generated logically for the new courses)
TEACHERS = {
    'PROF_MATH': {'courses': ['MAN11101', 'MAN13102', 'CSN11103', 'MAN13103', 'MAN13101']},
    'PROF_PHYSICS': {'courses': ['PHN11501']},
    'PROF_CHEMISTRY': {'courses': ['CYN11502']},
    'PROF_COMM': {'courses': ['HSN11600', 'HSN13601']},
    'PROF_ENV': {'courses': ['IDN11600']},
    'PROF_SOCRATES': {'courses': ['EAN11700']},
    
    # CS Professors
    'PROF_TURING': {'courses': ['CSN11101', 'CSN13101', 'CSN13400', 'CSN13404']},
    'PROF_HOPPER': {'courses': ['CSN15401', 'CSN15400', 'CSN15402', 'CSN15101']},
    'PROF_KNUTH': {'courses': ['CSN17101', 'CSN17400', 'CSN15403', 'CSN17600']},
    'PROF_ADA': {'courses': ['CSN11102', 'CSN11601', 'CSN13401']},
    
    # EE Professors
    'PROF_TESLA': {'courses': ['EEN11102', 'EEN11101', 'ECN13401', 'EEN13401']},
    'PROF_EDISON': {'courses': ['EEN15102', 'EEN17250', 'EEN13101', 'EEN15104', 'EEN15103']},
    'PROF_FARADAY': {'courses': ['EEN13102', 'EEN13101']},

    # BT Professors
    'PROF_PASTEUR': {'courses': ['BTN11101', 'BTN13103', 'BTN13101', 'BTN11102']},
    'PROF_FLEMING': {'courses': ['BTN15101', 'BTN15102', 'BTN15103', 'BTN17101']},

    # ME/PI/AM Professors
    'PROF_WATT': {'courses': ['MEN11101', 'AMN11102', 'AMN13101', 'MEN13102', 'CHN11102', 'MEN11602']},
    'PROF_FORD': {'courses': ['PIN13103', 'PIN17101', 'MEN15102', 'MEN17101', 'AMN11101', 'PIN11101']},
    'PROF_NEWTON': {'courses': ['AMN13107', 'AMN13109', 'MEN15103', 'MEN15101']},
    'PROF_ARCHIMEDES': {'courses': ['AMN13103', 'AMN13104', 'MEN13101', 'PIN15101']},
    
    # CV Professors
    'PROF_EIFFEL': {'courses': ['CEN11101', 'IDN11600', 'AMN13102', 'CEN13103', 'CEN11102']},
    'PROF_ROZA': {'courses': ['AMN15101', 'CEN15101', 'CEN17101', 'CEN17102']},

    # CH Professors
    'PROF_NOBEL': {'courses': ['CHN11101', 'CHN15110', 'CHN17272', 'CHN13103', 'CHN13104']},
    'PROF_HABER': {'courses': ['CHN17115', 'CHN17116']},

    # EC Professors
    'PROF_MARCONI': {'courses': ['ECN11101', 'ECN15101', 'ECN17102', 'ECN11102', 'ECN11103']},
    'PROF_BELL': {'courses': ['ECN13103', 'ECN13102', 'ECN13101', 'ECN15104', 'ECN17101']},
    
    # MT Professors
    'PROF_GUTENBERG': {'courses': ['AMN11103']},
    
    # Humanities/Management
    'PROF_DRUCKER': {'courses': ['HSN13602', 'HSN17602']}
}

# Available time slots
TIMESLOTS = [f'{day}_{hr:02d}-{hr+1:02d}' for day in ['Mon', 'Tue', 'Wed', 'Thu', 'Fri'] for hr in range(9, 17) if hr != 13] # 9-1, 2-6

# A flat list of every single lecture hour that needs to be scheduled
LECTURE_LIST = [course_id for course_id, details in COURSES.items() for _ in range(details['hours'])]

# --- 2. The Fitness Function (The Core of the GA) ---

def evaluate_timetable(individual):
    """
    Calculates the fitness of a timetable individual.
    The fitness is a penalty score. Lower is better. A score of 0 is a perfect timetable.
    """
    hard_violations = 0
    
    teacher_schedule = defaultdict(list)
    room_schedule = defaultdict(list)
    student_group_schedule = defaultdict(list)

    for course_id, teacher, room, timeslot in individual:
        course_details = COURSES[course_id]
        
        # H1: Teacher conflict
        if timeslot in teacher_schedule[teacher]:
            hard_violations += 1
        teacher_schedule[teacher].append(timeslot)
        
        # H2: Room conflict
        if timeslot in room_schedule[room]:
            hard_violations += 1
        room_schedule[room].append(timeslot)

        # H3: Student Group conflict
        student_group = (course_details['dept'], course_details['semester'])
        if timeslot in student_group_schedule[student_group]:
            hard_violations += 1
        student_group_schedule[student_group].append(timeslot)

        # H4: Room capacity
        if course_details['students'] > ROOMS[room]['capacity']:
            hard_violations += 1
            
    return (hard_violations,)


# --- 3. Configure the Genetic Algorithm with DEAP ---

creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)

toolbox = base.Toolbox()

def create_gene(course_id):
    """Creates a random valid gene for a given course."""
    valid_teachers = [t for t, details in TEACHERS.items() if course_id in details['courses']]
    if not valid_teachers:
        raise ValueError(f"No teacher found for course: {course_id} - {COURSES[course_id]['name']}")
    teacher = random.choice(valid_teachers)
    room = random.choice(list(ROOMS.keys()))
    timeslot = random.choice(TIMESLOTS)
    return (course_id, teacher, room, timeslot)

gene_creators = [lambda c=c: create_gene(c) for c in LECTURE_LIST]
toolbox.register("individual", tools.initCycle, creator.Individual, gene_creators, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

toolbox.register("evaluate", evaluate_timetable)
toolbox.register("mate", tools.cxTwoPoint)
toolbox.register("select", tools.selTournament, tournsize=3)

def mutate_timetable(individual, indpb):
    """Mutates a timetable by changing the room, timeslot, or teacher of a few lectures."""
    for i in range(len(individual)):
        if random.random() < indpb:
            course_id, teacher, room, timeslot = individual[i]
            
            mutation_type = random.random()
            if mutation_type < 0.33:
                # Mutate room
                individual[i] = (course_id, teacher, random.choice(list(ROOMS.keys())), timeslot)
            elif mutation_type < 0.66:
                # Mutate timeslot
                individual[i] = (course_id, teacher, room, random.choice(TIMESLOTS))
            else:
                # Mutate teacher (if alternatives exist)
                valid_teachers = [t for t, details in TEACHERS.items() if course_id in details['courses']]
                if len(valid_teachers) > 1:
                    new_teacher = random.choice([t for t in valid_teachers if t != teacher])
                    individual[i] = (course_id, new_teacher, room, timeslot)
    return individual,

toolbox.register("mutate", mutate_timetable, indpb=0.1)

# --- 4. Display Functions ---

def display_timetable(timetable, title="CENTRALIZED MASTER TIMETABLE"):
    """Prints a formatted timetable to the console."""
    print("\n" + "="*100)
    print(f"{title:^100}")
    print("="*100)
    
    timetable.sort(key=lambda x: (TIMESLOTS.index(x[3]), x[0]))

    header = f"| {'TIME SLOT':<18} | {'DEPT':<5} | {'SEM':<3} | {'COURSE':<35} | {'ROOM':<10} | {'TEACHER':<17} |"
    print(header)
    print("-" * len(header))

    for course_id, teacher, room, timeslot in timetable:
        details = COURSES[course_id]
        row = (f"| {timeslot:<18} | {details['dept']:<5} | {details['semester']:<3} | "
               f"{details['name']:<35} | {room:<10} | {teacher:<17} |")
        print(row)
    
    print("="*100)

def display_department_timetable(timetable, dept_id, semester=None):
    """Filters and displays the schedule for a specific department."""
    if dept_id not in DEPARTMENTS:
        print(f"\nError: Department '{dept_id}' not found.")
        return
        
    if semester:
        title = f"TIMETABLE FOR DEPT: {DEPARTMENTS[dept_id]['name']}, SEMESTER: {semester}"
        filtered_timetable = [g for g in timetable if COURSES[g[0]]['dept'] == dept_id and COURSES[g[0]]['semester'] == semester]
    else:
        title = f"TIMETABLE FOR DEPT: {DEPARTMENTS[dept_id]['name']} (All Semesters)"
        filtered_timetable = [g for g in timetable if COURSES[g[0]]['dept'] == dept_id]
        
    display_timetable(filtered_timetable, title=title)


# --- 5. Main Execution Block ---
def main():
    # GA Parameters (adjusted for larger problem)
    POP_SIZE = 600
    CXPB = 0.8
    MUTPB = 0.2
    NGEN = 800 # Increased generations

    print("Setting up Genetic Algorithm with data from PDF...")
    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    stats.register("max", np.max)

    print(f"Starting evolution for {len(LECTURE_LIST)} total lecture hours...")
    algorithms.eaSimple(pop, toolbox, cxpb=CXPB, mutpb=MUTPB, ngen=NGEN,
                        stats=stats, halloffame=hof, verbose=True)

    if hof:
        best_timetable = hof[0]
        fitness_score = best_timetable.fitness.values[0]
        
        print("\nEvolution finished.")
        print(f"Best Timetable Fitness (Penalty Score): {fitness_score}")
        print("A score of 0.0 means all hard constraints are met.")
        
        # --- PART 1: Display the generated centralized timetable ---
        display_timetable(best_timetable)
        
        # --- PART 2: Display department-wise timetables by filtering the result ---
        print("\nGenerating department-wise timetables from the master schedule...")
        
        display_department_timetable(best_timetable, 'CS', semester=1)
        display_department_timetable(best_timetable, 'ME', semester=3)
        display_department_timetable(best_timetable, 'BT', semester=5)
        display_department_timetable(best_timetable, 'EE', semester=7)

    else:
        print("No solution found.")


if __name__ == "__main__":
    main()

