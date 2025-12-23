import mongoose from "mongoose";

const courseSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true,
  },
  name: {
    type: String,
    required: true,
  },
  dept: {
    type: String,
    required: true,
  },
  semester: {
    type: Number,
    required: true,
  },
  students: {
    type: Number,
    required: true,
  },
  hours: {
    type: Number,
    required: true,
  },
  credits: {
    type: Number,
    required: true,
  },
  theory_course: {
    type: Boolean,
    required: true
  }
});

export const Course = mongoose.model("Course",courseSchema);