"""Ad-hoc SQL runner for the Spendly SQLite database.

Usage:
    .venv\\Scripts\\python.exe query.py "SELECT * FROM users"
    .venv\\Scripts\\python.exe query.py "SELECT * FROM expenses WHERE user_id = ?" 2

Notes:
- Wrap the SQL in quotes so the shell passes it as one argument.
- Extra arguments after the SQL are bound to ? placeholders (parameterised).
- SELECT/PRAGMA prints a table; INSERT/UPDATE/DELETE commits and reports rows.
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db import get_db


def print_table(rows):
    if not rows:
        print("(no rows)")
        return
    headers = rows[0].keys()
    data = [[("" if r[h] is None else str(r[h])) for h in headers] for r in rows]
    widths = [
        max(len(headers[i]), *(len(row[i]) for row in data))
        for i in range(len(headers))
    ]
    line = "  ".join(h.ljust(widths[i]) for i, h in enumerate(headers))
    print(line)
    print("  ".join("-" * widths[i] for i in range(len(headers))))
    for row in data:
        print("  ".join(row[i].ljust(widths[i]) for i in range(len(row))))
    print(f"\n({len(rows)} row{'s' if len(rows) != 1 else ''})")


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)

    sql = sys.argv[1]
    params = tuple(sys.argv[2:])

    conn = get_db()
    try:
        cursor = conn.execute(sql, params)
        if cursor.description is not None:  # SELECT / PRAGMA returns rows
            print_table(cursor.fetchall())
        else:  # INSERT / UPDATE / DELETE
            conn.commit()
            print(f"OK — {cursor.rowcount} row(s) affected.")
    except Exception as exc:
        print(f"Error: {type(exc).__name__}: {exc}", file=sys.stderr)
        sys.exit(1)
    finally:
        conn.close()


if __name__ == "__main__":
    main()
