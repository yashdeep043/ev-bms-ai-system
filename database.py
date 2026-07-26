import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "bms_telemetry.db")

def get_connection():
    return sqlite3.connect(DB_PATH, check_same_thread=False)

def init_db():
    """Initialize EV BMS database tables and seed baseline battery telemetry if empty."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # 1. Multi-Cell Battery Telemetry Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS cell_telemetry (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pack_id TEXT NOT NULL,
            cell_v1 REAL,
            cell_v2 REAL,
            cell_v3 REAL,
            cell_v4 REAL,
            pack_voltage REAL,
            pack_current_a REAL,
            temp_c REAL,
            int_resistance_mOhm REAL,
            soc_pct REAL,
            soh_pct REAL,
            status TEXT
        )
    ''')
    
    # 2. Thermal Runaway Alerts Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS thermal_alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            pack_id TEXT,
            temp_c REAL,
            temp_rate_c_per_sec REAL,
            severity TEXT,
            description TEXT
        )
    ''')
    
    # 3. AI Battery Health & Remaining Useful Life (RUL) Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS soh_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            cycle_count INTEGER,
            predicted_soh_pct REAL,
            estimated_rul_cycles INTEGER,
            health_category TEXT
        )
    ''')
    
    conn.commit()
    
    # Check if empty; if so, seed historical battery charge/discharge data
    cursor.execute("SELECT COUNT(*) FROM cell_telemetry")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_battery_history(conn)
        
    conn.close()

def seed_battery_history(conn):
    """Seed 24 hours of realistic 4S Li-ion battery pack charge/discharge telemetry."""
    now = datetime.now()
    records = []
    pack_id = "EV_PACK_MODEL3_01"
    
    # 240 samples representing a full drive + fast charge cycle
    for i in range(240):
        ts = (now - timedelta(minutes=(240 - i)*6)).strftime('%Y-%m-%d %H:%M:%S')
        
        # Simulate State of Charge (SoC %) discharging during drive, charging during plug-in
        cycle_phase = i % 120
        if cycle_phase < 80:
            # Driving / Discharging
            soc = max(100.0 - (cycle_phase * 1.0) + np.random.normal(0, 0.5), 15.0)
            current = -35.0 + np.random.normal(0, 5.0) # Discharging current (negative)
            temp = 25.0 + (cycle_phase * 0.25) + np.random.normal(0, 0.5) # Temperature rises
        else:
            # Fast Charging
            soc = min(20.0 + ((cycle_phase - 80) * 2.0) + np.random.normal(0, 0.5), 98.0)
            current = 50.0 + np.random.normal(0, 3.0) # Charging current (positive)
            temp = 45.0 - ((cycle_phase - 80) * 0.2) + np.random.normal(0, 0.5) # Cooling
            
        # Individual 4S Cell Voltages (Nominal 3.7V, Range 3.0V - 4.2V)
        v_cell_avg = 3.0 + (soc / 100.0) * 1.2
        cell_v1 = v_cell_avg + np.random.normal(0, 0.015)
        cell_v2 = v_cell_avg + np.random.normal(0, 0.015)
        cell_v3 = v_cell_avg + np.random.normal(0, 0.015)
        cell_v4 = v_cell_avg + np.random.normal(0, 0.015)
        
        pack_v = cell_v1 + cell_v2 + cell_v3 + cell_v4
        int_r = 12.5 + (i * 0.02) + np.random.normal(0, 0.2) # Internal resistance mOhm increases slowly
        soh = max(100.0 - (i * 0.03), 85.0) # State of Health decays slowly
        
        status = "NORMAL"
        if temp > 58.0:
            status = "THERMAL_WARNING"
        elif abs(cell_v1 - cell_v2) > 0.12:
            status = "CELL_IMBALANCE"
            
        records.append((ts, pack_id, round(cell_v1, 3), round(cell_v2, 3), round(cell_v3, 3), round(cell_v4, 3),
                        round(pack_v, 2), round(current, 2), round(temp, 1), round(int_r, 2),
                        round(soc, 1), round(soh, 1), status))
        
    cursor = conn.cursor()
    cursor.executemany('''
        INSERT INTO cell_telemetry 
        (timestamp, pack_id, cell_v1, cell_v2, cell_v3, cell_v4, pack_voltage, pack_current_a, temp_c, int_resistance_mOhm, soc_pct, soh_pct, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', records)
    conn.commit()

def log_cell_telemetry(data):
    """Insert single EV battery packet."""
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO cell_telemetry 
        (timestamp, pack_id, cell_v1, cell_v2, cell_v3, cell_v4, pack_voltage, pack_current_a, temp_c, int_resistance_mOhm, soc_pct, soh_pct, status)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        data.get("timestamp", datetime.now().strftime('%Y-%m-%d %H:%M:%S')),
        data.get("pack_id", "EV_PACK_MODEL3_01"),
        data.get("cell_v1", 3.70),
        data.get("cell_v2", 3.70),
        data.get("cell_v3", 3.70),
        data.get("cell_v4", 3.70),
        data.get("pack_voltage", 14.80),
        data.get("pack_current_a", -10.0),
        data.get("temp_c", 30.0),
        data.get("int_resistance_mOhm", 12.5),
        data.get("soc_pct", 75.0),
        data.get("soh_pct", 98.0),
        data.get("status", "NORMAL")
    ))
    conn.commit()
    conn.close()

def log_thermal_alert(pack_id, temp_c, rate, severity, description):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO thermal_alerts (timestamp, pack_id, temp_c, temp_rate_c_per_sec, severity, description)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), pack_id, temp_c, rate, severity, description))
    conn.commit()
    conn.close()

def get_recent_bms_telemetry(limit=100):
    conn = get_connection()
    df = pd.read_sql_query(f"SELECT * FROM cell_telemetry ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df

def get_all_thermal_alerts():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM thermal_alerts ORDER BY id DESC", conn)
    conn.close()
    return df

if __name__ == "__main__":
    init_db()
    print("EV BMS Database initialized and seeded successfully.")
