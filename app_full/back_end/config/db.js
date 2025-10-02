import mongoose from "mongoose";

export const dbConnection = () => {
  mongoose.connect(process.env.MONGO_URI,{dbName: "Schedulify"})
  .then(() => {
    console.log("Database is connected successfully");
  })
  .catch((err) => {
    console.log(`Some error has occurred while connecting to the database ${err}`);
  })
}