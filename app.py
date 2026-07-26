# EV Battery Intelligence Platform App (Refreshed)
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import time
import os

import importlib
import database as db
import bms_simulation
import ai_bms_engine

# Force Python process to reload updated module definitions from disk
importlib.reload(bms_simulation)
importlib.reload(ai_bms_engine)

from bms_simulation import BatteryPackSimulator
from ai_bms_engine import EVBatteryAI

# Page Configuration
st.set_page_config(
    page_title="EV Battery Intelligence Platform",
    page_icon="🔋",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# HIGH CONTRAST & BALANCED FULL-SCREEN DESIGN SYSTEM
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700;800&display=swap');
    
    /* Hide default Streamlit top header bar to prevent clipping at the top section */
    header[data-testid="stHeader"], [data-testid="stHeader"] {
        display: none !important;
        height: 0px !important;
        visibility: hidden !important;
    }
    
    /* Clean, spacious top margin & balanced layout without clipping */
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 0.5rem !important;
        padding-left: 1.2rem !important;
        padding-right: 1.2rem !important;
        max-width: 100% !important;
        width: 100% !important;
        margin: 0 auto !important;
        box-sizing: border-box !important;
    }

    /* Balanced side-by-side column spacing */
    [data-testid="stHorizontalBlock"] {
        width: 100% !important;
        max-width: 100% !important;
        margin-bottom: 8px !important;
        box-sizing: border-box !important;
    }

    [data-testid="column"] {
        min-width: 0 !important;
        flex: 1 1 0% !important;
        width: auto !important;
        box-sizing: border-box !important;
        padding: 0 4px !important;
    }

    /* Force text wrapping inside all cards & prevent word clipping */
    p, span, label, div, h1, h2, h3, h4, h5, h6 {
        color: #0f172a;
        word-wrap: break-word !important;
        overflow-wrap: break-word !important;
    }

    /* Streamlit Widget Labels (Sliders, Inputs, Toggles) */
    [data-testid="stWidgetLabel"] p,
    [data-testid="stWidgetLabel"] span,
    .stSlider label p,
    .stSlider label span,
    label p,
    label span {
        color: #0f172a !important;
        font-weight: 700 !important;
        font-size: 0.85rem !important;
        white-space: normal !important;
    }

    /* Slider Track & Controls */
    .stSlider, [data-testid="stSlider"] {
        width: 100% !important;
        max-width: 100% !important;
        box-sizing: border-box !important;
    }

    [data-testid="stTickBar"] div,
    [data-baseweb="slider"] div {
        color: #0f172a !important;
        font-weight: 700 !important;
    }

    /* Streamlit Metrics (st.metric) High Contrast Cards */
    [data-testid="stMetric"] {
        background: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 10px !important;
        padding: 8px 10px !important;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.03) !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    [data-testid="stMetricLabel"],
    [data-testid="stMetricLabel"] p,
    [data-testid="stMetricLabel"] span {
        color: #475569 !important;
        font-weight: 700 !important;
        font-size: 0.72rem !important;
        text-transform: uppercase !important;
        letter-spacing: 0.4px !important;
        white-space: nowrap !important;
        overflow: hidden !important;
        text-overflow: ellipsis !important;
    }

    [data-testid="stMetricValue"],
    [data-testid="stMetricValue"] div,
    [data-testid="stMetricValue"] span {
        color: #0f172a !important;
        font-size: clamp(1.0rem, 1.3vw, 1.4rem) !important;
        font-weight: 800 !important;
        word-break: break-word !important;
    }

    /* Plotly charts fit container strictly */
    .js-plotly-plot, .plot-container, [data-testid="stPlotlyChart"] {
        max-width: 100% !important;
        width: 100% !important;
        box-sizing: border-box !important;
    }

    /* Modern Styled Navigation Tabs with Wrap */
    [data-baseweb="tab-list"] {
        gap: 6px !important;
        background-color: transparent !important;
        border-bottom: 2px solid #cbd5e1 !important;
        padding-bottom: 2px !important;
        margin-bottom: 8px !important;
        flex-wrap: wrap !important;
        width: 100% !important;
        max-width: 100% !important;
    }
    
    [data-baseweb="tab"], 
    button[role="tab"] {
        background-color: #ffffff !important;
        border: 1.5px solid #cbd5e1 !important;
        border-radius: 8px 8px 0px 0px !important;
        padding: 6px 14px !important;
        transition: all 0.2s ease-in-out !important;
    }
    
    [data-baseweb="tab"] p, 
    [data-baseweb="tab"] div, 
    [data-baseweb="tab"] span,
    button[role="tab"] p {
        color: #334155 !important;
        font-weight: 700 !important;
        font-size: 0.88rem !important;
        opacity: 1 !important;
        white-space: nowrap !important;
    }
    
    /* Tab Hover State */
    [data-baseweb="tab"]:hover, 
    button[role="tab"]:hover {
        background-color: #eff6ff !important;
        border-color: #3b82f6 !important;
    }

    [data-baseweb="tab"]:hover p,
    [data-baseweb="tab"]:hover span,
    button[role="tab"]:hover p {
        color: #2563eb !important;
    }
    
    /* Tab Active/Selected State */
    [aria-selected="true"],
    button[role="tab"][aria-selected="true"] {
        background-color: #2563eb !important;
        border-color: #2563eb !important;
    }
    
    [aria-selected="true"] p, 
    [aria-selected="true"] div, 
    [aria-selected="true"] span,
    button[role="tab"][aria-selected="true"] p {
        color: #ffffff !important;
        font-weight: 800 !important;
    }

    /* Clean Metric Cards */
    .bms-card {
        background: #ffffff;
        border: 1.5px solid #cbd5e1;
        border-radius: 10px;
        padding: 8px 12px;
        box-shadow: 0 3px 8px rgba(0, 0, 0, 0.03);
        margin-bottom: 6px;
        width: 100%;
        box-sizing: border-box;
    }
    .bms-card-label {
        font-size: 0.70rem;
        font-weight: 800;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 0.4px;
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .bms-card-val {
        font-size: clamp(1.0rem, 1.3vw, 1.4rem);
        font-weight: 800;
        color: #2563eb;
        margin-top: 2px;
        word-break: break-word;
    }
    
    /* Physical Battery Cell Grid Card */
    .cell-grid-card {
        background: #ffffff;
        border: 1.5px solid #cbd5e1;
        border-radius: 10px;
        padding: 8px 10px;
        text-align: center;
        box-shadow: 0 3px 8px rgba(0,0,0,0.03);
        width: 100%;
        box-sizing: border-box;
    }
    .cell-num {
        font-size: 0.72rem;
        font-weight: 800;
        color: #334155;
        margin-bottom: 2px;
    }
    .cell-volts {
        font-size: clamp(1.0rem, 1.3vw, 1.4rem);
        font-weight: 800;
        color: #2563eb;
        word-break: break-word;
    }
    
    /* Floating Signature Pill */
    .author-pill {
        position: fixed;
        bottom: 10px;
        right: 14px;
        z-index: 99999;
        background: rgba(15, 23, 42, 0.80) !important;
        opacity: 0.85;
        backdrop-filter: blur(10px);
        -webkit-backdrop-filter: blur(10px);
        color: #ffffff !important;
        padding: 5px 12px;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.78rem;
        border: 1px solid rgba(255, 255, 255, 0.15);
        box-shadow: 0 4px 14px rgba(0, 0, 0, 0.2);
        transition: opacity 0.3s ease, background-color 0.3s ease, transform 0.2s ease;
    }
    
    .author-pill:hover {
        opacity: 1.0;
        background: rgba(15, 23, 42, 0.95) !important;
        transform: translateY(-2px);
    }
    
    .author-pill b, .author-pill span {
        color: #ffffff !important;
    }
</style>
""", unsafe_allow_html=True)

# Floating Author Signature
st.markdown('<div class="author-pill"><b> Developed by</b> Yashdeep</div>', unsafe_allow_html=True)

def setup_bms_engine():
    db.init_db()
    pack_sim = BatteryPackSimulator()
    ai_engine = EVBatteryAI()
    return pack_sim, ai_engine

pack_sim, ai_engine = setup_bms_engine()

# ---------------------------------------------------------
# ---------------------------------------------------------
# TOP STATIC BRAND HEADER & CONTROL BAR
# ---------------------------------------------------------
col_h1, col_h2, col_h3 = st.columns([2.2, 1.0, 1.2])
with col_h1:
    st.markdown('<h3 style="color:#0f172a; font-weight:800; margin:0;">⚡ EV BATTERY INTELLIGENCE PLATFORM</h3>', unsafe_allow_html=True)
    st.markdown('<p style="color:#64748b; font-weight:600; margin:0; font-size:0.80rem;">Real-Time 4S Li-ion Electro-Thermal Telemetry & AI Safety Analytics</p>', unsafe_allow_html=True)

with col_h2:
    live_stream = st.toggle("⚡ Live Telemetry", value=True, key="live_stream_toggle")

with col_h3:
    refresh_interval_sec = st.select_slider(
        "⏱️ Refresh Rate",
        options=[0.2, 0.5, 1.0, 2.0, 5.0],
        value=1.0,
        format_func=lambda x: f"{x}s ({round(1.0/x, 1)} Hz)",
        disabled=not live_stream,
        key="telemetry_refresh_rate_slider",
        help="Control live telemetry update speed across all dashboard components."
    )

run_interval = refresh_interval_sec if live_stream else None
hz_rate = round(1.0 / refresh_interval_sec, 1) if live_stream else 0.0

st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)

# ---------------------------------------------------------
# FRAGMENT 1: TOP METRICS BAR & LIVE STATUS INDICATOR
# ---------------------------------------------------------
@st.fragment(run_every=run_interval)
def render_top_metrics():
    df_telemetry = db.get_recent_bms_telemetry(limit=60)
    latest = df_telemetry.iloc[0] if len(df_telemetry) > 0 else None

    # Central Live Telemetry Status Banner
    status_badge_color = "#16a34a" if live_stream else "#64748b"
    status_text = "LIVE STREAMING 🟢" if live_stream else "STREAM PAUSED ⏸️"
    timestamp_str = latest["timestamp"] if latest is not None and "timestamp" in latest else "N/A"
    
    st.markdown(f"""
    <div style="background:#ffffff; border:1.5px solid #cbd5e1; border-radius:10px; padding:6px 14px; margin-bottom:10px; display:flex; align-items:center; justify-content:space-between; flex-wrap:wrap; box-shadow: 0 2px 6px rgba(0,0,0,0.03);">
        <div style="display:flex; align-items:center; gap:10px;">
            <span style="background:{status_badge_color}; color:#ffffff; font-weight:800; font-size:0.75rem; padding:3px 10px; border-radius:20px; text-transform:uppercase; letter-spacing:0.5px;">
                {status_text}
            </span>
            <span style="font-size:0.82rem; font-weight:700; color:#334155;">
                📡 Telemetry Rate: <b>{refresh_interval_sec}s</b> ({hz_rate} Hz)
            </span>
        </div>
        <div style="font-size:0.80rem; font-weight:700; color:#64748b;">
            🕒 Latest Telemetry Packet: <b style="color:#0f172a;">{timestamp_str}</b>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if latest is not None:
        m1, m2, m3, m4, m5 = st.columns(5)
        with m1:
            st.markdown(f'<div class="bms-card"><div class="bms-card-label">Pack Voltage</div><div class="bms-card-val">{latest["pack_voltage"]} V</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="bms-card"><div class="bms-card-label">Pack Current</div><div class="bms-card-val" style="color:{"#dc2626" if latest["pack_current_a"]<-40 else "#2563eb"};">{latest["pack_current_a"]} A</div></div>', unsafe_allow_html=True)
        with m3:
            st.markdown(f'<div class="bms-card"><div class="bms-card-label">Cell Temperature</div><div class="bms-card-val" style="color:{"#dc2626" if latest["temp_c"]>50 else "#16a34a"};">{latest["temp_c"]} °C</div></div>', unsafe_allow_html=True)
        with m4:
            st.markdown(f'<div class="bms-card"><div class="bms-card-label">State of Charge</div><div class="bms-card-val">{latest["soc_pct"]} %</div></div>', unsafe_allow_html=True)
        with m5:
            st.markdown(f'<div class="bms-card"><div class="bms-card-label">State of Health</div><div class="bms-card-val" style="color:#16a34a;">{latest["soh_pct"]} %</div></div>', unsafe_allow_html=True)

render_top_metrics()

# ---------------------------------------------------------
# STATIC TABS CONTAINER (NEVER RECREATED OR FLICKERED)
# ---------------------------------------------------------
tab_cells, tab_physics, tab_ai, tab_forecast = st.tabs([
    "🔋 Physical 4S Cell Grid",
    "⚡ Electro-Thermal Simulator",
    "🚨 Thermal Runaway AI Radar",
    "🔮 Capacity Decay & RUL Prediction"
])

# ---------------------------------------------------------
# TAB 1: PHYSICAL 4S CELL GRID (IN-PLACE FRAGMENT)
# ---------------------------------------------------------
with tab_cells:
    @st.fragment(run_every=run_interval)
    def render_tab_cells():
        df_telemetry = db.get_recent_bms_telemetry(limit=60)
        latest = df_telemetry.iloc[0] if len(df_telemetry) > 0 else None
        if latest is not None:
            st.markdown("##### 🔋 4S Battery Pack Physical Cell Array")
            
            c1, c2, c3, c4 = st.columns(4)
            with c1:
                st.markdown(f'<div class="cell-grid-card"><div class="cell-num">CELL #1</div><div class="cell-volts">{latest["cell_v1"]} V</div><p style="font-size:0.75rem; font-weight:700; color:#16a34a; margin:2px 0 0 0;">Optimal 🟢</p></div>', unsafe_allow_html=True)
            with c2:
                st.markdown(f'<div class="cell-grid-card"><div class="cell-num">CELL #2</div><div class="cell-volts">{latest["cell_v2"]} V</div><p style="font-size:0.75rem; font-weight:700; color:#16a34a; margin:2px 0 0 0;">Optimal 🟢</p></div>', unsafe_allow_html=True)
            with c3:
                st.markdown(f'<div class="cell-grid-card"><div class="cell-num">CELL #3</div><div class="cell-volts">{latest["cell_v3"]} V</div><p style="font-size:0.75rem; font-weight:700; color:#16a34a; margin:2px 0 0 0;">Optimal 🟢</p></div>', unsafe_allow_html=True)
            with c4:
                delta = abs(latest["cell_v1"] - latest["cell_v4"])
                st.markdown(f'<div class="cell-grid-card" style="border-color:{"#dc2626" if delta>0.1 else "#cbd5e1"};"><div class="cell-num">CELL #4</div><div class="cell-volts" style="color:{"#dc2626" if delta>0.1 else "#2563eb"};">{latest["cell_v4"]} V</div><p style="font-size:0.75rem; font-weight:700; color:{"#dc2626" if delta>0.1 else "#16a34a"}; margin:2px 0 0 0;">{"Imbalance 🔴" if delta>0.1 else "Optimal 🟢"}</p></div>', unsafe_allow_html=True)
                
            st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)
            
            g1, g2 = st.columns([2, 1])
            with g1:
                st.markdown("###### 📈 Cell Voltage Sync Waves (V1 - V4)")
                fig_v = px.line(
                    df_telemetry, x='timestamp', y=['cell_v1', 'cell_v2', 'cell_v3', 'cell_v4'],
                    color_discrete_sequence=['#2563eb', '#16a34a', '#d97706', '#dc2626']
                )
                fig_v.update_layout(
                    template="plotly_white", height=270, margin={"t": 10, "b": 10, "l": 10, "r": 10},
                    legend_title_text="", uirevision='constant', transition={'duration': 0}
                )
                st.plotly_chart(fig_v, use_container_width=True, key="chart_cell_v_sync")
                
            with g2:
                st.markdown("###### 📊 Pack Voltage Donut")
                fig_donut = go.Figure(go.Indicator(
                    mode = "gauge+number",
                    value = latest["pack_voltage"],
                    title = {'text': "Series Voltage (V)"},
                    gauge = {
                        'axis': {'range': [11.0, 17.0]},
                        'bar': {'color': "#2563eb"},
                        'steps': [
                            {'range': [11.0, 12.5], 'color': "#fee2e2"},
                            {'range': [12.5, 16.0], 'color': "#f1f5f9"},
                            {'range': [16.0, 17.0], 'color': "#dcfce7"}
                        ]
                    }
                ))
                fig_donut.update_layout(
                    template="plotly_white", height=270, margin={"t": 10, "b": 10, "l": 10, "r": 10},
                    uirevision='constant', transition={'duration': 0}
                )
                st.plotly_chart(fig_donut, use_container_width=True, key="chart_pack_voltage_gauge")

            with st.expander("📋 View Real-Time Telemetry Stream Table (Latest Packets First)"):
                df_sorted = df_telemetry.sort_values(by='id', ascending=False)
                st.dataframe(
                    df_sorted[['timestamp', 'cell_v1', 'cell_v2', 'cell_v3', 'cell_v4', 'pack_voltage', 'pack_current_a', 'temp_c', 'soc_pct', 'status']],
                    use_container_width=True,
                    height=180,
                    hide_index=True
                )

    render_tab_cells()

