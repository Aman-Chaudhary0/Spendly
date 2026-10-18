import sqlite3
import random
from datetime import datetime, timedelta
from database.db import get_db

def seed():
    user_id = 3
    count = 3
    months = 6
    
    # Verify user exists
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        user = conn.execute("SELECT id FROM users WHERE id = ?", (user_id,)).fetchone()
        if not user:
            print(f"No user found with id {user_id}.")
            return

        # Expense data
        categories = {
            "Food": (50, 800),
            "Transport": (20, 500),
            "Bills": (200, 3000),
            "Health": (100, 2000),
            "Entertainment": (100, 1500),
            "Shopping": (200, 5000),
            "Other": (50, 1000),
        }
        
        # Proportional distribution
        cat_pool = (
            ["Food"] * 5 + 
            ["Transport"] * 3 + 
            ["Bills"] * 2 + 
            ["Shopping"] * 2 + 
            ["Other"] * 2 + 
            ["Entertainment"] * 1 + 
            ["Health"] * 1
        )
        
        expenses = []
        now = datetime.now()
        for _ in range(count):
            cat = random.choice(cat_pool)
            min_val, max_val = categories[cat]
            amount = round(random.uniform(min_val, max_val), 2)
            days_back = random.randint(0, months * 30)
            date = (now - timedelta(days=days_back)).strftime("%Y-%m-%d")
            
            desc_map = {
                "Food": ["Grocery Store", "Zomato", "Local Cafe", "Fruit Vendor"],
                "Transport": ["Uber", "Auto Rickshaw", "Petrol Pump", "Metro"],
                "Bills": ["Electricity Bill", "Water Bill", "Internet Bill", "Phone Recharge"],
                "Health": ["Pharmacy", "Doctor Visit", "Health Checkup"],
                "Entertainment": ["Movie Ticket", "Netflix", "Gaming Zone"],
                "Shopping": ["Amazon", "Flipkart", "Cloth Store", "Mall"],
                "Other": ["Gift", "Donation", "Misc Expense"],
            }
            desc = random.choice(desc_map[cat])
            expenses.append((amount, cat, date, desc))

        try:
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) VALUES (?, ?, ?, ?, ?)",
                [(user_id, *e) for e in expenses]
            )
            conn.commit()
            print(f"Successfully inserted {len(expenses)} expenses for user {user_id}.")
            print(f"Date range: {min(e[2] for e in expenses)} to {max(e[2] for e in expenses)}")
            
            print("\nSample records:")
            for e in expenses[:5]:
                # Removed Rupee symbol to avoid UnicodeEncodeError on some Windows terminals
                print(f"Date: {e[2]}, Amount: {e[0]}, Cat: {e[1]}, Desc: {e[3]}")
                
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            conn.rollback()

if __name__ == "__main__":
    seed()
