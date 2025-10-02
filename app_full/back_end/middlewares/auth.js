import {User} from '../models/userSchema.js';
import jwt  from 'jsonwebtoken';
import {catchAsyncErrors} from './catchAsyncErrors.js'
import ErrorHandler from './error.js';

export const isAuthenticated = catchAsyncErrors(async(req,res,next) => {
  const {token} = req.cookies;

  if(!token){
    return next(new ErrorHandler(401,"This user is not authenticated / token not found"));
  }

  const decoded = jwt.verify(token,process.env.JWT_SECRET);

  req.user = await User.findById  (decoded.id);
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