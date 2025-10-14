"use client"

import type React from "react"

import { useState } from "react"
import { ChevronDown, Sparkles, Users, BookOpen, Building2, FileText, Landmark } from "lucide-react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Navbar } from "@/components/navbar"
import { CsvViewer } from "@/components/csv-viewer"
import axios from "axios"
import BASE_URL  from "../data.js"
import { toast } from "sonner"

export default function Home() {
  const [teachersFile, setTeachersFile] = useState<File | null>(null)
  const [coursesFile, setCoursesFile] = useState<File | null>(null)
  const [roomsFile, setRoomsFile] = useState<File | null>(null)
  const [departmentsFile, setDepartmentsFile] = useState<File | null>(null)
  const [draggingField, setDraggingField] = useState<string | null>(null)
  const [scheduleData, setScheduleData] = useState<any>(null)
  const [scheduleCsvText, setScheduleCsvText] = useState<string | null>(null)
  const [resultCsvFile, setResultCsvFile] = useState<File | null>(null)
  const [outputDragOver, setOutputDragOver] = useState(false)


  const handlesumbitcsv = async () => {

    try {
      if (!teachersFile || !coursesFile || !roomsFile || !departmentsFile) {
        alert("Please upload all required CSV files.")
        return
      }

      const formData = new FormData()
      formData.append("teachers", teachersFile)
      formData.append("courses", coursesFile)
      formData.append("rooms", roomsFile)
      formData.append("departments", departmentsFile)

      const response1 = await axios.post(`${BASE_URL}/upload`,
        formData,{
        headers: { "Content-Type": "multipart/form-data" }
    })

      // const csv = response.data.csv
      console.log(response1) ;
      toast.success("Files uploaded successfully!")



      const respast  = await axios.post(`${BASE_URL}/generate`) ;

      console.log(respast) ;
      // const response11 = await axios.get(
      //   `${BASE_URL}/timetable-json`,
       
      // );

      // console.log(response11) ;

      const response = await axios.get(`${BASE_URL}/download`, {
        responseType: "blob", // Get file blob
      });

      // Convert blob to text
      const text = await response.data.text();
      setScheduleCsvText(text);
      console.log("CSV loaded:", text);



      // // Convert blob to text (for displaying in frontend)
      // const text = await response.data.text(); 
      // setScheduleCsvText(text);

      // // Create a download link
      // const url = window.URL.createObjectURL(new Blob([response.data]));
      // const a = document.createElement("a");
      // a.href = url;
      // a.download = "timetable.csv"; // filename
      // document.body.appendChild(a);
      // a.click();
      // a.remove();
      // window.URL.revokeObjectURL(url);
            
          } catch (error) {
            console.error("Error uploading files:", error)
          }
  
  }

  const handleDragOver = (e: React.DragEvent, field: string) => {
    e.preventDefault()
    setDraggingField(field)
  }

  const handleDragLeave = () => {
    setDraggingField(null)
  }

  const handleDrop = (e: React.DragEvent, field: string) => {
    e.preventDefault()
    setDraggingField(null)
    const droppedFile = e.dataTransfer.files[0]
    if (droppedFile && droppedFile.type === "text/csv") {
      if (field === "teachers") setTeachersFile(droppedFile)
      if (field === "courses") setCoursesFile(droppedFile)
      if (field === "rooms") setRoomsFile(droppedFile)
      if (field === "departments") setDepartmentsFile(droppedFile)
    }
  }

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, field: string) => {
    const selectedFile = e.target.files?.[0]
    if (selectedFile) {
      if (field === "teachers") setTeachersFile(selectedFile)
      if (field === "courses") setCoursesFile(selectedFile)
      if (field === "rooms") setRoomsFile(selectedFile)
      if (field === "departments") setDepartmentsFile(selectedFile)
    }
  }

  const handleResultDrop = (e: React.DragEvent<HTMLDivElement>) => {
    e.preventDefault()
    setOutputDragOver(false)
    const f = e.dataTransfer.files?.[0]
    if (f && (f.type.includes("csv") || f.name.endsWith(".csv"))) {
      setResultCsvFile(f)
      setScheduleCsvText(null)
    }
  }

  const handleResultFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const f = e.target.files?.[0]
    if (f) {
      setResultCsvFile(f)
      setScheduleCsvText(null)
    }
  }

  const scrollToSection = (id: string) => {
    document.getElementById(id)?.scrollIntoView({ behavior: "smooth" })
  }

  const allFilesUploaded = teachersFile && coursesFile && roomsFile && departmentsFile

  return (
    <main className="min-h-screen">
      {/* Navbar */}
      <Navbar />

      {/* Hero Section */}
      <section
        id="hero-section"
        className="relative flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-primary/5 via-accent/5 to-background px-4 pt-16"
      >
        <div className="mx-auto max-w-4xl text-center">
          <div className="mb-6 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary/10 to-accent/10 px-4 py-2 text-sm font-medium text-primary">
            <Sparkles className="h-4 w-4" />
            AI-Powered Scheduling
          </div>
          <h1 className="mb-6 bg-gradient-to-r from-primary via-accent to-primary bg-clip-text text-balance font-sans text-5xl font-bold tracking-tight text-transparent md:text-7xl">
            Schedule5 – Smart Scheduling Made Simple
          </h1>
          <p className="text-pretty text-xl text-muted-foreground md:text-2xl">
            Upload your data. Get your schedule. No hassle.
          </p>
        </div>

        <button
          onClick={() => scrollToSection("demo-section")}
          className="absolute bottom-12 animate-bounce cursor-pointer rounded-full p-2 transition-colors hover:bg-accent/20"
          aria-label="Scroll to demo section"
        >
          <ChevronDown className="h-8 w-8 text-primary" />
        </button>
      </section>

      {/* Demo CSV Section */}
      <section
        id="demo-section"
        className="min-h-screen bg-gradient-to-b from-background via-primary/5 to-accent/5 px-4 py-20"
      >
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 text-center">
            <div className="mb-4 inline-flex items-center gap-2 rounded-full bg-gradient-to-r from-primary/10 to-accent/10 px-4 py-2 text-sm font-medium text-primary">
              <FileText className="h-4 w-4" />
              CSV Format Guide
            </div>
            <h2 className="mb-4 text-4xl font-bold text-foreground">CSV File Format Examples</h2>
            <p className="text-lg text-muted-foreground">
              Follow these formats when preparing your CSV files for upload
            </p>
          </div>

          <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-4">
            {/* Teachers CSV Format */}
            <Card className="overflow-hidden border-2 border-blue-500/20 bg-gradient-to-br from-blue-500/5 to-blue-600/5 shadow-lg">
              <div className="border-b border-blue-500/20 bg-gradient-to-r from-blue-500/10 to-blue-600/10 p-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-blue-500/20 p-2">
                    <Users className="h-5 w-5 text-blue-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">Teachers CSV</h3>
                </div>
              </div>
              <div className="p-4">
                <div className="overflow-x-auto rounded-lg bg-card">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border bg-muted/50">
                        <th className="px-3 py-2 text-left font-semibold text-foreground">teacher_id</th>
                        <th className="px-3 py-2 text-left font-semibold text-foreground">name</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">T001</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">John Smith</td>
                      </tr>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">T002</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">Jane Doe</td>
                      </tr>
                      <tr>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">T003</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">Bob Wilson</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">
                  Include unique teacher ID and full name for each instructor
                </p>
              </div>
            </Card>

            {/* Courses CSV Format */}
            <Card className="overflow-hidden border-2 border-purple-500/20 bg-gradient-to-br from-purple-500/5 to-purple-600/5 shadow-lg">
              <div className="border-b border-purple-500/20 bg-gradient-to-r from-purple-500/10 to-purple-600/10 p-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-purple-500/20 p-2">
                    <BookOpen className="h-5 w-5 text-purple-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">Courses CSV</h3>
                </div>
              </div>
              <div className="p-4">
                <div className="overflow-x-auto rounded-lg bg-card">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border bg-muted/50">
                        <th className="px-3 py-2 text-left font-semibold text-foreground">course_id</th>
                        <th className="px-3 py-2 text-left font-semibold text-foreground">name</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">CS101</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">Intro to CS</td>
                      </tr>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">MATH201</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">Calculus II</td>
                      </tr>
                      <tr>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">ENG102</td>
                        <td className="px-3 py-2 text-xs text-muted-foreground">Literature</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">
                  Include course code and full course name for each class
                </p>
              </div>
            </Card>

            {/* Rooms CSV Format */}
            <Card className="overflow-hidden border-2 border-green-500/20 bg-gradient-to-br from-green-500/5 to-green-600/5 shadow-lg">
              <div className="border-b border-green-500/20 bg-gradient-to-r from-green-500/10 to-green-600/10 p-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-green-500/20 p-2">
                    <Building2 className="h-5 w-5 text-green-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">Rooms CSV</h3>
                </div>
              </div>
              <div className="p-4">
                <div className="overflow-x-auto rounded-lg bg-card">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border bg-muted/50">
                        <th className="px-3 py-2 text-left font-semibold text-foreground">room_id</th>
                        <th className="px-3 py-2 text-left font-semibold text-foreground">capacity</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">R101</td>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">30</td>
                      </tr>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">R202</td>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">50</td>
                      </tr>
                      <tr>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">LAB1</td>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">25</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">
                  Include room identifier and maximum student capacity
                </p>
              </div>
            </Card>

            <Card className="overflow-hidden border-2 border-amber-500/20 bg-gradient-to-br from-amber-500/5 to-amber-600/5 shadow-lg">
              <div className="border-b border-amber-500/20 bg-gradient-to-r from-amber-500/10 to-amber-600/10 p-4">
                <div className="flex items-center gap-3">
                  <div className="rounded-lg bg-amber-500/20 p-2">
                    <Landmark className="h-5 w-5 text-amber-600" />
                  </div>
                  <h3 className="text-lg font-semibold text-foreground">Departments CSV</h3>
                </div>
              </div>
              <div className="p-4">
                <div className="overflow-x-auto rounded-lg bg-card">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-border bg-muted/50">
                        <th className="px-3 py-2 text-left font-semibold text-foreground">department_id</th>
                        <th className="px-3 py-2 text-left font-semibold text-foreground">name</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">D001</td>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">Computer Science</td>
                      </tr>
                      <tr className="border-b border-border">
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">D002</td>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">Mathematics</td>
                      </tr>
                      <tr>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">D003</td>
                        <td className="px-3 py-2 font-mono text-xs text-muted-foreground">English</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <p className="mt-3 text-xs text-muted-foreground">Include unique department ID and department name</p>
              </div>
            </Card>
          </div>

          <div className="mt-8 text-center">
            <Button
              size="lg"
              className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
              onClick={() => scrollToSection("upload-section")}
            >
              Ready to Upload
            </Button>
          </div>
        </div>
      </section>

      {/* CSV Input Section */}
      <section id="upload-section" className="min-h-screen bg-gradient-to-b from-accent/5 to-background px-4 py-20">
        <div className="mx-auto max-w-6xl">
          <h2 className="mb-4 text-center text-4xl font-bold text-foreground">Upload Your CSV Files</h2>
          <p className="mb-12 text-center text-lg text-muted-foreground">
            Upload your teachers, courses, rooms, and departments data in CSV format.
          </p>

          <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-4">
            {/* Teachers Upload */}
            <Card
              className={`group relative overflow-hidden border-2 border-dashed transition-all duration-300 ${
                draggingField === "teachers"
                  ? "border-primary bg-primary/5 shadow-lg shadow-primary/20"
                  : "border-border bg-card hover:border-primary/50 hover:shadow-md"
              }`}
              onDragOver={(e) => handleDragOver(e, "teachers")}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, "teachers")}
            >
              <div className="flex min-h-[280px] flex-col items-center justify-center p-6">
                <div className="mb-4 rounded-full bg-gradient-to-br from-blue-500/20 to-blue-600/20 p-4 transition-transform group-hover:scale-110">
                  <Users className="h-8 w-8 text-blue-600" />
                </div>

                <h3 className="mb-2 text-lg font-semibold text-foreground">Teachers</h3>

                <p className="mb-4 text-center text-xs text-muted-foreground">
                  {teachersFile ? teachersFile.name : "Drop CSV here"}
                </p>

                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, "teachers")}
                  className="hidden"
                  id="teachers-upload"
                />

                <label htmlFor="teachers-upload">
                  <Button
                    type="button"
                    size="sm"
                    className="cursor-pointer bg-gradient-to-r from-blue-500 to-blue-600 hover:opacity-90"
                    onClick={() => document.getElementById("teachers-upload")?.click()}
                  >
                    {teachersFile ? "Change File" : "Browse"}
                  </Button>
                </label>
              </div>
            </Card>

            {/* Courses Upload */}
            <Card
              className={`group relative overflow-hidden border-2 border-dashed transition-all duration-300 ${
                draggingField === "courses"
                  ? "border-primary bg-primary/5 shadow-lg shadow-primary/20"
                  : "border-border bg-card hover:border-primary/50 hover:shadow-md"
              }`}
              onDragOver={(e) => handleDragOver(e, "courses")}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, "courses")}
            >
              <div className="flex min-h-[280px] flex-col items-center justify-center p-6">
                <div className="mb-4 rounded-full bg-gradient-to-br from-purple-500/20 to-purple-600/20 p-4 transition-transform group-hover:scale-110">
                  <BookOpen className="h-8 w-8 text-purple-600" />
                </div>

                <h3 className="mb-2 text-lg font-semibold text-foreground">Courses</h3>

                <p className="mb-4 text-center text-xs text-muted-foreground">
                  {coursesFile ? coursesFile.name : "Drop CSV here"}
                </p>

                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, "courses")}
                  className="hidden"
                  id="courses-upload"
                />

                <label htmlFor="courses-upload">
                  <Button
                    type="button"
                    size="sm"
                    className="cursor-pointer bg-gradient-to-r from-purple-500 to-purple-600 hover:opacity-90"
                    onClick={() => document.getElementById("courses-upload")?.click()}
                  >
                    {coursesFile ? "Change File" : "Browse"}
                  </Button>
                </label>
              </div>
            </Card>

            {/* Rooms Upload */}
            <Card
              className={`group relative overflow-hidden border-2 border-dashed transition-all duration-300 ${
                draggingField === "rooms"
                  ? "border-primary bg-primary/5 shadow-lg shadow-primary/20"
                  : "border-border bg-card hover:border-primary/50 hover:shadow-md"
              }`}
              onDragOver={(e) => handleDragOver(e, "rooms")}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, "rooms")}
            >
              <div className="flex min-h-[280px] flex-col items-center justify-center p-6">
                <div className="mb-4 rounded-full bg-gradient-to-br from-green-500/20 to-green-600/20 p-4 transition-transform group-hover:scale-110">
                  <Building2 className="h-8 w-8 text-green-600" />
                </div>

                <h3 className="mb-2 text-lg font-semibold text-foreground">Rooms</h3>

                <p className="mb-4 text-center text-xs text-muted-foreground">
                  {roomsFile ? roomsFile.name : "Drop CSV here"}
                </p>

                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, "rooms")}
                  className="hidden"
                  id="rooms-upload"
                />

                <label htmlFor="rooms-upload">
                  <Button
                    type="button"
                    size="sm"
                    className="cursor-pointer bg-gradient-to-r from-green-500 to-green-600 hover:opacity-90"
                    onClick={() => document.getElementById("rooms-upload")?.click()}
                  >
                    {roomsFile ? "Change File" : "Browse"}
                  </Button>
                </label>
              </div>
            </Card>

            <Card
              className={`group relative overflow-hidden border-2 border-dashed transition-all duration-300 ${
                draggingField === "departments"
                  ? "border-primary bg-primary/5 shadow-lg shadow-primary/20"
                  : "border-border bg-card hover:border-primary/50 hover:shadow-md"
              }`}
              onDragOver={(e) => handleDragOver(e, "departments")}
              onDragLeave={handleDragLeave}
              onDrop={(e) => handleDrop(e, "departments")}
            >
              <div className="flex min-h-[280px] flex-col items-center justify-center p-6">
                <div className="mb-4 rounded-full bg-gradient-to-br from-amber-500/20 to-amber-600/20 p-4 transition-transform group-hover:scale-110">
                  <Landmark className="h-8 w-8 text-amber-600" />
                </div>

                <h3 className="mb-2 text-lg font-semibold text-foreground">Departments</h3>

                <p className="mb-4 text-center text-xs text-muted-foreground">
                  {departmentsFile ? departmentsFile.name : "Drop CSV here"}
                </p>

                <input
                  type="file"
                  accept=".csv"
                  onChange={(e) => handleFileChange(e, "departments")}
                  className="hidden"
                  id="departments-upload"
                />

                <label htmlFor="departments-upload">
                  <Button
                    type="button"
                    size="sm"
                    className="cursor-pointer bg-gradient-to-r from-amber-500 to-amber-600 hover:opacity-90"
                    onClick={() => document.getElementById("departments-upload")?.click()}
                  >
                    {departmentsFile ? "Change File" : "Browse"}
                  </Button>
                </label>
              </div>
            </Card>
          </div>

          {allFilesUploaded && (
            <div className="mt-8 text-center">
              <Button
                size="lg"
                className="bg-gradient-to-r from-primary to-accent hover:opacity-90"
                onClick={() => {
                  handlesumbitcsv() ;
                  // setScheduleCsvText(csv)
                  // setResultCsvFile(null)
                  setScheduleData({
                    processed: true,
                    timestamp: new Date().toLocaleString(),
                  })
                  scrollToSection("output-section")
                }}
              >
                Generate Schedule
              </Button>
            </div>
          )}
        </div>
      </section>

      {/* Output Section */}
      <section
        id="output-section"
        className="min-h-screen bg-gradient-to-br from-accent/10 via-primary/5 to-background px-4 py-20"
      >
        <div className="mx-auto max-w-5xl">
          <h2 className="mb-4 text-center text-4xl font-bold text-foreground">Generated Schedule</h2>
          <p className="mb-12 text-center text-lg text-muted-foreground">
            Your optimized schedule CSV will appear below
          </p>

          <Card className="overflow-hidden shadow-xl">
            <div className="min-h-[400px] p-8">
              {scheduleData || scheduleCsvText || resultCsvFile ? (
                <div className="space-y-4">
                  {/* Existing processed info banner */}
                  <div className="rounded-lg bg-gradient-to-r from-primary/10 to-accent/10 p-4">
                    <p className="text-sm text-foreground">
                      Schedule processed at: {scheduleData?.timestamp || new Date().toLocaleString()}
                    </p>
                  </div>

                  <CsvViewer csvText={scheduleCsvText ?? undefined} file={resultCsvFile ?? undefined} />
                </div>
              ) : (
                <div
                  className={`flex min-h-[350px] flex-col items-center justify-center rounded-lg border-2 border-dashed p-8 text-center transition-colors ${
                    outputDragOver ? "bg-accent/30" : "bg-muted/50"
                  }`}
                  onDragOver={(e) => {
                    e.preventDefault()
                    setOutputDragOver(true)
                  }}
                  onDragLeave={() => setOutputDragOver(false)}
                  onDrop={handleResultDrop}
                >
                  <p className="text-lg text-foreground">Drop your schedule.csv here to preview</p>
                  <p className="mt-2 text-sm text-muted-foreground">Or select a CSV file using the picker below</p>
                  <label className="mt-6 inline-flex">
                    <input type="file" accept=".csv,text/csv" className="hidden" onChange={handleResultFileChange} />
                    <Button variant="outline">Select CSV</Button>
                  </label>
                </div>
              )}
            </div>
          </Card>
        </div>
      </section>
    </main>
  )
}
