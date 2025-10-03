import { catchAsyncError } from "../middlewares/catchAsyncErrors.js";
import ErrorHandler from "../middlewares/error.js";
import { User } from "../models/userSchema.js";
import { generateForgotPasswordEmailTemplate } from "../utils/emailTemplate.js";
import { sendEmail } from "../utils/sendEmail.js";
import {sendToken} from "../utils/sendToken.js"
import crypto from "crypto";

export const register = catchAsyncError(async(req, res,next) => {
  const {name,email,password,role} = req.body;

  if(!name || !email || !password || !role){
    return next(new ErrorHandler(401,"Please Provide all the fields in the form"));
  }

  const isEmail = await User.findOne({email});

  if(isEmail){
    return next(new ErrorHandler(401,"This user is already registered on the portal"));
  }

  if (password.length < 8 || password.length > 16) {
    return next(
      new ErrorHandler(
        400,
        "Password must be at least 8 characters long and less than 16 characters"
      )
    );
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
    return next(new ErrorHandler(400,"Invalid Email Or Password.1"));
  }
  const isPasswordMatched = await user.comparePasswords(password);
  if (!isPasswordMatched) {
    return next(new ErrorHandler(400, "Invalid Email Or Password.2"));
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

export const getUser = catchAsyncError((req, res, next) => {
  // console.log("here at getuser");

  const user = req.user;
  // console.log(user);

  res.status(200).json({
    success: true,
    user,
  });
});

export const forgotPassword = catchAsyncError(async (req, res, next) => {
  if (!req.body.email) {
    return next(new ErrorHandler(400,"Please provide email"));
  }
  const { email } = req.body;
  if (!email) {
    return next(new ErrorHandler(400,"Please provide email"));
  }
  const user = await User.findOne({ email });
  if (!user) {
    return next(new ErrorHandler(400,"Invalid Email"));
  }
  const resetToken = user.getResetPasswordToken();
  await user.save({ validateModifiedOnly: false });

  const resetPasswordUrl = `${process.env.FRONTEND_URL}/password/reset/${resetToken}`;

  const message = generateForgotPasswordEmailTemplate(resetPasswordUrl);

  try {
    await sendEmail({
      email: user.email,
      subject: "Schedulify - password forget",
      message,
    });
    res.status(200).json({
      success: true,
      message: `Email sent to ${user.email} with password reset instructions`,
    });
  } catch (error) {
    user.resetPasswordToken = undefined;
    user.resetPasswordExpire = undefined;
    await user.save({ validateBeforeSave: false });
    return next(new ErrorHandler(500,error.message));
  }
});

export const resetPassword = catchAsyncError(async (req, res, next) => {
  const { token } = req.params;
  const resetPasswordToken = crypto
    .createHash("sha256")
    .update(token)
    .digest("hex");

  const user = await User.findOne({
    resetPasswordToken,
    resetPasswordExpire: { $gt: Date.now() }, // Check if the token is still valid
  });
  if (!user) {
    return next(new ErrorHandler(400,"Invalid or expired reset token"));
  }

  if (req.body.password !== req.body.confirmPassword) {
    return next(new ErrorHandler(400,"Passwords do not match"));
  }

  if (req.body.password.length < 8 || req.body.password.length > 16) {
    return next(
      new ErrorHandler(
        "Password must be at least 8 characters long and less than 16 characters",
        400
      )
    );
  }

  
  user.password = req.body.password;
  user.resetPasswordToken = undefined;
  user.resetPasswordExpire = undefined;
  await user.save({ validateModifiedOnly: false });

  sendToken(user, 200,res, "Password reset successfully");
});

export const updatePassword = catchAsyncError(async (req, res, next) => {
  const user = await User.findById(req.user._id).select("+password");
  const { currentPassword, newPassword, confirmPassword } = req.body;
  if (!currentPassword || !newPassword || !confirmPassword) {
    return next(new ErrorHandler(400,"Please provide all fields"));
  }

  const isPasswordMatched = await bcrypt.compare(
    currentPassword,
    user.password
  );
  if (!isPasswordMatched) {
    return next(new errorHandler(400,"Current password is incorrect"));
  }
  if (newPassword.length < 8 || newPassword.length > 16) {
    return next(
      new ErrorHandler(
        "Password must be at least 8 characters long and less than 16 characters",
        400
      )
    );
  }
  if (newPassword !== confirmPassword) {
    return next(
      new ErrorHandler(400,"New password and confirm password do not match")
    );
  }

  // const hashedPassword = await bcrypt.hash(newPassword, 10);
  user.password = newPassword;
  await user.save({ validateModifiedOnly: false });

  res.status(200).json({
    success: true,
    message: "Password updated successfully",
  });
});