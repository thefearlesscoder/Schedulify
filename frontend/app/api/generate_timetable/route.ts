import { type NextRequest, NextResponse } from "next/server"

interface Teacher {
  id: string
  name: string
  subjects: string[]
}

interface Room {
  id: string
  name: string
}

interface Subject {
  id: string
  name: string
}

interface Section {
  id: string
  name: string
}

interface TimeSlot {
  id: string
  start: string
  end: string
}

interface TimetableEntry {
  subject: string
  teacher: string
  room: string
  section: string
}

interface TimetableData {
  [day: string]: {
    [timeSlot: string]: TimetableEntry | null
  }
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

// Simple timetable generation algorithm
function generateTimetable(
  teachers: Teacher[],
  rooms: Room[],
  subjects: Subject[],
  sections: Section[],
  timeSlots: TimeSlot[],
): TimetableData {
  const timetable: TimetableData = {}

  // Initialize empty timetable
  DAYS.forEach((day) => {
    timetable[day] = {}
    timeSlots.forEach((slot) => {
      const timeSlotLabel = `${slot.start} - ${slot.end}`
      timetable[day][timeSlotLabel] = null
    })
  })

  // Track teacher and room availability
  const teacherSchedule: { [teacherId: string]: Set<string> } = {}
  const roomSchedule: { [roomId: string]: Set<string> } = {}

  teachers.forEach((teacher) => {
    teacherSchedule[teacher.id] = new Set()
  })

  rooms.forEach((room) => {
    roomSchedule[room.id] = new Set()
  })

  // Generate random assignments
  let assignmentAttempts = 0
  const maxAttempts = 1000

  DAYS.forEach((day) => {
    timeSlots.forEach((slot) => {
      const timeSlotLabel = `${slot.start} - ${slot.end}`
      const dayTimeKey = `${day}-${timeSlotLabel}`

      // Try to assign a class for each section
      sections.forEach((section) => {
        if (assignmentAttempts >= maxAttempts) return

        // Randomly select a subject
        const availableSubjects = subjects.filter((s) => s.name.trim())
        if (availableSubjects.length === 0) return

        const randomSubject = availableSubjects[Math.floor(Math.random() * availableSubjects.length)]

        // Find teachers who can teach this subject
        const availableTeachers = teachers.filter(
          (teacher) =>
            teacher.subjects.some(
              (s) =>
                s.toLowerCase().includes(randomSubject.name.toLowerCase()) ||
                randomSubject.name.toLowerCase().includes(s.toLowerCase()),
            ) && !teacherSchedule[teacher.id].has(dayTimeKey),
        )

        if (availableTeachers.length === 0) return

        // Find available rooms
        const availableRooms = rooms.filter((room) => !roomSchedule[room.id].has(dayTimeKey))

        if (availableRooms.length === 0) return

        // Make random selections
        const selectedTeacher = availableTeachers[Math.floor(Math.random() * availableTeachers.length)]
        const selectedRoom = availableRooms[Math.floor(Math.random() * availableRooms.length)]

        // Skip if this time slot is already filled for this section
        if (timetable[day][timeSlotLabel] !== null) return

        // Assign the class
        timetable[day][timeSlotLabel] = {
          subject: randomSubject.name,
          teacher: selectedTeacher.name,
          room: selectedRoom.name,
          section: section.name,
        }

        // Mark teacher and room as busy
        teacherSchedule[selectedTeacher.id].add(dayTimeKey)
        roomSchedule[selectedRoom.id].add(dayTimeKey)

        assignmentAttempts++
      })
    })
  })

  return timetable
}

export async function POST(request: NextRequest) {
  try {
    const body = await request.json()
    const { teachers, rooms, subjects, sections, timeSlots } = body

    // Validate input
    if (!teachers || !rooms || !subjects || !sections || !timeSlots) {
      return NextResponse.json({ error: "Missing required fields" }, { status: 400 })
    }

    if (
      teachers.length === 0 ||
      rooms.length === 0 ||
      subjects.length === 0 ||
      sections.length === 0 ||
      timeSlots.length === 0
    ) {
      return NextResponse.json({ error: "All fields must have at least one entry" }, { status: 400 })
    }

    // Simulate processing time
    await new Promise((resolve) => setTimeout(resolve, 2000))

    // Generate timetable
    const timetable = generateTimetable(teachers, rooms, subjects, sections, timeSlots)

    // Format time slots for response
    const formattedTimeSlots = timeSlots.map((slot) => `${slot.start} - ${slot.end}`)

    return NextResponse.json({
      success: true,
      timetable,
      timeSlots: formattedTimeSlots,
    })
  } catch (error) {
    console.error("Error generating timetable:", error)
    return NextResponse.json({ error: "Internal server error" }, { status: 500 })
  }
}
