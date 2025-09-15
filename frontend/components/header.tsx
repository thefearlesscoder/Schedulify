import { ThemeToggle } from "./theme-toggle"
import { GraduationCap } from "lucide-react"

export function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b bg-background/95 backdrop-blur supports-[backdrop-filter]:bg-background/60">
      <div className="container mx-auto px-6 py-4 max-w-6xl">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <div className="flex items-center justify-center w-10 h-10 bg-primary rounded-lg">
              <GraduationCap className="h-6 w-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">Timetable Generator</h1>
              <p className="text-sm text-muted-foreground">Smart scheduling made easy</p>
            </div>
          </div>
          <ThemeToggle />
        </div>
      </div>
    </header>
  )
}
