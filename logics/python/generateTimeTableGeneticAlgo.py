import random
import numpy as np
from deap import base, creator, tools, algorithms

# --- 1. Define Your Data (Complex Scenario) ---

COURSES = {
    'CS101_A': 55, 'CS101_B': 55, 'MA101_A': 55, 'MA101_B': 55, 'PHY102_A': 50, 'PHY102_B': 50,
    'CS301_A': 50, 'CS302_A': 50, 'CS303_A': 45, 'CS501_A': 45, 'CS502_A': 40, 'CS503_A': 40
}
ROOMS = {
    'LH1': 100, 'LH2': 100, 'CR1': 60, 'CR2': 60, 'CR3': 45, 'LAB1': 55
}
TEACHERS = {
    'PROF_A': ['CS501_A', 'CS301_A'], 'PROF_B': ['CS502_A', 'CS101_A'],
    'PROF_C': ['CS503_A', 'CS301_A'], 'ASOC_D': ['CS101_A', 'CS101_B'],
    'ASOC_E': ['CS302_A', 'CS303_A'], 'ASOC_F': ['MA101_A', 'MA101_B'],
    'ASOC_G': ['PHY102_A', 'PHY102_B']
}
TIMESLOTS = [
    'Mon_09-10', 'Mon_10-11', 'Mon_11-12', 'Mon_12-01', 'Tue_09-10', 'Tue_10-11',
    'Tue_11-12', 'Tue_12-01', 'Wed_09-10', 'Wed_10-11', 'Wed_11-12', 'Wed_12-01',
    'Thu_09-10', 'Thu_10-11', 'Thu_11-12', 'Thu_12-01', 'Fri_09-10', 'Fri_10-11',
    'Fri_11-12', 'Fri_12-01'
]
TEACHER_PREFERENCES = {
    'PROF_A': {'preferred_slots': [t for t in TIMESLOTS if '09-10' in t or '10-11' in t]},
    'PROF_B': {'preferred_slots': [t for t in TIMESLOTS if 'Mon' not in t]}
}

# --- 2. The Fitness Function ---
def evaluate_timetable(individual):
    hard_violations = 0
    soft_violations = 0
    teacher_schedule = {}
    room_schedule = {}
    for course, teacher, room, timeslot in individual:
        if teacher not in teacher_schedule: teacher_schedule[teacher] = []
        if timeslot in teacher_schedule[teacher]: hard_violations += 1
        teacher_schedule[teacher].append(timeslot)
        if room not in room_schedule: room_schedule[room] = []
        if timeslot in room_schedule[room]: hard_violations += 1
        room_schedule[room].append(timeslot)
        if COURSES.get(course, 0) > ROOMS.get(room, 0): hard_violations += 1
        if teacher in TEACHER_PREFERENCES and timeslot not in TEACHER_PREFERENCES[teacher]['preferred_slots']:
            soft_violations += 1
    return ((hard_violations * 1000) + soft_violations,)

# --- 3. Configure the Genetic Algorithm ---
creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
creator.create("Individual", list, fitness=creator.FitnessMin)
toolbox = base.Toolbox()

def get_valid_teacher(course_id):
    valid_teachers = [t for t, c in TEACHERS.items() if course_id in c]
    if not valid_teachers: raise ValueError(f"No teacher for course: {course_id}")
    return random.choice(valid_teachers)

toolbox.register("attr_gene", lambda c: (c, get_valid_teacher(c), random.choice(list(ROOMS.keys())), random.choice(list(TIMESLOTS))))

# ** THE CORRECTION IS HERE **
# Create a list of zero-argument functions (lambdas) for gene creation
gene_creators = [lambda c=c: toolbox.attr_gene(c) for c in COURSES.keys()]
toolbox.register("individual", tools.initCycle, creator.Individual, gene_creators, n=1)
toolbox.register("population", tools.initRepeat, list, toolbox.individual)

def safe_crossover(ind1, ind2):
    return (ind1, ind2) if len(ind1) < 2 else tools.cxTwoPoint(ind1, ind2)

def mutate_timetable(individual, indpb):
    for i in range(len(individual)):
        if random.random() < indpb:
            course, teacher, room, timeslot = individual[i]
            if random.random() < 0.5:
                individual[i] = (course, teacher, random.choice(list(ROOMS.keys())), timeslot)
            else:
                individual[i] = (course, teacher, room, random.choice(list(TIMESLOTS)))
    return individual,

toolbox.register("evaluate", evaluate_timetable)
toolbox.register("mate", safe_crossover)
toolbox.register("mutate", mutate_timetable, indpb=0.1)
toolbox.register("select", tools.selTournament, tournsize=3)

# --- 4. Display Function ---
def display_timetable_grid(timetable):
    print("\n" + "="*80)
    print(" " * 30 + "OPTIMIZED TIMETABLE" + " " * 30)
    print("="*80)
    header = f"| {'TIME SLOT':<12} | {'COURSE':<10} | {'STUDENTS':<8} | {'ROOM':<6} | {'CAPACITY':<8} | {'TEACHER':<8} |"
    print(header)
    print("-"*len(header))

    for course, teacher, room, timeslot in sorted(timetable, key=lambda x: x[3]):
        students = COURSES.get(course, '?')
        capacity = ROOMS.get(room, '?')
        row = f"| {timeslot:<12} | {course:<10} | {str(students):<8} | {room:<6} | {str(capacity):<8} | {teacher:<8} |"
        print(row)

    print("="*80)

# --- 5. Main Execution Block ---
def main():
    if not all([COURSES, TEACHERS, ROOMS, TIMESLOTS]):
        print("Error: Data dictionaries must not be empty.")
        return

    pop = toolbox.population(n=300)
    hof = tools.HallOfFame(1)
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)

    algorithms.eaSimple(pop, toolbox, cxpb=0.7, mutpb=0.2, ngen=500,
                        stats=stats, halloffame=hof, verbose=True)

    if hof:
        best_timetable = hof[0]
        display_timetable_grid(best_timetable)
        print(f"\nFinal Fitness (Penalty Score): {best_timetable.fitness.values[0]}")
        print("A lower score is better. A score near 0 means a near-perfect timetable.")
    else:
        print("No valid solution found.")

if __name__ == "__main__":
    main()