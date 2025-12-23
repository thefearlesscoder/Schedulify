const mongoose = require("mongoose");
const ScheduleSchema = new mongoose.Schema({
  user: { type: mongoose.Schema.Types.ObjectId, ref: "User" },
  scheduleData: { type: Array, required: true }, // Stores the final JSON schedule
  createdAt: { type: Date, default: Date.now },
});
module.exports = mongoose.model("Schedule", ScheduleSchema);
