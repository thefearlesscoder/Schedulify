import { dbConnection } from "./config/db.js";
import express from "express";
import { config } from "dotenv";
import userRouter from './routes/userRoutes.js';
import { errorMiddleware } from "./middlewares/error.js";
import cors from "cors";
import cookieParser from "cookie-parser";
export const app = express();

config({ path: "./.env" });

app.use(
  cors({
    origin: [process.env.FRONTEND_URL],
    methods: ["GET", "POST", "PUT", "DELETE"],
    credentials: true,
  })
);

app.use(cookieParser());
app.use(express.json());
app.use(express.urlencoded({ extended: true }));

app.use("/api/v1/user", userRouter);

dbConnection();

app.use(errorMiddleware); 