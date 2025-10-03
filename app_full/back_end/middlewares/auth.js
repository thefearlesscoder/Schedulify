import {User} from '../models/userSchema.js';
import jwt  from 'jsonwebtoken';
import {catchAsyncError} from './catchAsyncErrors.js'
import ErrorHandler from './error.js';

export const isAuthenticated = catchAsyncError(async(req,res,next) => {
  const {token} = req.cookies;

  if(!token){
    return next(new ErrorHandler(401,"This user is not authenticated / token not found"));
  }

  let decoded;
  try {
    // --- IMPROVED DEBUGGING ---
    // Add a log to see the secret being used. Be careful not to do this in production.
    // console.log("Verifying token with secret:", process.env.JWT_SECRET);

    decoded = jwt.verify(token, process.env.JWT_SECRET);
  } catch (error) {
    // This will catch the specific error from jwt.verify
    console.error("JWT Verification Failed:", error.message);
    return next(
      new ErrorHandler(
        401,
        `JSON Web Token is invalid. Error: ${error.message}`
      )
    );
  }

  // console.log("This means the token is verified successfully");
  // const decoded = jwt.verify(token,process.env.JWT_SECRET);
  
  req.user = await User.findById(decoded.id);
  next();
});

export const isAuthorized = (...roles) => {
  return (req,res,next) => {
    if(!req.user){
      return next(new ErrorHandler(401, "User not found in request / user can't be authorized"));
    }
    if (!roles.includes(req.user.role)) {
      return next(
        new ErrorHandler(
          `Role:with this role (${req.user.role}) is not allowed to access this resource`,
          403
        )
      );
    }
    next();
  };
}