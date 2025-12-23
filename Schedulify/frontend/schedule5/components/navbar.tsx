"use client"

import { Calendar } from "lucide-react"
import { Button } from "@/components/ui/button"
import { ThemeToggle } from "@/components/theme-toggle"

export function Navbar() {
  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" })
  }

  return (
    <nav className="fixed top-0 z-50 w-full border-b border-border/40 bg-background/80 backdrop-blur-md">
      <div className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
        <div className="flex items-center gap-2">
          <div className="rounded-lg bg-gradient-to-br from-primary to-accent p-2">
            <Calendar className="h-6 w-6 text-primary-foreground" />
          </div>
          <span className="text-xl font-bold text-foreground">Schedule5</span>
        </div>

        <div className="hidden items-center gap-8 md:flex">
          <button
            onClick={() => scrollToSection("hero-section")}
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Home
          </button>
          <button
            onClick={() => scrollToSection("upload-section")}
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Upload
          </button>
          <button
            onClick={() => scrollToSection("output-section")}
            className="text-sm font-medium text-muted-foreground transition-colors hover:text-foreground"
          >
            Schedule
          </button>
          <ThemeToggle />
          <Button size="sm" className="bg-gradient-to-r from-primary to-accent">
            Get Started
          </Button>
        </div>
      </div>
    </nav>
  )
}