# ---------------------------------------------------------
# TAB 2: ADVANCED ELECTRO-THERMAL SIMULATOR & COOLING LAB
# ---------------------------------------------------------
with tab_physics:
    st.markdown("##### ⚡ Advanced Electro-Thermal Simulator & Thermal Management Lab")
    
    # PROMINENT INTERACTIVE COOLING MODE SELECTOR
    cool_sel = st.radio(
        "🧊 Select Active Thermal Management Cooling Mode",
        ["💧 Active Liquid Cooling (82% Heat Removal)", "🌀 Forced Air Fan Cooling (48% Heat Removal)", "🛑 Passive Convection (12% Heat Removal)"],
        horizontal=True
    )
    if "Liquid" in cool_sel:
        cool_mode = "liquid"
    elif "Air" in cool_sel:
        cool_mode = "air"
    else:
        cool_mode = "none"
        
    st.markdown("<div style='margin-bottom:4px;'></div>", unsafe_allow_html=True)
    
    c_s1, c_s2, c_s3 = st.columns(3)
    with c_s1:
        curr_draw = st.slider("Current Draw (A)", -100.0, 100.0, -40.0, 5.0, help="Discharge (-100A) / Charge (+100A)")
    with c_s2:
        imb_factor = st.slider("Cell Imbalance Factor", 0.0, 1.0, 0.3, 0.1)
    with c_s3:
        amb_temp = st.slider("Ambient Temp (°C)", -10.0, 50.0, 25.0, 1.0)
        
    sim_res = BatteryPackSimulator().simulate_pack_state(current_a=curr_draw, ambient_temp=amb_temp, cell_imbalance_factor=imb_factor, cooling_mode=cool_mode)
    
    p1, p2, p3, p4, p5, p6 = st.columns(6)
    with p1:
        st.metric("Voltage Delta (ΔV)", f"{sim_res['delta_v_mv']} mV")
    with p2:
        st.metric("Joule Heat Gen", f"{sim_res['joule_heat_watts']} W")
    with p3:
        st.metric("Cooling Removed", f"{sim_res['cooling_removal_watts']} W", delta=f"{sim_res['cooling_efficiency_pct']}% Eff")
    with p4:
        st.metric("Net Thermal Accum.", f"{sim_res['net_heat_watts']} W")
    with p5:
        st.metric("Pack Equilibrium Temp", f"{sim_res['temp_c']} °C")
    with p6:
        st.metric("Balancing Circuit", "ACTIVE 🟢" if sim_res['balancing_active'] else "NORMAL ⚪")

    st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)
    
    # 2 VISUAL SIMULATOR CHARTS (FIT ON SCREEN)
    col_sim_g1, col_sim_g2 = st.columns([1.5, 1.5])
    
    with col_sim_g1:
        st.markdown("###### 🔋 Simulated 4S Individual Cell Voltages")
        cell_df = pd.DataFrame({
            'Cell': ['Cell #1', 'Cell #2', 'Cell #3', 'Cell #4 (Imbalanced)'],
            'Voltage (V)': [sim_res['cell_v1'], sim_res['cell_v2'], sim_res['cell_v3'], sim_res['cell_v4']]
        })
        fig_sim_cells = px.bar(
            cell_df, x='Cell', y='Voltage (V)', color='Voltage (V)',
            color_continuous_scale=['#dc2626', '#2563eb', '#16a34a'],
            range_y=[2.5, 4.3]
        )
        fig_sim_cells.update_layout(
            template="plotly_white", height=230, margin={"t": 10, "b": 10, "l": 10, "r": 10},
            coloraxis_showscale=False
        )
        st.plotly_chart(fig_sim_cells, use_container_width=True, key="chart_sim_cell_voltages")

    with col_sim_g2:
        st.markdown("###### 🔥 Thermal Power Balance Breakdown (Watts)")
        thermal_df = pd.DataFrame({
            'Thermal Component': ['Joule Heat Generated', 'Cooling Heat Removed', 'Net Heat Retained'],
            'Power (Watts)': [sim_res['joule_heat_watts'], sim_res['cooling_removal_watts'], sim_res['net_heat_watts']],
            'Category': ['Gen', 'Cool', 'Net']
        })
        fig_sim_heat = px.bar(
            thermal_df, x='Thermal Component', y='Power (Watts)', color='Category',
            color_discrete_map={'Gen': '#dc2626', 'Cool': '#2563eb', 'Net': '#d97706'}
        )
        fig_sim_heat.update_layout(
            template="plotly_white", height=230, margin={"t": 10, "b": 10, "l": 10, "r": 10},
            showlegend=False
        )
        st.plotly_chart(fig_sim_heat, use_container_width=True, key="chart_sim_thermal_balance")

