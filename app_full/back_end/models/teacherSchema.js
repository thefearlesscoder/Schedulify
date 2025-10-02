import mongoose from "mongoose";

export const teacherSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true,
  },
  courses: [{ type: mongoose.Schema.Types.ObjectId, ref: "Course" }],
});

export const Teacher = mongoose.model("Teacher",teacherSchema);