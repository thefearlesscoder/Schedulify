"use client"

import { useState } from "react"
import { InputForms } from "@/components/input-forms"
import { TimetableDisplay } from "@/components/timetable-display"
import { Header } from "@/components/header"
import { useToast } from "@/hooks/use-toast"
import { Toaster } from "@/components/ui/toaster"
import { Card, CardContent } from "@/components/ui/card"
import { Calendar, Clock, Users, BookOpen } from "lucide-react"

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

export default function TimetableGenerator() {
  const [timetable, setTimetable] = useState<TimetableData>({})
  const [timeSlots, setTimeSlots] = useState<string[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const { toast } = useToast()

  const handleGenerate = async (data: {
    teachers: Teacher[]
    rooms: Room[]
    subjects: Subject[]
    sections: Section[]
    timeSlots: TimeSlot[]
  }) => {
    setIsLoading(true)

    try {
      const response = await fetch("/api/generate_timetable", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(data),
      })

      if (!response.ok) {
        const errorData = await response.json()
        throw new Error(errorData.error || "Failed to generate timetable")
      }

      const result = await response.json()

      if (result.success) {
        setTimetable(result.timetable)
        setTimeSlots(result.timeSlots)
        toast({
          title: "Success!",
          description: "Timetable generated successfully.",
        })

        // Scroll to timetable
        setTimeout(() => {
          const timetableElement = document.getElementById("timetable-section")
          if (timetableElement) {
            timetableElement.scrollIntoView({ behavior: "smooth" })
          }
        }, 100)
      } else {
        throw new Error("Failed to generate timetable")
      }
    } catch (error) {
      console.error("Error:", error)
      toast({
        title: "Error",
        description: error instanceof Error ? error.message : "Failed to generate timetable. Please try again.",
        variant: "destructive",
      })
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-background">
      <Header />

      <main className="container mx-auto px-6 py-8 max-w-6xl">
        <div className="text-center mb-12 animate-fade-in">
          <div className="mb-6">
            <h2 className="text-5xl font-bold mb-4 text-balance text-foreground">Smart Timetable Generator</h2>
            <p className="text-muted-foreground text-xl text-pretty max-w-2xl mx-auto leading-relaxed">
              Create organized schedules effortlessly by inputting teachers, rooms, subjects, sections, and time slots
            </p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 max-w-3xl mx-auto mb-8">
            <Card className="p-4 hover:shadow-md transition-shadow">
              <CardContent className="p-0 text-center">
                <Users className="h-8 w-8 text-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Teachers</p>
              </CardContent>
            </Card>
            <Card className="p-4 hover:shadow-md transition-shadow">
              <CardContent className="p-0 text-center">
                <BookOpen className="h-8 w-8 text-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Subjects</p>
              </CardContent>
            </Card>
            <Card className="p-4 hover:shadow-md transition-shadow">
              <CardContent className="p-0 text-center">
                <Calendar className="h-8 w-8 text-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Rooms</p>
              </CardContent>
            </Card>
            <Card className="p-4 hover:shadow-md transition-shadow">
              <CardContent className="p-0 text-center">
                <Clock className="h-8 w-8 text-primary mx-auto mb-2" />
                <p className="text-sm font-medium">Time Slots</p>
              </CardContent>
            </Card>
          </div>
        </div>

        <div className="mb-16 animate-slide-up">
          <InputForms onGenerate={handleGenerate} isLoading={isLoading} />
        </div>

        {isLoading && (
          <div className="flex items-center justify-center py-16">
            <div className="flex flex-col items-center space-y-4">
              <div className="relative">
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary/20"></div>
                <div className="animate-spin rounded-full h-12 w-12 border-4 border-primary border-t-transparent absolute top-0"></div>
              </div>
              <div className="text-center">
                <p className="text-lg font-medium text-foreground">Generating your timetable...</p>
                <p className="text-sm text-muted-foreground">This may take a few moments</p>
              </div>
            </div>
          </div>
        )}

        {/* Timetable Display */}
        <div id="timetable-section" className="animate-slide-up">
          <TimetableDisplay timetable={timetable} timeSlots={timeSlots} />
        </div>

        <footer className="mt-20 pt-8 border-t border-border">
          <div className="text-center text-muted-foreground">
            <p className="text-sm">
              Built with ❤️ using Next.js and TailwindCSS • Responsive Design • Dark Mode Support
            </p>
          </div>
        </footer>
      </main>

      <Toaster />
    </div>
  )
}