# ---------------------------------------------------------
# TAB 3: THERMAL RUNAWAY AI RADAR & EMERGENCY PROTOCOL
# ---------------------------------------------------------
with tab_ai:
    @st.fragment(run_every=run_interval)
    def render_tab_ai():
        df_telemetry = db.get_recent_bms_telemetry(limit=60)
        latest = df_telemetry.iloc[0] if len(df_telemetry) > 0 else None
        
        st.markdown("##### 🚨 IsolationForest AI Thermal Runaway Radar & Anomaly Early Warning")
        
        # INTERACTIVE TESTING & FAULT INJECTION CONTROLS
        col_t1, col_t2 = st.columns([2.2, 1.2])
        with col_t1:
            st.caption("🤖 Machine Learning Anomaly Engine: Unsupervised IsolationForest scoring cell temperature vs internal resistance spikes.")
        with col_t2:
            if st.button("🔥 Inject Thermal Anomaly Fault", use_container_width=True):
                db.log_cell_telemetry({
                    'timestamp': pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S'),
                    'pack_voltage': 14.1,
                    'pack_current_a': -78.5,
                    'soc_pct': 42.0,
                    'soh_pct': 88.0,
                    'cell_v1': 3.7,
                    'cell_v2': 3.7,
                    'cell_v3': 3.7,
                    'cell_v4': 3.0,
                    'temp_c': 64.5,
                    'int_resistance_mOhm': 24.5,
                    'status': 'THERMAL_WARNING'
                })
                db.log_thermal_alert("EV_PACK_MODEL3_01", 64.5, 2.5, "CRITICAL", "Thermal Runaway Imminent! (Temp > 60°C)")
                st.toast("🚨 Thermal Overheat Anomaly Injected!", icon="🔥")

        # RISK EVALUATION METRICS
        is_risk, risk_score, risk_msg = False, 0.10, "BATTERY HEALTHY"
        if latest is not None:
            is_risk, risk_score, risk_msg = EVBatteryAI().predict_thermal_runaway_risk(latest.to_dict())

        k_r1, k_r2, k_r3, k_r4 = st.columns(4)
        with k_r1:
            st.metric("AI Anomaly Risk Score", f"{risk_score}", delta="CRITICAL 🔴" if is_risk else "HEALTHY 🟢")
        with k_r2:
            outlier_count = len(df_telemetry[df_telemetry['status'] != 'NORMAL'])
            st.metric("Detected Outliers", f"{outlier_count} Packets")
        with k_r3:
            st.metric("HV Contactor Relay", "TRIPPED / OFF 🔴" if is_risk else "CONNECTED 🟢")
        with k_r4:
            st.metric("Cooling Pump Override", "100% MAX FLOW 🌊" if is_risk else "AUTO (NORMAL) 💧")

        st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)

        col_r1, col_r2 = st.columns([1.5, 1.1])
        with col_r1:
            st.markdown("###### 📈 Thermal Anomaly Scatter (Temp vs Internal Resistance)")
            fig_scatter = px.scatter(
                df_telemetry, x='temp_c', y='int_resistance_mOhm', color='status',
                hover_data=['timestamp', 'pack_current_a'],
                labels={'temp_c': 'Temperature (°C)', 'int_resistance_mOhm': 'Internal Resistance (mΩ)'},
                color_discrete_map={'NORMAL': '#16a34a', 'THERMAL_WARNING': '#dc2626', 'CELL_IMBALANCE': '#d97706'}
            )
            fig_scatter.add_vline(x=60.0, line_dash="dash", line_color="#dc2626", annotation_text="Critical Temp Cutoff (60°C)")
            fig_scatter.update_layout(
                template="plotly_white", height=270, margin={"t": 10, "b": 10, "l": 10, "r": 10},
                uirevision='constant', transition={'duration': 0}
            )
            st.plotly_chart(fig_scatter, use_container_width=True, key="chart_thermal_radar_scatter")
            
        with col_r2:
            st.markdown("###### 📊 AI Safety Incident Alerts Log (Latest First)")
            alerts = db.get_all_thermal_alerts()
            if len(alerts) > 0:
                # Ensure newest alert is always at row 1 on top
                if 'id' in alerts.columns:
                    alerts = alerts.sort_values(by='id', ascending=False)
                elif 'timestamp' in alerts.columns:
                    alerts = alerts.sort_values(by='timestamp', ascending=False)
                    
                avail_cols = [c for c in ['timestamp', 'temp_c', 'severity', 'description', 'status'] if c in alerts.columns]
                if not avail_cols:
                    avail_cols = list(alerts.columns)
                st.dataframe(alerts[avail_cols], use_container_width=True, height=190, hide_index=True)
            else:
                st.success("🟢 Zero Thermal Runaway Risk Detected. Battery Cell Array Healthy.")
                
            st.markdown(f"""
            <div class="bms-card" style="padding:10px 12px; margin-top:4px; border-color:{"#dc2626" if is_risk else "#cbd5e1"};">
                <div class="bms-card-label">BMS Emergency Protocol Status</div>
                <p style="font-size:0.78rem; font-weight:700; color:{"#dc2626" if is_risk else "#334155"}; margin:4px 0 0 0; line-height:1.4;">
                    <b>Diagnostic</b>: {risk_msg}<br>
                    <b>Action</b>: {"HV Breaker Tripped • Emergency Cabin Alert Broadcast" if is_risk else "Cell Array Monitoring Active • Nominals Normal"}
                </p>
            </div>
            """, unsafe_allow_html=True)

    render_tab_ai()

