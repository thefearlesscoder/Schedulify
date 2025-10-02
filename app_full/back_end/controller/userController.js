import { catchAsyncError } from "../middlewares/catchAsyncErrors.js";
import ErrorHandler from "../middlewares/error.js";
import { User } from "../models/userSchema.js";
import {sendToken} from "../utils/sendToken.js"

export const register = catchAsyncError(async(req, res,next) => {
  const {name,email,password,role} = req.body;

  if(!name || !email || !password || !role){
    return next(new ErrorHandler(401,"Please Provide all the fields in the form"));
  }

  const isEmail = User.findOne({email});

  if(isEmail){
    return next(new ErrorHandler(401,"This user is already registered on the portal"));
  }

  const user = await User.create({
    name,
    email,
    password,
    role
  });
  sendToken(user,201,res,"User Registered");
});

export const login = catchAsyncError(async(req,res,next) => {
  const { email, password, role } = req.body;
  if (!email || !password || !role) {
    return next(
      new ErrorHandler("Please provide email ,password and role.", 400)
    );
  }
  const user = await User.findOne({ email }).select("+password");
  if (!user) {
    return next(new ErrorHandler("Invalid Email Or Password.", 400));
  }
  const isPasswordMatched = await user.comparePassword(password);
  if (!isPasswordMatched) {
    return next(new ErrorHandler("Invalid Email Or Password.", 400));
  }
  if (user.role !== role) {
    return next(
      new ErrorHandler(`User with provided email and ${role} not found!`, 404)
    );
  }
  // console.log("user logged in");

  sendToken(user, 201, res, "User Logged In!");
});

export const logout = catchAsyncError(async(req,res,next) => {
  res
    .status(201)
    .cookie("token", "", {
      httpOnly: true,
      expires: new Date(Date.now()),
    })
    .json({
      success: true,
      message: "Logged Out Successfully.",
    });
});

export const getUser = catchAsyncErrors((req, res, next) => {
  // console.log("here at getuser");

  const user = req.user;
  // console.log(user);

  res.status(200).json({
    success: true,
    user,
  });
});