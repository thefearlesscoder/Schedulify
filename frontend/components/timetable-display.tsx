"use client"

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"

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

interface TimetableDisplayProps {
  timetable: TimetableData
  timeSlots: string[]
}

const DAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]

// Color palette for different subjects
const SUBJECT_COLORS = [
  "bg-blue-100 text-blue-800 border-blue-200",
  "bg-green-100 text-green-800 border-green-200",
  "bg-purple-100 text-purple-800 border-purple-200",
  "bg-orange-100 text-orange-800 border-orange-200",
  "bg-pink-100 text-pink-800 border-pink-200",
  "bg-teal-100 text-teal-800 border-teal-200",
  "bg-indigo-100 text-indigo-800 border-indigo-200",
  "bg-red-100 text-red-800 border-red-200",
  "bg-yellow-100 text-yellow-800 border-yellow-200",
  "bg-cyan-100 text-cyan-800 border-cyan-200",
]

export function TimetableDisplay({ timetable, timeSlots }: TimetableDisplayProps) {
  // Create a mapping of subjects to colors
  const subjectColorMap = new Map<string, string>()
  let colorIndex = 0

  const getSubjectColor = (subject: string) => {
    if (!subjectColorMap.has(subject)) {
      subjectColorMap.set(subject, SUBJECT_COLORS[colorIndex % SUBJECT_COLORS.length])
      colorIndex++
    }
    return subjectColorMap.get(subject)!
  }

  if (!timetable || Object.keys(timetable).length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Timetable</CardTitle>
        </CardHeader>
        <CardContent>
          <p className="text-muted-foreground text-center py-8">
            No timetable generated yet. Fill in the form above and click "Generate Timetable".
          </p>
        </CardContent>
      </Card>
    )
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>Generated Timetable</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="overflow-x-auto">
          <table className="w-full border-collapse">
            <thead>
              <tr>
                <th className="border border-border p-3 bg-muted font-semibold text-left min-w-24">Day</th>
                {timeSlots.map((slot) => (
                  <th key={slot} className="border border-border p-3 bg-muted font-semibold text-center min-w-48">
                    {slot}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {DAYS.map((day) => (
                <tr key={day}>
                  <td className="border border-border p-3 bg-muted/50 font-medium">{day}</td>
                  {timeSlots.map((slot) => {
                    const entry = timetable[day]?.[slot]

                    return (
                      <td key={`${day}-${slot}`} className="border border-border p-2">
                        {entry ? (
                          <div className={`p-3 rounded-lg border-2 text-sm ${getSubjectColor(entry.subject)}`}>
                            <div className="font-semibold text-balance">{entry.subject}</div>
                            <div className="text-xs mt-1 opacity-90">{entry.teacher}</div>
                            <div className="text-xs opacity-80">Room: {entry.room}</div>
                            <div className="text-xs opacity-80">Section: {entry.section}</div>
                          </div>
                        ) : (
                          <div className="p-3 text-center text-muted-foreground text-sm">Free</div>
                        )}
                      </td>
                    )
                  })}
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Legend */}
        <div className="mt-6">
          <h4 className="font-semibold mb-3">Subject Legend</h4>
          <div className="flex flex-wrap gap-2">
            {Array.from(subjectColorMap.entries()).map(([subject, colorClass]) => (
              <div key={subject} className={`px-3 py-1 rounded-full text-sm border-2 ${colorClass}`}>
                {subject}
              </div>
            ))}
          </div>
        </div>
      </CardContent>
    </Card>
  )
}
