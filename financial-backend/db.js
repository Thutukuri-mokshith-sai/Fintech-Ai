const mysql = require('mysql');

const db = mysql.createConnection({
    host: 'localhost', // Change if using a remote database
    user: 'root', // Replace with your MySQL username
    password: '', // Replace with your MySQL password
    database: 'financialmanagement' // Your database name
});

db.connect((err) => {
    if (err) {
        console.error('Database connection failed: ' + err.stack);
        return;
    }
    console.log('Connected to database.');
});

module.exports = db;
