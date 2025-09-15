"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import { Trash2, Plus, Users, MapPin, BookOpen, Layers, Clock } from "lucide-react"

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

interface InputFormsProps {
  onGenerate: (data: {
    teachers: Teacher[]
    rooms: Room[]
    subjects: Subject[]
    sections: Section[]
    timeSlots: TimeSlot[]
  }) => void
  isLoading: boolean
}

export function InputForms({ onGenerate, isLoading }: InputFormsProps) {
  const [teachers, setTeachers] = useState<Teacher[]>([{ id: "1", name: "", subjects: [""] }])
  const [rooms, setRooms] = useState<Room[]>([{ id: "1", name: "" }])
  const [subjects, setSubjects] = useState<Subject[]>([{ id: "1", name: "" }])
  const [sections, setSections] = useState<Section[]>([{ id: "1", name: "" }])
  const [timeSlots, setTimeSlots] = useState<TimeSlot[]>([{ id: "1", start: "", end: "" }])

  const addTeacher = () => {
    const newId = Date.now().toString()
    setTeachers([...teachers, { id: newId, name: "", subjects: [""] }])
  }

  const removeTeacher = (id: string) => {
    if (teachers.length > 1) {
      setTeachers(teachers.filter((t) => t.id !== id))
    }
  }

  const updateTeacher = (id: string, field: keyof Teacher, value: any) => {
    setTeachers(teachers.map((t) => (t.id === id ? { ...t, [field]: value } : t)))
  }

  const addSubjectToTeacher = (teacherId: string) => {
    setTeachers(teachers.map((t) => (t.id === teacherId ? { ...t, subjects: [...t.subjects, ""] } : t)))
  }

  const removeSubjectFromTeacher = (teacherId: string, subjectIndex: number) => {
    setTeachers(
      teachers.map((t) =>
        t.id === teacherId
          ? {
              ...t,
              subjects: t.subjects.filter((_, i) => i !== subjectIndex),
            }
          : t,
      ),
    )
  }

  const updateTeacherSubject = (teacherId: string, subjectIndex: number, value: string) => {
    setTeachers(
      teachers.map((t) =>
        t.id === teacherId
          ? {
              ...t,
              subjects: t.subjects.map((s, i) => (i === subjectIndex ? value : s)),
            }
          : t,
      ),
    )
  }

  const addRoom = () => {
    const newId = Date.now().toString()
    setRooms([...rooms, { id: newId, name: "" }])
  }

  const removeRoom = (id: string) => {
    if (rooms.length > 1) {
      setRooms(rooms.filter((r) => r.id !== id))
    }
  }

  const updateRoom = (id: string, name: string) => {
    setRooms(rooms.map((r) => (r.id === id ? { ...r, name } : r)))
  }

  const addSubject = () => {
    const newId = Date.now().toString()
    setSubjects([...subjects, { id: newId, name: "" }])
  }

  const removeSubject = (id: string) => {
    if (subjects.length > 1) {
      setSubjects(subjects.filter((s) => s.id !== id))
    }
  }

  const updateSubject = (id: string, name: string) => {
    setSubjects(subjects.map((s) => (s.id === id ? { ...s, name } : s)))
  }

  const addSection = () => {
    const newId = Date.now().toString()
    setSections([...sections, { id: newId, name: "" }])
  }

  const removeSection = (id: string) => {
    if (sections.length > 1) {
      setSections(sections.filter((s) => s.id !== id))
    }
  }

  const updateSection = (id: string, name: string) => {
    setSections(sections.map((s) => (s.id === id ? { ...s, name } : s)))
  }

  const addTimeSlot = () => {
    const newId = Date.now().toString()
    setTimeSlots([...timeSlots, { id: newId, start: "", end: "" }])
  }

  const removeTimeSlot = (id: string) => {
    if (timeSlots.length > 1) {
      setTimeSlots(timeSlots.filter((t) => t.id !== id))
    }
  }

  const updateTimeSlot = (id: string, field: "start" | "end", value: string) => {
    setTimeSlots(timeSlots.map((t) => (t.id === id ? { ...t, [field]: value } : t)))
  }

  const handleGenerate = () => {
    onGenerate({
      teachers: teachers.filter((t) => t.name.trim() && t.subjects.some((s) => s.trim())),
      rooms: rooms.filter((r) => r.name.trim()),
      subjects: subjects.filter((s) => s.name.trim()),
      sections: sections.filter((s) => s.name.trim()),
      timeSlots: timeSlots.filter((t) => t.start.trim() && t.end.trim()),
    })
  }

  return (
    <div className="space-y-8">
      <Card className="shadow-sm hover:shadow-md transition-all duration-300 card-enhanced">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className="flex items-center justify-center w-8 h-8 bg-primary/10 rounded-lg">
              <Users className="h-5 w-5 text-primary" />
            </div>
            Teachers
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          {teachers.map((teacher) => (
            <div
              key={teacher.id}
              className="space-y-4 p-6 border border-border rounded-xl bg-card/50 hover:bg-card transition-all duration-200 hover:shadow-md"
            >
              <div className="flex items-center gap-3">
                <div className="flex-1">
                  <Label htmlFor={`teacher-${teacher.id}`} className="text-sm font-medium">
                    Teacher Name
                  </Label>
                  <Input
                    id={`teacher-${teacher.id}`}
                    value={teacher.name}
                    onChange={(e) => updateTeacher(teacher.id, "name", e.target.value)}
                    placeholder="Enter teacher name"
                    className="mt-1 input-enhanced"
                  />
                </div>
                <Button
                  variant="outline"
                  size="icon"
                  onClick={() => removeTeacher(teacher.id)}
                  disabled={teachers.length === 1}
                  className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-all duration-200"
                >
                  <Trash2 className="h-4 w-4" />
                </Button>
              </div>
              <div className="space-y-3">
                <Label className="text-sm font-medium">Subjects</Label>
                {teacher.subjects.map((subject, index) => (
                  <div key={index} className="flex items-center gap-3">
                    <Input
                      value={subject}
                      onChange={(e) => updateTeacherSubject(teacher.id, index, e.target.value)}
                      placeholder="Enter subject"
                      className="flex-1 input-enhanced"
                    />
                    <Button
                      variant="outline"
                      size="icon"
                      onClick={() => removeSubjectFromTeacher(teacher.id, index)}
                      disabled={teacher.subjects.length === 1}
                      className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-all duration-200"
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                ))}
                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => addSubjectToTeacher(teacher.id)}
                  className="hover:bg-primary/10 hover:text-primary hover:border-primary/20 transition-all duration-200"
                >
                  <Plus className="h-4 w-4 mr-2" />
                  Add Subject
                </Button>
              </div>
            </div>
          ))}
          <Button
            onClick={addTeacher}
            variant="outline"
            className="w-full hover:bg-primary/10 hover:text-primary hover:border-primary/20 bg-transparent transition-all duration-200"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Teacher
          </Button>
        </CardContent>
      </Card>

      <Card className="shadow-sm hover:shadow-md transition-all duration-300 card-enhanced">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className="flex items-center justify-center w-8 h-8 bg-primary/10 rounded-lg">
              <MapPin className="h-5 w-5 text-primary" />
            </div>
            Rooms
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {rooms.map((room) => (
            <div
              key={room.id}
              className="flex items-center gap-3 p-4 border border-border rounded-lg bg-card/50 hover:bg-card transition-all duration-200 hover:shadow-md"
            >
              <div className="flex-1">
                <Input
                  value={room.name}
                  onChange={(e) => updateRoom(room.id, e.target.value)}
                  placeholder="Enter room name"
                  className="input-enhanced"
                />
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => removeRoom(room.id)}
                disabled={rooms.length === 1}
                className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-all duration-200"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            onClick={addRoom}
            variant="outline"
            className="w-full hover:bg-primary/10 hover:text-primary hover:border-primary/20 bg-transparent transition-all duration-200"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Room
          </Button>
        </CardContent>
      </Card>

      <Card className="shadow-sm hover:shadow-md transition-all duration-300 card-enhanced">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className="flex items-center justify-center w-8 h-8 bg-primary/10 rounded-lg">
              <BookOpen className="h-5 w-5 text-primary" />
            </div>
            Subjects
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {subjects.map((subject) => (
            <div
              key={subject.id}
              className="flex items-center gap-3 p-4 border border-border rounded-lg bg-card/50 hover:bg-card transition-all duration-200 hover:shadow-md"
            >
              <div className="flex-1">
                <Input
                  value={subject.name}
                  onChange={(e) => updateSubject(subject.id, e.target.value)}
                  placeholder="Enter subject name"
                  className="input-enhanced"
                />
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => removeSubject(subject.id)}
                disabled={subjects.length === 1}
                className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-all duration-200"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            onClick={addSubject}
            variant="outline"
            className="w-full hover:bg-primary/10 hover:text-primary hover:border-primary/20 bg-transparent transition-all duration-200"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Subject
          </Button>
        </CardContent>
      </Card>

      <Card className="shadow-sm hover:shadow-md transition-all duration-300 card-enhanced">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className="flex items-center justify-center w-8 h-8 bg-primary/10 rounded-lg">
              <Layers className="h-5 w-5 text-primary" />
            </div>
            Sections
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {sections.map((section) => (
            <div
              key={section.id}
              className="flex items-center gap-3 p-4 border border-border rounded-lg bg-card/50 hover:bg-card transition-all duration-200 hover:shadow-md"
            >
              <div className="flex-1">
                <Input
                  value={section.name}
                  onChange={(e) => updateSection(section.id, e.target.value)}
                  placeholder="Enter section name"
                  className="input-enhanced"
                />
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => removeSection(section.id)}
                disabled={sections.length === 1}
                className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-all duration-200"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            onClick={addSection}
            variant="outline"
            className="w-full hover:bg-primary/10 hover:text-primary hover:border-primary/20 bg-transparent transition-all duration-200"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Section
          </Button>
        </CardContent>
      </Card>

      <Card className="shadow-sm hover:shadow-md transition-all duration-300 card-enhanced">
        <CardHeader className="pb-4">
          <CardTitle className="flex items-center gap-3 text-xl">
            <div className="flex items-center justify-center w-8 h-8 bg-primary/10 rounded-lg">
              <Clock className="h-5 w-5 text-primary" />
            </div>
            Time Slots
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4">
          {timeSlots.map((slot) => (
            <div
              key={slot.id}
              className="flex items-center gap-3 p-4 border border-border rounded-lg bg-card/50 hover:bg-card transition-all duration-200 hover:shadow-md"
            >
              <div className="flex-1 grid grid-cols-2 gap-3">
                <div>
                  <Label htmlFor={`start-${slot.id}`} className="text-sm font-medium">
                    Start Time
                  </Label>
                  <Input
                    id={`start-${slot.id}`}
                    type="time"
                    value={slot.start}
                    onChange={(e) => updateTimeSlot(slot.id, "start", e.target.value)}
                    className="mt-1 input-enhanced"
                  />
                </div>
                <div>
                  <Label htmlFor={`end-${slot.id}`} className="text-sm font-medium">
                    End Time
                  </Label>
                  <Input
                    id={`end-${slot.id}`}
                    type="time"
                    value={slot.end}
                    onChange={(e) => updateTimeSlot(slot.id, "end", e.target.value)}
                    className="mt-1 input-enhanced"
                  />
                </div>
              </div>
              <Button
                variant="outline"
                size="icon"
                onClick={() => removeTimeSlot(slot.id)}
                disabled={timeSlots.length === 1}
                className="hover:bg-destructive/10 hover:text-destructive hover:border-destructive/20 transition-all duration-200"
              >
                <Trash2 className="h-4 w-4" />
              </Button>
            </div>
          ))}
          <Button
            onClick={addTimeSlot}
            variant="outline"
            className="w-full hover:bg-primary/10 hover:text-primary hover:border-primary/20 bg-transparent transition-all duration-200"
          >
            <Plus className="h-4 w-4 mr-2" />
            Add Time Slot
          </Button>
        </CardContent>
      </Card>

      <div className="flex justify-center pt-8">
        <Button
          onClick={handleGenerate}
          size="lg"
          disabled={isLoading}
          className="min-w-64 h-12 text-lg font-semibold shadow-lg hover:shadow-xl transition-all duration-200 hover:scale-105"
        >
          {isLoading ? (
            <div className="flex items-center gap-2">
              <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary-foreground/20 border-t-primary-foreground"></div>
              Generating...
            </div>
          ) : (
            "Generate Timetable"
          )}
        </Button>
      </div>
    </div>
  )
}
