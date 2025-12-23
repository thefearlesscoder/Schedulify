"use client"

import { useEffect, useMemo, useState } from "react"
import Papa from "papaparse"
import { Button } from "@/components/ui/button"

type CsvViewerProps = {
  file?: File
  csvText?: string
  maxRows?: number
}

export function CsvViewer({ file, csvText, maxRows = 100 }: CsvViewerProps) {
  const [text, setText] = useState<string>("")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [view, setView] = useState<"table" | "raw">("table")
  const [showAll, setShowAll] = useState(false)

  useEffect(() => {
    let cancelled = false
    async function load() {
      setError(null)
      if (file) {
        try {
          setLoading(true)
          const content = await file.text()
          if (!cancelled) setText(content)
        } catch {
          if (!cancelled) setError("Failed to read CSV file.")
        } finally {
          if (!cancelled) setLoading(false)
        }
      } else if (csvText) {
        setText(csvText)
      } else {
        setText("")
      }
    }
    load()
    return () => {
      cancelled = true
    }
  }, [file, csvText])

  const parsed = useMemo(() => {
    if (!text) return null
    try {
      const result = Papa.parse<string[]>(text.trim(), {
        delimiter: "",
        newline: "",
        dynamicTyping: false,
        header: false,
        skipEmptyLines: "greedy",
      })
      const rows = (result.data || []) as string[][]
      return rows
    } catch {
      setError("Failed to parse CSV.")
      return null
    }
  }, [text])

  const headers = useMemo(() => (parsed && parsed.length ? parsed[0] : []), [parsed])
  const rows = useMemo(() => (parsed && parsed.length > 1 ? parsed.slice(1) : []), [parsed])

  const blob = useMemo(() => (text ? new Blob([text], { type: "text/csv;charset=utf-8" }) : null), [text])
  const url = useMemo(() => (blob ? URL.createObjectURL(blob) : null), [blob])
  useEffect(
    () => () => {
      if (url) URL.revokeObjectURL(url)
    },
    [url],
  )

  if (loading) {
    return <div className="rounded-lg border bg-card text-card-foreground p-4 text-sm">Parsing CSV…</div>
  }
  if (error) {
    return <div className="rounded-lg border bg-card text-card-foreground p-4 text-sm text-destructive">{error}</div>
  }
  if (!text) {
    return (
      <div className="rounded-lg border bg-card text-card-foreground p-4 text-sm opacity-80">No CSV loaded yet.</div>
    )
  }

  return (
    <div className="rounded-lg border bg-card text-card-foreground overflow-hidden">
      <div className="flex items-center justify-between gap-2 p-3 border-b">
        <div className="flex items-center gap-2">
          <Button size="sm" variant={view === "table" ? "default" : "outline"} onClick={() => setView("table")}>
            Table
          </Button>
          <Button size="sm" variant={view === "raw" ? "default" : "outline"} onClick={() => setView("raw")}>
            Raw CSV
          </Button>
        </div>
        <div className="flex items-center gap-2">
          {view === "table" && rows.length > maxRows ? (
            <Button size="sm" variant="outline" onClick={() => setShowAll((s) => !s)}>
              {showAll ? "Show first rows" : `Show all (${rows.length})`}
            </Button>
          ) : null}
          <Button
            size="sm"
            variant="outline"
            onClick={async () => {
              try {
                await navigator.clipboard.writeText(text)
              } catch {}
            }}
          >
            Copy
          </Button>
          {url ? (
            <a
              href={url}
              download="schedule.csv"
              className="inline-flex items-center rounded-md border px-3 py-1.5 text-sm hover:bg-accent hover:text-accent-foreground"
            >
              Download
            </a>
          ) : null}
        </div>
      </div>

      {view === "raw" ? (
        <pre className="max-h-[60vh] overflow-auto p-4 text-sm leading-6">{text}</pre>
      ) : (
        <div className="w-full overflow-auto">
          <table className="w-full border-collapse text-sm">
            <caption className="sr-only">CSV Preview</caption>
            <thead className="sticky top-0 bg-muted text-muted-foreground">
              <tr>
                {headers.map((h, i) => (
                  <th key={i} className="border-b px-3 py-2 text-left font-medium">
                    {h}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {(showAll ? rows : rows.slice(0, maxRows)).map((r, rIdx) => (
                <tr key={rIdx} className="odd:bg-muted/40">
                  {r.map((cell, cIdx) => (
                    <td key={cIdx} className="border-b px-3 py-2 align-top">
                      {cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
          {rows.length === 0 ? <div className="p-4 text-sm opacity-80">No rows to display.</div> : null}
        </div>
      )}
    </div>
  )
}
