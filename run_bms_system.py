import os
import sys
import subprocess
import time
import threading

def run_simulator_background():
    print("Starting background EV BMS Simulator process...")
    sim_script = os.path.join(os.path.dirname(__file__), "bms_simulator.py")
    subprocess.run([sys.executable, sim_script])

def main():
    print("==========================================================")
    print("⚡ AI-POWERED EV BATTERY MANAGEMENT SYSTEM (BMS) ⚡")
    print("==========================================================")
    
    # 1. Initialize Database
    import database as db
    db.init_db()
    print("✓ SQLite BMS Database Initialized & Seeded")
    
    # 2. Launch Background Simulator in separate thread
    sim_thread = threading.Thread(target=run_simulator_background, daemon=True)
    sim_thread.start()
    print("✓ EV Battery CAN Bus Telemetry Simulator Active")
    
    time.sleep(2)
    
    # 3. Launch Streamlit App
    app_path = os.path.join(os.path.dirname(__file__), "app.py")
    print("✓ Launching Streamlit EV BMS Dashboard on app.py...")
    subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])

if __name__ == "__main__":
    main()
