import express from 'express';

import { login,logout,register,resetPassword,forgotpassword,updatePassword,getUser } from '../controller/userController.js';

import { isAuthenticated } from '../middlewares/auth.js';

const router = express.Router();

router.post("/register", register);
router.post("/login", login);
router.get("/logout", isAuthenticated, logout);
router.get("/me", isAuthenticated, getUser);
router.post("/password/forgot", forgotpassword);
router.put("/password/reset/:token", resetPassword);
router.put("/password/update", isAuthenticated, updatePassword);

export default router;