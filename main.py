import os
import sqlite3
import database
from gui import BookingApp


def main():
    print("DB path     :", database.DB_NAME)
    print("File exists?:", os.path.exists(database.DB_NAME))

    database.create_tables()

    # Check what tables are in the DB right now
    conn = sqlite3.connect(database.DB_NAME)
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    conn.close()
    print("Tables now  :", [t[0] for t in tables])

    database.seed_data()

    app = BookingApp()
    app.mainloop()

if __name__ == "__main__":
    main()
