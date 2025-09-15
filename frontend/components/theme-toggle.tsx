"use client"

import { Moon, Sun } from "lucide-react"
import { useTheme } from "next-themes"
import { Button } from "@/components/ui/button"
import { useEffect, useState } from "react"

export function ThemeToggle() {
  const { theme, setTheme } = useTheme()
  const [mounted, setMounted] = useState(false)

  useEffect(() => {
    setMounted(true)
  }, [])

  if (!mounted) {
    return (
      <Button variant="outline" size="icon" className="w-10 h-10 bg-transparent">
        <div className="h-4 w-4" />
      </Button>
    )
  }

  const isDark = theme === "dark"

  return (
    <Button
      variant="outline"
      size="icon"
      onClick={() => {
        const newTheme = isDark ? "light" : "dark"
        console.log("[v0] Switching theme from", theme, "to", newTheme)
        setTheme(newTheme)
      }}
      className="w-10 h-10 transition-all duration-200 hover:scale-105 border-border bg-background hover:bg-accent"
    >
      {isDark ? (
        <Sun className="h-4 w-4 transition-all text-foreground" />
      ) : (
        <Moon className="h-4 w-4 transition-all text-foreground" />
      )}
      <span className="sr-only">Toggle theme</span>
    </Button>
  )
}