# ---------------------------------------------------------
# TAB 4: CAPACITY DECAY & RUL PREDICTION (CYCLES + DAYS DUAL METRICS)
# ---------------------------------------------------------
with tab_forecast:
    st.markdown("##### 🔮 RandomForest Capacity Degradation & RUL Forecast")
    
    df_telemetry_hist = db.get_recent_bms_telemetry(limit=60)
    
    col_fc1, col_fc2 = st.columns([2, 1])
    with col_fc1:
        cycles = st.slider("Projection Horizon (Cycles & Days)", 100, 1500, 600, 50)
    
    fc_df, meta = EVBatteryAI().forecast_soh_decay(future_cycles=cycles, df_bms=df_telemetry_hist)
    
    rul_cycles = meta['rul_cycles']
    rul_days = meta['rul_days']
    rul_years = meta['rul_years']
    c_per_day = meta['cycles_per_day']
    est_proj_days = int(cycles / c_per_day)
    
    with col_fc2:
        st.markdown(f'<p style="font-size:0.80rem; font-weight:700; color:#475569; margin:28px 0 0 0;">🗓️ Projection: <b>{cycles} Cycles</b> ≈ <b>{est_proj_days} Days</b> (~{round(est_proj_days/30, 1)} Mos)</p>', unsafe_allow_html=True)
    
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        st.metric("Remaining Useful Life (RUL)", f"{rul_cycles:,} Cycles", delta=f"~{rul_days:,} Days ({rul_years} Yrs)")
    with k2:
        st.metric("Estimated Drive Distance", f"{int(rul_cycles * 0.35):,} km")
    with k3:
        svc_days = meta.get('service_due_days', 300)
        svc_cyc = meta.get('service_due_cycles', 540)
        st.metric("Next Service Due", f"In ~{svc_days:,} Days", delta=f"~{svc_cyc:,} Cycles Left 🔧")
    with k4:
        st.metric("Health Classification", "OPTIMAL 🟢" if rul_cycles > 500 else "DEGRADED 🔴")

    st.markdown("<div style='margin-bottom:6px;'></div>", unsafe_allow_html=True)
    
    # 2-COLUMN BALANCED MAIN PANEL (FIT ON SCREEN)
    col_left, col_right = st.columns([1.8, 1.2])
    
    with col_left:
        st.markdown("###### 📈 SOH Degradation Curve (Cycles vs Estimated Days)")
        fig_area = px.area(
            fc_df, x='Charge Cycle', y='Predicted SoH (%)',
            hover_data=['Estimated Day'],
            color_discrete_sequence=['#2563eb']
        )
        fig_area.add_hline(y=70.0, line_dash="dash", line_color="#dc2626", annotation_text="EOL Cutoff (70%)")
        fig_area.update_layout(
            template="plotly_white", height=270, margin={"t": 10, "b": 10, "l": 10, "r": 10},
            uirevision='constant', transition={'duration': 0}
        )
        fig_area.update_traces(hovertemplate="<b>Cycle %{x}</b> (~Day %{customdata[0]})<br>Predicted SoH: <b>%{y}%</b>")
        st.plotly_chart(fig_area, use_container_width=True, key="chart_capacity_decay_area")
        
    with col_right:
        st.markdown("###### 📊 Cycle & Calendar Day Milestone Table (Latest Milestone First)")
        step = max(1, cycles // 6)
        checkpoints = list(range(1, cycles + 1, step))
        if cycles not in checkpoints:
            checkpoints.append(cycles)
        
        milestone_df = fc_df[fc_df['Charge Cycle'].isin(checkpoints)].copy()
        milestone_df = milestone_df[['Charge Cycle', 'Estimated Day', 'Predicted SoH (%)']]
        milestone_df['Status'] = milestone_df['Predicted SoH (%)'].apply(lambda x: 'Healthy 🟢' if x > 80 else ('Degraded 🟡' if x >= 70 else 'EOL Reached 🔴'))
        
        # Sort descending so latest/highest cycle milestone is on line 1 at top
        milestone_df = milestone_df.sort_values(by='Charge Cycle', ascending=False)
        
        st.dataframe(milestone_df, use_container_width=True, height=170, hide_index=True)

        st.markdown(f"""
        <div class="bms-card" style="padding:10px 12px; margin-top:4px;">
            <div class="bms-card-label">AI Life Expectancy & Electro-Thermal Analysis</div>
            <p style="font-size:0.78rem; font-weight:700; color:#334155; margin:4px 0 0 0; line-height:1.4;">
                Current SOH: <b>{meta.get('current_soh', 98.0)}%</b> • Decay Rate: <b>{meta.get('decay_rate_pct', 0.022)}%/cycle</b><br>
                Usage Pace: <b>{c_per_day} cycles/day</b><br>
                Expected Life: <b>{rul_cycles:,} cycles</b> (~<b>{rul_days:,} days</b> / <b>{rul_years} yrs</b>)<br>
                Service Due: <b>In ~{meta.get('service_due_days', 300):,} Days</b> (~<b>{meta.get('service_due_cycles', 540):,} Cycles</b>)
            </p>
        </div>
        """, unsafe_allow_html=True)
#cd C:\Users\yashd\.gemini\antigravity\scratch\ev_bms_ai_system ; python run_bms_system.py