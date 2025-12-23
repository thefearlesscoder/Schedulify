const handleGenerate = async () => {
  if (!groups || !rooms || !courses) {
    alert("Please upload all 3 CSV files");
    return;
  }

  const token = localStorage.getItem("token");
  if (!token) return navigate("/login");

  // Helper to rename files
  const renameFile = (file, newName) =>
    new File([file], newName, { type: file.type });

  const formData = new FormData();
  formData.append("files", renameFile(groups, "groups.csv"));
  formData.append("files", renameFile(rooms, "rooms.csv"));
  formData.append("files", renameFile(courses, "courses.csv"));

  // Debug: check FormData
  for (let pair of formData.entries()) {
    console.log(pair[0], pair[1].name); // should log "files groups.csv", etc.
  }

  setLoading(true);
  try {
    const res = await axios.post(
      "http://localhost:5000/api/schedule/generate",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
          "x-auth-token": token,
        },
      }
    );

    // Prepend the new schedule to the list
    setSchedules([res.data, ...schedules]);
    alert("Timetable generated successfully!");
  } catch (err) {
    console.error(err.response?.data || err.message);
    alert(
      "Generation failed: " +
        (err.response?.data?.msg || err.response?.data?.message || err.message)
    );
  } finally {
    setLoading(false);
  }
};
