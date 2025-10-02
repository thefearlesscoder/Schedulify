import { dbConnection } from "./config/db.js";
import express from "express";
import { config } from "dotenv";
const app = express();

dbConnection();
config({path: './.env'})
export default app;