import express from "express";
import bodyParser from "body-parser";
import fileUpload from "express-fileupload";
import expressLayouts from "express-ejs-layouts";
import routes from "./routes.js";

const app = express();
const port = 5000;

app.set("view engine", "ejs");

app.use(bodyParser.json());
app.use(fileUpload());
app.use(expressLayouts);
app.use("/", routes);

app.listen(port, ()=> {
    console.log(`>> Server is running on http://localhost:${port}`);
})