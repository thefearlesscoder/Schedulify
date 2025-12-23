import mongoose from "mongoose";

export const roomSchema = new mongoose.Schema({
  id: {
    type: String,
    required: true,
    unique: true,
  },
  capacity: {
    type: Number,
    required: true,
  }
});

export const Room = mongoose.model("Room",roomSchema);