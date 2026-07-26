import time
import json
import random
from datetime import datetime
import database as db
from bms_simulation import BatteryPackSimulator
from ai_bms_engine import EVBatteryAI

try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False

MQTT_BROKER = "broker.hivemq.com"
MQTT_PORT = 1883
MQTT_TOPIC = "ev/bms/telemetry"

def run_bms_simulator(interval_sec=1, max_loops=None):
    print(f"⚡ Starting Real-Time EV Battery Management System (BMS) Simulator... (Interval: {interval_sec}s)")
    db.init_db()
    pack_sim = BatteryPackSimulator()
    ai_engine = EVBatteryAI()
    
    client = None
    if MQTT_AVAILABLE:
        try:
            if hasattr(mqtt, "CallbackAPIVersion"):
                client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION1, "EV_BMS_Simulator")
            else:
                client = mqtt.Client("EV_BMS_Simulator")
            client.connect(MQTT_BROKER, MQTT_PORT, keepalive=60)
            client.loop_start()
            print(f"✓ Connected to MQTT Broker: {MQTT_BROKER}:{MQTT_PORT} (Topic: {MQTT_TOPIC})")
        except Exception as e:
            print(f"Note on MQTT Broker Connection: {e} (Writing telemetry directly to SQLite)")
            client = None

    pack_id = "EV_PACK_MODEL3_01"
    loop_count = 0
    
    try:
        while True:
            # Simulate driving discharge current (-40A to -10A) with occasional high current draw
            current_draw = -25.0 + random.uniform(-15.0, 10.0)
            imbalance = 0.0
            
            # Synthetic Event Injector (5% probability thermal surge or imbalance)
            if random.random() < 0.05:
                current_draw = -65.0 # Fast acceleration spike
                imbalance = 0.8
                
            state = pack_sim.simulate_pack_state(current_a=current_draw, cell_imbalance_factor=imbalance)
            
            payload = {
                "timestamp": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                "pack_id": pack_id,
                "cell_v1": state['cell_v1'],
                "cell_v2": state['cell_v2'],
                "cell_v3": state['cell_v3'],
                "cell_v4": state['cell_v4'],
                "pack_voltage": state['pack_voltage'],
                "pack_current_a": state['pack_current_a'],
                "temp_c": state['temp_c'],
                "int_resistance_mOhm": state['int_resistance_mOhm'],
                "soc_pct": round(random.uniform(40.0, 95.0), 1),
                "soh_pct": round(random.uniform(92.0, 99.0), 1),
                "status": state['status']
            }
            
            # Check AI Thermal Runaway Risk
            is_risk, score, desc = ai_engine.predict_thermal_runaway_risk(payload)
            if is_risk:
                db.log_thermal_alert(pack_id, payload['temp_c'], 1.8, "CRITICAL", desc)
                payload['status'] = 'THERMAL_RUNAWAY_WARNING'
                
            # Log into SQLite database
            db.log_cell_telemetry(payload)
            
            # Publish over MQTT
            if client:
                client.publish(MQTT_TOPIC, json.dumps(payload))
                
            print(f"[{payload['timestamp']}] {pack_id} | V_pack: {payload['pack_voltage']}V | I: {payload['pack_current_a']}A | Temp: {payload['temp_c']}°C | {payload['status']}")
            
            loop_count += 1
            if max_loops and loop_count >= max_loops:
                break
            time.sleep(interval_sec)
            
    except KeyboardInterrupt:
        print("\nBMS Simulator stopped.")
    finally:
        if client:
            client.loop_stop()
            client.disconnect()

if __name__ == "__main__":
    run_bms_simulator(interval_sec=0.1)

