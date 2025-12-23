import sys
import json
import random
import numpy as np
from collections import defaultdict

# DEAP: Distributed Evolutionary Algorithms in Python
from deap import base, creator, tools, algorithms

def run_genetic_algorithm(data):
    """
    This function encapsulates the entire GA process.
    It takes the input data as an argument and returns the best timetable.
    """
    
    # --- 1. Unpack data from the input JSON ---
    COURSES = data['courses']
    TEACHERS = data['teachers']
    ROOMS = data['rooms']
    TIMESLOTS = data['timeslots']
    TEACHER_PREFERENCES = data.get('preferences', {}) # Use .get for optional keys

    # A flat list of every single lecture hour that needs to be scheduled
    LECTURE_LIST = [course_id for course_id, details in COURSES.items() for _ in range(details['hours'])]

    # --- 2. The Fitness Function (Now with Soft Constraints) ---
    def evaluate_timetable(individual):
        hard_violations = 0
        soft_violations = 0
        teacher_schedule = defaultdict(list)
        room_schedule = defaultdict(list)
        student_group_schedule = defaultdict(list)

        for course_id, teacher, room, timeslot in individual:
            course_details = COURSES[course_id]
            if course_details['students'] > ROOMS[room]['capacity']:
                hard_violations += 1
            if timeslot in teacher_schedule[teacher]:
                hard_violations += 1
            teacher_schedule[teacher].append(timeslot)
            if timeslot in room_schedule[room]:
                hard_violations += 1
            room_schedule[room].append(timeslot)
            student_group = (course_details['dept'], course_details['semester'])
            if timeslot in student_group_schedule[student_group]:
                hard_violations += 1
            student_group_schedule[student_group].append(timeslot)

            if teacher in TEACHER_PREFERENCES:
                prefs = TEACHER_PREFERENCES[teacher]
                if prefs.get('preferred_rooms') and room not in prefs['preferred_rooms']:
                    soft_violations += 1
                if prefs.get('preferred_slots') and timeslot not in prefs['preferred_slots']:
                    soft_violations += 1
        
        total_penalty = (hard_violations * 1000) + soft_violations
        return (total_penalty,)

    # --- 3. Configure the Genetic Algorithm with DEAP ---
    creator.create("FitnessMin", base.Fitness, weights=(-1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMin)
    toolbox = base.Toolbox()

    def create_gene(course_id):
        valid_teachers = [t for t, details in TEACHERS.items() if course_id in details['courses']]
        if not valid_teachers:
            # Print errors to stderr so they don't corrupt the JSON output
            print(f"Error: No teacher found for course: {course_id}", file=sys.stderr)
            return None
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
        for i in range(len(individual)):
            if random.random() < indpb:
                course_id, teacher, room, timeslot = individual[i]
                if random.random() < 0.5:
                    individual[i] = (course_id, teacher, random.choice(list(ROOMS.keys())), timeslot)
                else:
                    individual[i] = (course_id, teacher, room, random.choice(TIMESLOTS))
        return individual,

    toolbox.register("mutate", mutate_timetable, indpb=0.1)

    # --- 4. Run the GA ---
    POP_SIZE = 500  # Adjust as needed
    NGEN = 500      # Adjust as needed
    
    pop = toolbox.population(n=POP_SIZE)
    hof = tools.HallOfFame(1)
    
    # We send progress to stderr
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("min", np.min)
    
    # The verbose parameter in eaSimple prints to stdout, which we don't want.
    # We can create a custom loop to print to stderr if needed, but for simplicity we omit it here.
    algorithms.eaSimple(pop, toolbox, cxpb=0.8, mutpb=0.2, ngen=NGEN,
                        stats=stats, halloffame=hof, verbose=False) # verbose=False is key

    if hof:
        return hof[0], hof[0].fitness.values[0]
    else:
        return None, -1

if __name__ == "__main__":
    # 1. Read data from standard input
    input_data = json.load(sys.stdin)
    
    # 2. Run the algorithm
    best_timetable, fitness = run_genetic_algorithm(input_data)
    
    # 3. Create a result object and print it to standard output as a JSON string
    if best_timetable:
        result = {
            "status": "success",
            "fitness": fitness,
            "timetable": best_timetable
        }
    else:
        result = {
            "status": "error",
            "message": "No solution found."
        }
        
    print(json.dumps(result))


