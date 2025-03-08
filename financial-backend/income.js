const express = require("express");
const mysql = require("mysql2");
const util = require("util");

const router = express.Router();

// ✅ MySQL Database Connection
const db = mysql.createConnection({
  host: "localhost",
  user: "root",
  password: "",
  database: "financialmanagement",
});

db.connect((err) => {
  if (err) {
    console.error("Database connection failed: " + err.message);
  } else {
    console.log("✅ Connected to MySQL database");
  }
});

// Enable async/await for queries
db.query = util.promisify(db.query);

// ✅ CREATE Transaction (income or expense)
// ✅ CREATE Transaction (with dynamic user_id and transaction_type)
router.post("/", async (req, res) => {
    console.log("📌 Creating a new transaction...", req.body);
  
    const { user_id = 1, amount, category, transaction_type, transaction_date, description } = req.body;
  
    // Check if user_id exists in the users table
    const userCheckSql = `SELECT * FROM users WHERE user_id = ?`;
    try {
      const userExists = await db.query(userCheckSql, [user_id]);
      if (userExists.length === 0) {
        console.log("❌ User not found");
        return res.status(404).json({ message: "User not found" });
      }
  
      // Proceed with transaction insertion
      const sql = `INSERT INTO transactions (user_id, amount, transaction_type, category, transaction_date, description) 
                   VALUES (?, ?, ?, ?, ?, ?)`;
      const result = await db.query(sql, [user_id, amount, transaction_type, category, transaction_date, description]);
      console.log("✅ Transaction added:", result.insertId);
      res.status(201).json({ message: "Transaction added", transaction_id: result.insertId });
    } catch (err) {
      console.error("❌ Error creating transaction:", err.message);
      res.status(500).json({ error: err.message });
    }
  });
  
// ✅ READ All Transactions (Income & Expense)
router.get("/", async (req, res) => {
  console.log("📌 Fetching all transactions...");
  const sql = `SELECT * FROM transactions`;
  try {
    const results = await db.query(sql);
    console.log("✅ Transactions retrieved:", results.length);
    res.json(results);
  } catch (err) {
    console.error("❌ Error fetching transactions:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ✅ UPDATE Transaction (Income or Expense)
router.put("/:id", async (req, res) => {
  console.log(`📌 Updating transaction with ID: ${req.params.id}`);
  const { amount, category, transaction_type, transaction_date, description } = req.body;

  if (!transaction_type || !['income', 'expense'].includes(transaction_type)) {
    return res.status(400).json({ error: "Invalid transaction type. It must be either 'income' or 'expense'." });
  }

  const sql = `UPDATE transactions SET amount = ?, category = ?, transaction_type = ?, transaction_date = ?, description = ? 
               WHERE transaction_id = ?`;
  try {
    const result = await db.query(sql, [amount, category, transaction_type, transaction_date, description, req.params.id]);
    if (result.affectedRows === 0) {
      console.log("❌ Transaction not found or unchanged");
      return res.status(404).json({ message: "Transaction not found or unchanged" });
    }
    console.log("✅ Transaction updated");
    res.json({ message: "Transaction updated" });
  } catch (err) {
    console.error("❌ Error updating transaction:", err.message);
    res.status(500).json({ error: err.message });
  }
});

// ✅ DELETE Transaction
router.delete("/:id", async (req, res) => {
  console.log(`📌 Deleting transaction with ID: ${req.params.id}`);
  const sql = `DELETE FROM transactions WHERE transaction_id = ?`;
  try {
    const result = await db.query(sql, [req.params.id]);
    if (result.affectedRows === 0) {
      console.log("❌ Transaction not found");
      return res.status(404).json({ message: "Transaction not found" });
    }
    console.log("✅ Transaction deleted");
    res.json({ message: "Transaction deleted" });
  } catch (err) {
    console.error("❌ Error deleting transaction:", err.message);
    res.status(500).json({ error: err.message });
  }
});

module.exports = router;
