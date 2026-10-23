import os
import sqlite3

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_NAME = os.path.join(BASE_DIR, "campus_booking.db")

def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

def create_tables():
    conn = get_connection()
    cursor = conn.cursor()

    #Users table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL,
            campus TEXT
        )
    """)

    #Campuses table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS campuses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL
        )
    """)

    #Resources table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS resources (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            campus TEXT NOT NULL,
            resource_type TEXT
        )
    """)

    #Bookings table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            resource_code TEXT NOT NULL,
            username TEXT NOT NULL,
            campus TEXT NOT NULL,
            booking_date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            duration INTEGER NOT NULL,
            status TEXT DEFAULT 'active'
        )
    """)

    conn.commit()
    conn.close()

def seed_data():
    create_tables()
    conn = get_connection()
    cursor = conn.cursor()

    campuses = ["Centurion", "Bryston", "Pretoria"]
    for c in campuses:
        cursor.execute("INSERT OR IGNORE INTO campuses (name) VALUES (?)", (c,))

    default_users = [
        ("admin_cent", "admin321", "admin", "Centurion"),
        ("admin_bryn", "admin321", "admin", "Brynston"),
        ("admin_ptr", "admin321", "admin", "Pretoria"),
        ("operator", "op123", "operator", None)
    ]

    for u in default_users:
        cursor.execute(
            "INSERT OR IGNORE INTO users (username, password, role, campus) VALUES (?, ?, ?, ?)",
            u,
        )

    sample_resources = [
        ("LAB-CENT-01", "PC Lab 1", "Centurion", "PC Lab"),
        ("LAB-CENT-02", "PC Lab 2", "Centurion", "PC Lab"),
        ("PRJ-CENT-01", "Multimedia Projector", "Centurion", "Projector"),
        ("LAB-BRYN-01", "PC Lab A", "Brynston", "PC Lab"),
        ("SEM-BRYN-01", "Seminar Room 1", "Brynston", "Seminar Room"),
        ("LAB-PTR-01", "PC Lab P", "Pretoria", "PC Lab"),
        ("SEM-PTR-01", "Seminar Room P", "Pretoria", "Seminar Room"),
    ]

    for r in sample_resources:
        cursor.execute(
            "INSERT OR IGNORE INTO resources (resource_code, name, campus, resource_type) VALUES (?, ?, ?, ?)",
            r,
        )

    conn.commit()
    conn.close()

def add_user(username, password, role, campus=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (username, password, role, campus) VALUES (?, ?, ?, ?)",
            (username, password, role, campus),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()


def get_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None


def get_campuses():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM campuses")
    rows = cursor.fetchall()
    conn.close()
    return [row["name"] for row in rows]


def add_resources(resource_code, name, campus, resource_type):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO resources (resource_code, name, campus, resource_type) VALUES (?, ?, ?, ?)",
            (resource_code, name, campus, resource_type),
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False
    finally:
        conn.close()

def update_resource(resource_code, name, resource_type):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE resources SET name = ?, resource_type = ? WHERE resource_code = ?",
        (name, resource_type, resource_code),
    )
    conn.commit()
    conn.close()

def delete_resource(resource_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELET FROM resources WHERE resource_code = ?", (resource_code,))
    conn.commit()
    conn.close()

def get_resources(campus):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources WHERE campus = ?", (campus,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_all_resources():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM resources")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def create_booking(resource_code, username, campus, booking_date, start_time, duration):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        """INSERT INTO bookings 
           (resource_code, username, campus, booking_date, start_time, duration, status)
           VALUES (?, ?, ?, ?, ?, ?, 'active')""",
        (resource_code, username, campus, booking_date, start_time, duration),
    )
    conn.commit()
    conn.close()

def get_bookings_for_resource(resource_code):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM bookings WHERE resource_code = ? AND status = 'active'",
        (resource_code,),
    )
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_bookings_for_user(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE username = ?", (username,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def get_bookings_for_campus(campus):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings WHERE campus = ?", (campus,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def cancel_booking(booking_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE bookings SET status = 'cancelled' WHERE id = ?", (booking_id,)
    )
    conn.commit()
    conn.close()

def get_all_bookings():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM bookings")
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]