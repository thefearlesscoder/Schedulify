
#include <bits/stdc++.h>
using namespace std;

struct Slot {
    string day;
    string time;
    string subject;
    string section;
    string teacher;
    string room;
    bool occupied;
};

int main() {
    // Days and 2-hour time slots
    vector<string> days = {"Mon", "Tue", "Wed", "Thu", "Fri"};
    vector<string> times = {"9-11", "11-1", "1-3", "3-5"};

    // Subjects
    vector<string> subjects = {"Math", "Physics", "Chemistry", "DBMS", "OS", "CN"};

    // Teachers (2 per subject → total 12) for testing
    vector<string> teachers = {"T1","T2","T3","T4","T5","T6","T7","T8","T9","T10","T11","T12"};

    //  teacher to subject
    map<string,string> teacherSubject;
    for (int i = 0; i < teachers.size(); i++) {
        teacherSubject[teachers[i]] = subjects[i/2]; // 2 teachers per subject
    }

    // Sections (now 4)
    vector<string> sections = {"SecA", "SecB", "SecC", "SecD"};

    vector<string> rooms = {"Room1", "Room2", "Room3", "Room4"};

    vector<Slot> slots;
    for (auto &d : days) {
        for (auto &t : times) {
            for (auto &r : rooms) {
                slots.push_back({d, t, "", "", "", r, false});
            }
        }
    }

    srand(time(0));

    // Assign subjects for each section
    for (auto &sec : sections) {
        for (int i = 0; i < teachers.size(); i++) {
            string teacher = teachers[i];
            string subj = teacherSubject[teacher];

            // Find a free slot
            while (true) {
                int idx = rand() % slots.size();
                if (!slots[idx].occupied) {
                    // Check if teacher is free in that slot
                    bool clash = false;
                    for (auto &sl : slots) {
                        if (sl.day == slots[idx].day &&
                            sl.time == slots[idx].time &&
                            sl.teacher == teacher &&
                            sl.occupied) {
                            clash = true;
                            break;
                        }
                    }
                    if (!clash) {
                        slots[idx].subject = subj;
                        slots[idx].teacher = teacher;
                        slots[idx].section = sec;
                        slots[idx].occupied = true;
                        break;
                    }
                }
            }
        }
    }

    for (auto &sec : sections) {
        cout << "\n==================== TIMETABLE for " << sec << " ====================\n";
        cout << setw(8) << "Day/Time";
        for (auto &t : times) cout << setw(30) << t;
        cout << "\n";

        for (auto &d : days) {
            cout << setw(8) << d;
            for (auto &t : times) {
                string cell = "--";
                for (auto &sl : slots) {
                    if (sl.day == d && sl.time == t && sl.occupied && sl.section == sec) {
                        cell = sl.subject + " | " + sl.teacher + " | " + sl.room;
                        break;
                    }
                }
                cout << setw(30) << cell;
            }
            cout << "\n";
        }
    }

    return 0;
}
