"use client"

import type React from "react"

import { useCallback, useState } from "react"
import { CsvViewer } from "./csv-viewer"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Button } from "@/components/ui/button"

export function ResultCsvSection() {
  const [file, setFile] = useState<File | null>(null)
  const [dragOver, setDragOver] = useState(false)

  const onDrop = useCallback((e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if ((f && f.type.includes("csv")) || f?.name.endsWith(".csv")) {
      setFile(f)
    }
  }, [])

  const onFileChange = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) setFile(f)
  }, [])

  return (
    <section id="result-preview" className="container mx-auto px-4 py-12">
      <Card className="bg-card text-card-foreground">
        <CardHeader>
          <CardTitle className="text-balance">Result Preview</CardTitle>
          <CardDescription>
            Drop your generated schedule CSV here to preview it instantly, or use the file picker.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-6">
          <div
            onDragOver={(e) => {
              e.preventDefault()
              setDragOver(true)
            }}
            onDragLeave={() => setDragOver(false)}
            onDrop={onDrop}
            className={`rounded-xl border border-dashed p-6 transition-colors ${
              dragOver ? "bg-accent/30" : "bg-muted/50"
            }`}
            role="region"
            aria-label="Drop schedule CSV here"
          >
            <div className="flex flex-col items-center gap-3 text-center">
              <p className="text-sm">Drag & drop the generated {"schedule.csv"} here</p>
              <p className="text-xs opacity-70">Accepted format: .csv</p>
              <div>
                <label className="inline-flex">
                  <input type="file" accept=".csv,text/csv" className="hidden" onChange={onFileChange} />
                  <Button asChild variant="outline" size="sm">
                    <span>Select CSV</span>
                  </Button>
                </label>
              </div>
              {file ? (
                <p className="text-xs opacity-80">
                  Loaded: {file.name} ({Math.round(file.size / 1024)} KB)
                </p>
              ) : null}
            </div>
          </div>

          <CsvViewer file={file ?? undefined} />
        </CardContent>
      </Card>
    </section>
  )
}
