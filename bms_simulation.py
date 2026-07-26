import pandas as pd
import numpy as np

class BatteryPackSimulator:
    def __init__(self):
        # 4S Lithium-ion Battery Pack Specifications
        self.nominal_voltage = 14.8 # 4 * 3.7V
        self.max_voltage = 16.8     # 4 * 4.2V fully charged
        self.min_voltage = 12.0     # 4 * 3.0V fully discharged
        self.capacity_ah = 60.0     # 60 Ah capacity
        self.base_int_resistance = 12.0 # 12 mOhm base internal resistance

    def simulate_pack_state(self, current_a=-25.0, ambient_temp=25.0, cell_imbalance_factor=0.0, cooling_mode="none"):
        """
        Simulate electro-thermal battery dynamics for a 4S Li-ion pack.
        current_a: negative for discharge (driving), positive for charge (plugged in).
        cell_imbalance_factor: 0.0 for balanced cells, >0.1 for aging degraded cell.
        cooling_mode: 'liquid' (82% removal), 'air' (48% removal), or 'none' (12% removal).
        """
        # Calculate State-of-Charge (SoC %) based on current flow
        c_rate = abs(current_a) / self.capacity_ah
        
        # Base voltage per cell (3.0V - 4.2V range)
        v_base = 3.65 + 0.45 * np.tanh(current_a / 30.0) # Load voltage drop
        
        cell_1 = v_base + np.random.normal(0, 0.008)
        cell_2 = v_base + np.random.normal(0, 0.008)
        cell_3 = v_base + np.random.normal(0, 0.008)
        # Apply degradation imbalance to Cell 4
        cell_4 = v_base - (cell_imbalance_factor * 0.15) + np.random.normal(0, 0.008)
        
        cell_1 = max(min(cell_1, 4.25), 2.85)
        cell_2 = max(min(cell_2, 4.25), 2.85)
        cell_3 = max(min(cell_3, 4.25), 2.85)
        cell_4 = max(min(cell_4, 4.25), 2.85)
        
        pack_voltage = cell_1 + cell_2 + cell_3 + cell_4
        
        # Calculate Cell Voltage Imbalance Delta (V)
        voltages = [cell_1, cell_2, cell_3, cell_4]
        v_max = max(voltages)
        v_min = min(voltages)
        delta_v_mv = round((v_max - v_min) * 1000, 1) # Millivolts
        
        # Joule Heating Math: Q_heat = I^2 * R_internal
        r_internal_mOhm = self.base_int_resistance + (cell_imbalance_factor * 8.0)
        r_ohms = r_internal_mOhm / 1000.0
        joule_heat_watts = (current_a ** 2) * r_ohms

        # Cooling Mode Thermal Dissipation Math
        if cooling_mode == 'liquid':
            cooling_eff = 82.0
        elif cooling_mode == 'air':
            cooling_eff = 48.0
        else:
            cooling_eff = 12.0
            
        cooling_removal_watts = joule_heat_watts * (cooling_eff / 100.0)
        net_heat_watts = joule_heat_watts - cooling_removal_watts
        
        # Temperature rise estimate (°C)
        temp_c = ambient_temp + (net_heat_watts * 0.08) + (c_rate * 4.5)
        
        # Active Cell Balancing status
        balancing_active = delta_v_mv > 50.0 # Active balancing triggers if delta > 50mV
        
        status = "NORMAL"
        if temp_c > 60.0:
            status = "CRITICAL_OVERHEAT"
        elif delta_v_mv > 100.0:
            status = "SEVERE_CELL_IMBALANCE"
        elif balancing_active:
            status = "BALANCING_ACTIVE"
            
        return {
            'pack_voltage': round(pack_voltage, 2),
            'pack_current_a': round(current_a, 1),
            'c_rate': round(c_rate, 2),
            'cell_v1': round(cell_1, 3),
            'cell_v2': round(cell_2, 3),
            'cell_v3': round(cell_3, 3),
            'cell_v4': round(cell_4, 3),
            'delta_v_mv': delta_v_mv,
            'temp_c': round(temp_c, 1),
            'joule_heat_watts': round(joule_heat_watts, 2),
            'cooling_removal_watts': round(cooling_removal_watts, 2),
            'cooling_efficiency_pct': cooling_eff,
            'net_heat_watts': round(net_heat_watts, 2),
            'int_resistance_mOhm': round(r_internal_mOhm, 2),
            'balancing_active': balancing_active,
            'status': status
        }

if __name__ == "__main__":
    sim = BatteryPackSimulator()
    res = sim.simulate_pack_state(current_a=-45.0, cell_imbalance_factor=0.8)
    print("EV Battery Physics State:", res)
