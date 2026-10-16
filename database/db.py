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

def create_user(name, email, password):
    """
    Creates a new user in the database.
    Returns the ID of the created user.
    Raises sqlite3.IntegrityError if the email is already registered.
    """
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, password)
        )
        conn.commit()
        return cursor.lastrowid

def get_user_by_email(email):
    """
    Retrieves a user from the database by their email.
    Returns the user row as a tuple if found, otherwise None.
    """
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users WHERE email = ? LIMIT 1",
            (email,)
        )
        return cursor.fetchone()

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
