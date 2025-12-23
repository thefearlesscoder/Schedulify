import mongoose from "mongoose";

const TimetableSchema = new mongoose.Schema({
  name: {
    type: String,
    required: true,
    default: `Timetable - ${new Date().toISOString()}`,
  },
  // We link the timetable to a specific user
  user: {
    type: mongoose.Schema.Types.ObjectId,
    ref: "User",
    required: true,
  },
  // The main timetable data. 'Object' allows for a flexible, nested structure.
  timetableData: {
    type: Object,
    required: true,
  },
  fitness: {
    type: Number,
    required: true,
  },
  createdAt: {
    type: Date,
    default: Date.now,
  },
});

export const Timetable = mongoose.model("Timetable", TimetableSchema);
