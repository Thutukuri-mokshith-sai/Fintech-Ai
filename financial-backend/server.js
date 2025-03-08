require("dotenv").config();
const express = require("express");
const authRoutes = require("./auth");
const income=require("./income");
const app = express();
const cors = require("cors");
app.use(cors());
app.use(express.json());

// Routes
app.use("/auth", authRoutes);
app.use("/income",income);
// Start Server
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => console.log(`Server running on port ${PORT}`));
