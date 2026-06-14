import os
import random
import sys
from datetime import date, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_db

USER_ID = 2
COUNT = 5
MONTHS = 3

# (min, max, weight, [descriptions]) per category. Higher weight = more common.
CATEGORIES = {
    "Food": (50, 800, 8, [
        "Groceries from BigBazaar", "Lunch at local dhaba", "Swiggy order",
        "Vegetables from sabzi mandi", "Chai and snacks", "Dinner with family",
        "Zomato biryani order", "Milk and bread",
    ]),
    "Transport": (20, 500, 5, [
        "Auto rickshaw fare", "Ola cab ride", "Metro card recharge",
        "Petrol fill-up", "Bus ticket", "Uber to office",
    ]),
    "Bills": (200, 3000, 4, [
        "Electricity bill", "Mobile recharge (Jio)", "Broadband bill",
        "Gas cylinder refill", "DTH recharge", "Water bill",
    ]),
    "Health": (100, 2000, 2, [
        "Pharmacy - Apollo", "Doctor consultation", "Monthly medicines",
        "Lab tests", "Dentist visit",
    ]),
    "Entertainment": (100, 1500, 2, [
        "PVR movie tickets", "Netflix subscription", "Spotify Premium",
        "Weekend outing", "Gaming top-up",
    ]),
    "Shopping": (200, 5000, 3, [
        "Myntra clothes", "Amazon order", "Footwear from Bata",
        "Flipkart electronics", "Gift for friend",
    ]),
    "Other": (50, 1000, 3, [
        "Temple donation", "Stationery", "Salon haircut",
        "Misc household", "Courier charges",
    ]),
}


def random_date_within(months):
    today = date.today()
    span_days = months * 30
    offset = random.randint(0, span_days)
    return today - timedelta(days=offset)


def generate_expenses(user_id, count, months):
    names = list(CATEGORIES.keys())
    weights = [CATEGORIES[c][2] for c in names]
    rows = []
    for _ in range(count):
        cat = random.choices(names, weights=weights, k=1)[0]
        lo, hi, _w, descriptions = CATEGORIES[cat]
        amount = round(random.uniform(lo, hi), 2)
        description = random.choice(descriptions)
        d = random_date_within(months).isoformat()
        rows.append((user_id, amount, cat, d, description))
    return rows


def main():
    conn = get_db()
    try:
        user = conn.execute(
            "SELECT id FROM users WHERE id = ?", (USER_ID,)
        ).fetchone()
        if user is None:
            print(f"No user found with id {USER_ID}.")
            return

        rows = generate_expenses(USER_ID, COUNT, MONTHS)

        try:
            conn.execute("BEGIN")
            conn.executemany(
                "INSERT INTO expenses (user_id, amount, category, date, description) "
                "VALUES (?, ?, ?, ?, ?)",
                rows,
            )
            conn.commit()
        except Exception:
            conn.rollback()
            raise

        dates = [r[3] for r in rows]
        print(f"Inserted {len(rows)} expenses for user id {USER_ID}.")
        print(f"Date range: {min(dates)} to {max(dates)}")
        print("\nSample of inserted records:")
        sample = conn.execute(
            "SELECT id, amount, category, date, description "
            "FROM expenses WHERE user_id = ? ORDER BY id DESC LIMIT 5",
            (USER_ID,),
        ).fetchall()
        for r in sample:
            print(
                f"  #{r['id']}  Rs {r['amount']:>8.2f}  "
                f"{r['category']:<13}  {r['date']}  {r['description']}"
            )
    finally:
        conn.close()


if __name__ == "__main__":
    main()
