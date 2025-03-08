require("dotenv").config();
const express = require("express");
const mysql = require("mysql2");
const bcrypt = require("bcryptjs");
const jwt = require("jsonwebtoken");

const router = express.Router();

// MySQL Database Connection
const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "",
  database: "financialmanagement",
});

db.connect((err) => {
  if (err) console.error("Database connection failed:", err);
  else console.log("Connected to MySQL Database");
});

// **Signup API**
router.post("/signup", async (req, res) => {
  const { name, email, password } = req.body;

  try {
    const [existingUser] = await db.promise().query("SELECT * FROM users WHERE email = ?", [email]);
    if (existingUser.length > 0) {
      return res.status(400).json({ message: "Email already exists" });
    }

    const hashedPassword = await bcrypt.hash(password, 10);
    await db.promise().query("INSERT INTO users (name, email, password_hash) VALUES (?, ?, ?)", [name, email, hashedPassword]);

    res.status(201).json({ message: "User registered successfully" });
  } catch (error) {
    res.status(500).json({ message: "Server error", error });
  }
});

// **Login API**
router.post("/login", async (req, res) => {
  const { email, password } = req.body;

  try {
    const [user] = await db.promise().query("SELECT * FROM users WHERE email = ?", [email]);
    if (user.length === 0) {
      return res.status(400).json({ message: "Invalid email or password" });
    }

    const isValidPassword = await bcrypt.compare(password, user[0].password_hash);
    if (!isValidPassword) {
      return res.status(400).json({ message: "Invalid email or password" });
    }

    const token = jwt.sign({ user_id: user[0].user_id, email: user[0].email }, process.env.JWT_SECRET, { expiresIn: "1h" });

    res.json({ message: "Login successful", token });
  } catch (error) {
    res.status(500).json({ message: "Server error", error });
  }
});

module.exports = router;
