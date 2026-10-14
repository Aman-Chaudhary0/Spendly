import sqlite3

DATABASE_PATH = 'spendly.db'

def get_db():
    """
    Returns a connection to the SQLite database.
    Enforces foreign key constraints on every connection.
    """
    conn = sqlite3.connect(DATABASE_PATH)
    # SQLite foreign keys are off by default; must be enabled per connection
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def init_db():
    """
    Initializes the database by creating the required tables.
    """
    with get_db() as conn:
        # Users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        """)

        # Expenses table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS expenses (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                amount REAL NOT NULL,
                category TEXT NOT NULL,
                date TEXT NOT NULL,
                description TEXT,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        conn.commit()

def seed_db():
    """
    Populates the database with initial test data.
    """
    with get_db() as conn:
        # Seed a test user
        # In a real app, passwords would be hashed
        conn.execute(
            "INSERT OR IGNORE INTO users (id, name, email, password) VALUES (?, ?, ?, ?)",
            (1, "Test User", "test@example.com", "hashed_password_123")
        )

        # Seed some test expenses for the test user
        expenses = [
            (1, 50.0, "Food", "2023-10-01", "Grocery shopping"),
            (1, 20.0, "Transport", "2023-10-02", "Taxi to work"),
            (1, 100.0, "Bills", "2023-10-03", "Internet bill"),
        ]
        conn.executemany(
            "INSERT OR IGNORE INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
            expenses
        )
        conn.commit()
