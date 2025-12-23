import {app} from "./app.js";


app.listen(process.env.PORT,() => {
  console.log(`Server is running fine at port ${process.env.PORT}`);
})