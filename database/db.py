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
            details TEXT,
            severity TEXT
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

def insertAlert(source_ip, alert_type, details, severity):
    """Saves a security alert to the database"""
    timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO alerts (timestamp, source_ip, alert_type, details, severity)
        VALUES (?, ?, ?, ?, ?)
    """, (timestamp, source_ip, alert_type, details, severity))
    conn.commit()
    conn.close()

def getRecentAlerts(limit=50):
    """Returns the most recent alerts for the dashboard"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        SELECT timestamp, source_ip, alert_type, details, severity
        FROM alerts
        ORDER BY id DESC
        LIMIT ?
    """, (limit,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def getAlertStats():

    """Here, the COUNT of the alerts would be returned here! ALl based on Severity, use COUNT() to obtain say How many CRITICAL, How many MEDIUM etc"""


    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
         SELECT severity, COUNT(*)
         FROM alerts
         GROUP BY severity
    """)  #DO NOT forget to add THIS

    rows = cursor.fetchall()   #remember this returns the ROWS because cursor.fetchall() the results is returned from cursor.fetcall() as TUPLES but only inside function 
    #for that data from database to be obtained you need to use "Return Rows" or data is lost

    return rows


def getTOPIPs():

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
             SELECT source_ip, COUNT(*) AS total
             FROM alerts
             GROUP BY source_ip  
             ORDER BY total DESC 
             LIMIT 5                   
        """)  #DO NOT forget to add THIS


    #Remember, that GROUP BY, is usually by same field of something declared at the top!
    #ORDER BY is what SORTS the results we get and DESC means "HIGHEST FIRST so Highest to Lowest"
    #So ORDER BY total DESC means "sort by the count, biggest number at the top"
    
    rows = cursor.fetchall()

    return rows


