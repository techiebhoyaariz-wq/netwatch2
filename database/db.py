import sqlite3
import time

# database file stored in project root
DB_PATH = "/tmp/netwatch.db"



def initDB():
    """
    Creates the database and tables if they don't exist yet.
    Called once when the program starts.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # table to store every captured packet
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS packets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_ip TEXT,
            dest_ip TEXT,
            protocol TEXT,
            size INTEGER
        )
    """)

    # table to store every alert raised
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            source_ip TEXT,
            alert_type TEXT,
            details TEXT
        )
    """)

    conn.commit()
    conn.close()
    print("Database initialised successfully")

def insertPacket(timestamp, source_ip, dest_ip, protocol, size):
    """Saves a captured packet to the database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO packets (timestamp, source_ip, dest_ip, protocol, size)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, source_ip, dest_ip, protocol, size))
    conn.commit()
    conn.close()

def insertAlert(source_ip, alert_type, details):
    """Saves a security alert to the database"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (timestamp, source_ip, alert_type, details)
        VALUES (?, ?, ?, ?)
    """, (timestamp, source_ip, alert_type, details))
    conn.commit()
    conn.close()

def getRecentAlerts(limit=50):
    """Returns the most recent alerts for the dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, source_ip, alert_type, details
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows
