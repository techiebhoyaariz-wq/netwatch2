from flask import Flask, jsonify, render_template
from database.db import getRecentAlerts, initDB
import threading
import sys
import os

# add parent directory to path so we can import our own modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = Flask(__name__)

@app.route('/')
def index():
    """Serves the main dashboard page"""
    return render_template('index.html')

@app.route('/api/alerts')
def apiAlerts():
    """Returns recent alerts as JSON for the dashboard to display"""
    alerts = getRecentAlerts(limit=50)
    # convert list of tuples into list of dictionaries
    alertList = []
    for row in alerts:
        alertList.append({
            "timestamp": row[0],
            "source_ip": row[1],
            "alert_type": row[2],
            "details": row[3]
        })
    return jsonify(alertList)

@app.route('/api/stats')
def apiStats():
    """Returns basic packet statistics for the dashboard charts"""
    from database.db import DB_PATH
    import sqlite3
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # count packets by protocol
    cursor.execute("SELECT protocol, COUNT(*) FROM packets GROUP BY protocol")
    protocolRows = cursor.fetchall()
    
    # total alerts count
    cursor.execute("SELECT COUNT(*) FROM alerts")
    totalAlerts = cursor.fetchone()[0]
    
    conn.close()
    
    protocols = {}
    for row in protocolRows:
        protocols[row[0]] = row[1]
    
    return jsonify({
        "protocols": protocols,
        "total_alerts": totalAlerts
    })

if __name__ == '__main__':
    initDB()
    app.run(debug=True, port=5000)
