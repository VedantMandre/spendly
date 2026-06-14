import random
import sys
from datetime import datetime
from werkzeug.security import generate_password_hash
from database.db import get_db

indian_first_names = [
    "Rahul", "Aarav", "Vihaan", "Aditya", "Sai", "Arjun", "Aryan", "Reyansh", "Krishna", "Ishaan",
    "Priya", "Ananya", "Aadhya", "Diya", "Saanvi", "Pooja", "Neha", "Riya", "Aaradhya", "Kavya"
]

indian_last_names = [
    "Sharma", "Verma", "Gupta", "Patel", "Mehta", "Singh", "Kumar", "Joshi", "Iyer", "Nair",
    "Reddy", "Rao", "Choudhury", "Das", "Banerjee", "Chatterjee", "Mishra", "Pandey", "Sen", "Roy"
]

def generate_random_user():
    first = random.choice(indian_first_names)
    last = random.choice(indian_last_names)
    name = f"{first} {last}"
    
    # email derived from name with random 2-3 digit suffix
    suffix = random.randint(10, 999)
    email = f"{first.lower()}.{last.lower()}{suffix}@gmail.com"
    return name, email

def main():
    conn = get_db()
    try:
        while True:
            name, email = generate_random_user()
            # check if exists
            row = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
            if not row:
                break
        
        password_hash = generate_password_hash("password123")
        created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        cursor = conn.execute(
            "INSERT INTO users (name, email, password_hash, created_at) VALUES (?, ?, ?, ?)",
            (name, email, password_hash, created_at)
        )
        conn.commit()
        user_id = cursor.lastrowid
        
        print(f"ID: {user_id}")
        print(f"Name: {name}")
        print(f"Email: {email}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
