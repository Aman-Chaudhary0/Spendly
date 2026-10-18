from database.db import get_db
import sqlite3
from datetime import datetime

def get_user_by_id(user_id):
    """
    Retrieves a user by their ID and formats their membership date.
    """
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT name, email FROM users WHERE id = ?",
            (user_id,)
        )
        row = cursor.fetchone()
        if row:
            # Since created_at column is missing from the current schema,
            # we use a fallback value until the schema is updated.
            member_since = "Unknown"

            return {
                "name": row["name"],
                "email": row["email"],
                "member_since": member_since
            }
    return None

def get_summary_stats(user_id):
    """
    Fetch total expenses, count, and top category for a user.
    """
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # Total and Count
        stats_row = cursor.execute(
            "SELECT SUM(amount) as total, COUNT(*) as count FROM expenses WHERE user_id = ?",
            (user_id,)
        ).fetchone()

        total = stats_row["total"] if stats_row and stats_row["total"] is not None else 0
        count = stats_row["count"] if stats_row else 0

        # Top Category
        category_row = cursor.execute(
            "SELECT category FROM expenses WHERE user_id = ? GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
            (user_id,)
        ).fetchone()

        top_category = category_row["category"] if category_row else "—"

        return {
            "total_spent": total,
            "transaction_count": count,
            "top_category": top_category
        }

def get_recent_transactions(user_id, limit=10):
    """
    Retrieves the most recent transactions for a user.
    """
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT date, description, category, amount FROM expenses WHERE user_id = ? ORDER BY date DESC LIMIT ?",
            (user_id, limit)
        )
        rows = cursor.fetchall()
        return [
            {"date": row["date"], "desc": row["description"], "category": row["category"], "amount": row["amount"]}
            for row in rows
        ]

def get_category_breakdown(user_id):
    """
    Fetch spending breakdown by category for a user.
    """
    with get_db() as conn:
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute(
            "SELECT category as name, SUM(amount) as amount FROM expenses WHERE user_id = ? GROUP BY category ORDER BY amount DESC",
            (user_id,)
        )
        rows = cursor.fetchall()

        if not rows:
            return []

        total_spent = sum(row['amount'] for row in rows)
        if total_spent == 0:
            return []

        breakdown = []
        sum_percentages = 0

        for row in rows:
            amount = row['amount']
            percentage = round((amount / total_spent) * 100)
            breakdown.append({
                "name": row['name'],
                "amount": amount,
                "percentage": percentage
            })
            sum_percentages += percentage

        # Adjust the largest category to ensure total is exactly 100%
        diff = 100 - sum_percentages
        if diff != 0:
            breakdown[0]['percentage'] += diff

        return breakdown
