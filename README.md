# ⚡ AI-Powered EV Battery Management System (BMS)

An advanced, real-time **Electric Vehicle Battery Management System (BMS)** built with Python, Streamlit, Scikit-Learn, Plotly, SQLite, and MQTT.

![Python](https://img.shields.io/badge/Python-3.12-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-FF4B4B.svg)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-F7931E.svg)
![License](https://img.shields.io/badge/License-MIT-green.svg)

---

## 🌟 Key Features

* 🔋 **Physical 4S Cell Grid & Voltage Waveforms**: Real-time series monitoring of individual Lithium-ion cell voltages ($V_1 - V_4$), voltage imbalance delta ($\Delta V$), and active cell balancing logic.
* ⚡ **Electro-Thermal Simulator & Active Cooling Lab**: Dynamic simulation of Joule heating ($Q = I^2 R$) with interactive cooling modes:
  * 💧 **Active Liquid Cooling** (82% Heat Removal)
  * 🌀 **Forced Air Fan Cooling** (48% Heat Removal)
  * 🛑 **Passive Convection** (12% Heat Removal)
* 🚨 **IsolationForest AI Thermal Runaway Radar**: Unsupervised Machine Learning anomaly scoring to detect localized thermal runaway risk and severe internal resistance spikes before critical failure.
* 🔮 **RandomForest Capacity Decay & RUL Forecast**: Predicts battery State-of-Health (SoH %) degradation over charge cycles and maps remaining useful life to calendar days and years.
* 🎛️ **Central Live Telemetry Speed Control**: Integrated header slider allowing real-time rate control from **0.2s (5.0 Hz)** to **5.0s (0.2 Hz)** across all dashboard components.
* 🛡️ **Emergency Contactor Relays & Fault Injection**: High-voltage battery breaker relay trip mechanism (<10ms isolation) and synthetic fault injection testing.

---

## 🏗️ System Architecture

```
[ CAN Bus Telemetry Simulator ] ---> [ SQLite Database (bms_telemetry.db) ]
              │                                      │
              ├───> [ MQTT Broker (paho-mqtt) ]       ├───> [ IsolationForest AI Engine ]
                                                     └───> [ Streamlit Web Platform (app.py) ]
```

---

## 📂 Project Structure

```text
ev_bms_ai_system/
├── app.py                   # Streamlit Frontend & Live Dashboard
├── ai_bms_engine.py         # IsolationForest Anomaly & RandomForest RUL Models
├── bms_simulation.py        # Electro-Thermal Physics & Battery Dynamics Engine
├── bms_simulator.py         # Background CAN Bus Telemetry & MQTT Publisher
├── database.py              # SQLite Data Access Layer & Alert Logging
├── run_bms_system.py        # Master System Orchestrator
├── Run_EV_BMS.bat           # Windows 1-Click Launch Script
├── build_10_page_pdf.py     # Master Technical Manual PDF Generator
├── requirements.txt         # Project Dependencies
└── README.md                # Documentation & Overview
```

---

## 🚀 Getting Started

### 1. Clone the Repository
```bash
git clone https://github.com/yashdeep043/ev-bms-ai-system.git
cd ev-bms-ai-system
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the Master BMS Application
```bash
python run_bms_system.py
```
*(Or double-click `Run_EV_BMS.bat` on Windows)*.

---

## 📑 Technical Documentation

* 📄 **Master PDF Manual**: Includes complete 11-page technical reference, mathematical equations, database schemas, and codebase annotations.

---

## 👤 Author

**Developed by Yashdeep**  
*EV Power Electronics & Battery Intelligence Engineering*
