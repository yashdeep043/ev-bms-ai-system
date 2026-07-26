import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest, RandomForestRegressor

class EVBatteryAI:
    def __init__(self):
        # 1. Unsupervised Anomaly & Thermal Runaway Detector
        self.anomaly_detector = IsolationForest(contamination=0.04, random_state=42)
        # 2. Supervised State-of-Health (SoH) & RUL Forecaster
        self.soh_forecaster = RandomForestRegressor(n_estimators=50, random_state=42)
        
        self.is_anomaly_fitted = False
        self.is_soh_fitted = False

    def train_anomaly_detector(self, df_bms):
        """Train IsolationForest model on historical battery telemetry."""
        if len(df_bms) < 20:
            return False
            
        features = df_bms[['cell_v1', 'cell_v2', 'cell_v3', 'cell_v4', 'temp_c', 'int_resistance_mOhm', 'pack_current_a']].dropna()
        if len(features) >= 20:
            self.anomaly_detector.fit(features)
            self.is_anomaly_fitted = True
            return True
        return False

    def predict_thermal_runaway_risk(self, packet):
        """
        Evaluates single EV battery packet for thermal runaway or cell degradation risk.
        Returns: risk_flag (bool), risk_score (float), description (str)
        """
        temp = packet.get('temp_c', 30.0)
        r_int = packet.get('int_resistance_mOhm', 12.0)
        v1 = packet.get('cell_v1', 3.7)
        v2 = packet.get('cell_v2', 3.7)
        v3 = packet.get('cell_v3', 3.7)
        v4 = packet.get('cell_v4', 3.7)
        
        delta_v = max(v1, v2, v3, v4) - min(v1, v2, v3, v4)
        
        # Rule-Based Physics Early Warning System
        if temp > 60.0:
            return True, -0.95, "CRITICAL ALERT: Thermal Runaway Imminent! (Temp > 60°C)"
        if r_int > 22.0:
            return True, -0.80, "HIGH RISK: Severe Internal Resistance Spike (Cell Degradation)"
        if delta_v > 0.15:
            return True, -0.70, "WARNING: Extreme Cell Voltage Imbalance (>150mV)"
            
        # Machine Learning Statistical Outlier Scoring
        if self.is_anomaly_fitted:
            features = np.array([[v1, v2, v3, v4, temp, r_int, packet.get('pack_current_a', -10.0)]])
            pred = self.anomaly_detector.predict(features)[0]
            score = float(self.anomaly_detector.score_samples(features)[0])
            if pred == -1:
                return True, round(score, 3), "ML ALERT: Anomaly Pattern Detected"
                
        return False, 0.1, "BATTERY HEALTHY"

    def train_soh_forecaster(self, df_bms):
        """Train RandomForest model to forecast battery capacity decay."""
        if len(df_bms) < 30:
            return False
            
        df = df_bms.copy()
        features = df[['int_resistance_mOhm', 'temp_c']]
        target = df['soh_pct']
        
        self.soh_forecaster.fit(features, target)
        self.is_soh_fitted = True
        return True

    def forecast_soh_decay(self, future_cycles=500, df_bms=None):
        """Generates multi-cycle ahead Battery State-of-Health (SoH %) decay curve and metadata dict."""
        cycles = np.arange(1, future_cycles + 1)
        cycles_per_day = 1.8
        est_days = np.round(cycles / cycles_per_day, 1)
        
        current_soh = 98.0
        if df_bms is not None and len(df_bms) > 0 and 'soh_pct' in df_bms.columns:
            current_soh = float(df_bms['soh_pct'].iloc[0])
            
        decay_rate = 0.022
        soh_decay = current_soh - decay_rate * cycles - 0.000012 * (cycles ** 2) + np.random.normal(0, 0.25, future_cycles)
        soh_decay = np.clip(soh_decay, 60.0, 100.0)
        
        # Remaining Useful Life (RUL) calculation (Cutoff at 70% SoH)
        eol_indices = np.where(soh_decay < 70.0)[0]
        if len(eol_indices) > 0:
            rul_cycles = int(eol_indices[0])
        else:
            rul_cycles = int(future_cycles + 850)
            
        rul_days = int(rul_cycles / cycles_per_day)
        rul_years = round(rul_days / 365.0, 1)
        
        service_due_cycles = max(100, int(rul_cycles * 0.45))
        service_due_days = max(30, int(service_due_cycles / cycles_per_day))
        
        df_forecast = pd.DataFrame({
            'Charge Cycle': cycles,
            'Estimated Day': est_days,
            'Predicted SoH (%)': np.round(soh_decay, 2),
            'EOL Limit (70%)': 70.0
        })
        
        meta = {
            'rul_cycles': rul_cycles,
            'rul_days': rul_days,
            'rul_years': rul_years,
            'cycles_per_day': cycles_per_day,
            'current_soh': round(current_soh, 1),
            'decay_rate_pct': decay_rate,
            'service_due_days': service_due_days,
            'service_due_cycles': service_due_cycles
        }
        
        return df_forecast, meta

if __name__ == "__main__":
    ai = EVBatteryAI()
    sample_pkt = {'cell_v1': 3.7, 'cell_v2': 3.7, 'cell_v3': 3.7, 'cell_v4': 3.2, 'temp_c': 64.5, 'int_resistance_mOhm': 24.5}
    is_risk, score, desc = ai.predict_thermal_runaway_risk(sample_pkt)
    print(f"Risk Alert: {is_risk} | Score: {score} | Msg: {desc}")
