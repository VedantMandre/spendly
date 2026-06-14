import sqlite3
import os
import sys

DB_PATH = "expense_tracker.db"

def main():
    if not os.path.exists(DB_PATH):
        print(f"Error: Database file '{DB_PATH}' not found.")
        return

    print("====================================================")
    print(" Spendly SQLite Interactive Shell")
    print(" Enter SQL queries. Type 'exit' or 'quit' to exit.")
    print("====================================================")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    while True:
        try:
            query = input("sqlite> ").strip()
            if not query:
                continue
            if query.lower() in ("exit", "quit"):
                break
            
            # Execute query
            cursor.execute(query)
            
            # If it's a SELECT query, display results
            if query.lower().startswith("select"):
                rows = cursor.fetchall()
                if not rows:
                    print("(No rows returned)")
                    continue
                
                # Print headers
                headers = rows[0].keys()
                print(" | ".join(headers))
                print("-" * (sum(len(h) for h in headers) + 3 * (len(headers) - 1)))
                
                for row in rows:
                    print(" | ".join(str(row[h]) for h in headers))
            else:
                conn.commit()
                print(f"Executed successfully. Rows affected: {cursor.rowcount}")

        except KeyboardInterrupt:
            print("\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")

    conn.close()

if __name__ == "__main__":
    main()
