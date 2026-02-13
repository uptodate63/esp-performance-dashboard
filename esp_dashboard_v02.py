
import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from scipy.interpolate import interp1d
from datetime import datetime
import io

# Page configuration
st.set_page_config(
    page_title="ESP Performance Dashboard",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern dark theme with proper font colors
st.markdown("""
    <style>
    .main {
        background-color: #0D1117;
    }
    .stApp {
        background-color: #0D1117;
    }
    h1, h2, h3, h4, h5, h6 {
        color: #E6EDF3 !important;
    }
    p, label, div, span {
        color: #C9D1D9 !important;
    }
    .stMarkdown {
        color: #C9D1D9 !important;
    }
    .metric-card {
        background-color: #161B22;
        padding: 20px;
        border-radius: 10px;
        border: 1px solid #30363D;
        margin: 10px 0;
    }
    .status-optimal {
        color: #00FF88 !important;
        font-weight: bold;
        font-size: 1.2em;
    }
    .status-warning {
        color: #FF1744 !important;
        font-weight: bold;
        font-size: 1.2em;
    }
    div[data-testid="stMetricValue"] {
        font-size: 1.8em;
        color: #58A6FF !important;
    }
    div[data-testid="stMetricLabel"] {
        color: #8B949E !important;
    }
    div[data-testid="stMetricDelta"] {
        color: #7EE787 !important;
    }
    input, textarea, select {
        color: #E6EDF3 !important;
        background-color: #0D1117 !important;
        border-color: #30363D !important;
    }
    .stButton>button {
        color: #FFFFFF !important;
        border-color: #238636 !important;
    }
    .st-emotion-cache-16txtl3 {
        color: #C9D1D9 !important;
    }
    section[data-testid="stSidebar"] {
        background-color: #0D1117 !important;
    }
    section[data-testid="stSidebar"] label {
        color: #C9D1D9 !important;
    }
    .calculation-section {
        background-color: #161B22;
        padding: 15px;
        border-radius: 8px;
        border-left: 3px solid #58A6FF;
        margin: 10px 0;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state for user inputs
def init_session_state():
    """Initialize all session state variables if they don't exist"""
    defaults = {
        'pump_data_loaded': False,
        'design_calculated': False,
        'custom_pump_loaded': False,
        # ESP Selection inputs
        'pump_model': '',
        'bep_flow': None,
        'rec_min': None,
        'rec_max': None,
        'bhp_per_stage': None,
        # Well Data inputs
        'well_name': '',
        'perf_start_depth_md': None,
        'perf_start_depth_tvd': None,
        'pump_setting_depth_tvd': None,
        'pump_setting_depth_md': None,
        'tubing_id': None,
        'target_rate': None,
        'water_cut': None,
        # Pressure & Temperature inputs
        'p_wh': None,
        'static_pressure': None,
        'bottom_hole_temp': None,
        # Fluid Properties inputs
        'water_sg': None,
        'oil_api': None,
        'gas_sg': None,
        'bubble_point_pressure': None,
        'gas_compressibility': None,
        'gor': None,
        'productivity_index': None,
        # Equipment inputs
        'pump_od': None,
        'num_rgs_od400': None,
        'num_rgs_od500': None,
        'num_agh_od400': None,
        'num_agh_od500': None,
        'cable_number': None,
        # Electrical inputs
        'motor_hp_nameplate': None,
        'motor_voltage_nameplate': None,
        'motor_ampere_nameplate': None,
        'motor_frequency': None,
        'transformer_voltage': None,
        'motor_power_factor': None,
        'motor_efficiency': None,
        'pump_efficiency': None,
        # Live monitoring inputs - persist these
        'pip_value': None,
        'pdp_value': None,
        'p_gradient_value': None,
        'actual_stages_value': None,
    }
    
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value

# Call initialization
init_session_state()

# Default pump curve data (ESP-3000) - only for reference
DEFAULT_Q_CURVE = [
    48.86,111.21,159.86,201.57,257.17,305.83,361.43,433.98,472.69,528.24,
    684.46,736.78,827.12,910.52,986.38,1070.38,1145.84,1267.20,1327.36,
    1417.91,1516.22,1626.44,1737.84,1783.25,1897.50,1973.98,2001.76,
    2106.02,2163.58,2266.88,2363.20,2502.20,2561.76,2682.92,2794.13,
    2898.38,3009.60,3113.86,3225.06,3336.27,3447.48,3544.79,3649.03,
    3753.41,3829.76,3920.12,4000.33,4078.93,4177.38,4280.70,4387.16
]

DEFAULT_H_CURVE = [
    40.27,40.51,40.76,41.01,41.25,41.33,41.63,41.87,42.12,42.24,
    42.61,42.86,43.11,43.28,43.33,43.36,43.36,43.33,43.33,42.93,
    42.74,42.37,42.00,41.83,41.03,40.51,40.27,39.40,38.88,38.28,
    37.48,36.07,35.45,34.21,32.86,31.50,30.02,28.53,26.80,24.93,
    23.10,21.37,19.30,17.66,15.68,13.95,12.10,10.24,8.06,8.06,8.89
]

# Title
st.markdown("<h1 style='text-align: center; color: #58A6FF;'>⚡ ESP Performance Dashboard v2.0</h1>", 
            unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #7D8590;'>Real-time Electric Submersible Pump Monitoring & Analysis with ESP Running Sheet Calculations</p>", 
            unsafe_allow_html=True)
st.markdown("---")

# Sidebar for navigation
with st.sidebar:
    st.image("https://img.icons8.com/fluency/96/000000/oil-industry.png", width=80)
    st.markdown("<h2 style='color: #E6EDF3;'>Navigation</h2>", unsafe_allow_html=True)
    page = st.radio("Select Mode:", 
                    ["📊 Part 1: Design & Sizing", "🔴 Part 2: Live Monitoring"],
                    label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("<h3 style='color: #E6EDF3;'>About</h3>", unsafe_allow_html=True)
    st.info("""
    **Part 1:** Complete ESP system design with running sheet calculations including:
    - Custom pump curve excel data upload
    - Well fluid properties
    - PVT calculations
    - ESP Electrical parameters
    
    **Part 2:** Monitor live ESP operation with real-time sensor data and performance tracking.
    """)
    
    st.markdown("---")
    st.markdown("<h4 style='color: #E6EDF3;'>Quick Stats</h4>", unsafe_allow_html=True)
    if st.session_state.design_calculated:
        st.metric("Design Flow", f"{st.session_state.get('target_rate', 0):.0f} bpd")
        st.metric("Required Stages", f"{st.session_state.get('n_stages', 0)}")
        st.metric("TDH", f"{st.session_state.get('TDH_design', 0):.0f} ft")

# ==================== PART 1: DESIGN & SIZING ====================
if page == "📊 Part 1: Design & Sizing":
    st.header("📊 Part 1: ESP System Design & Sizing")
    
    # Create tabs for better organization
    tab1, tab2, tab3, tab4 = st.tabs(["🔧 ESP Selection", "🏭 Well & Fluid Data", "⚡ Equipment & Electrical Parameters", "📋 Results & Analysis"])
    
    # ========== TAB 1: ESP SELECTION ==========
    with tab1:
        st.subheader("🔧 Pump Curve Data")
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            pump_model = st.text_input(
                "ESP Model", 
                value=st.session_state.pump_model,
                placeholder="e.g., ESP-3000",
                key="pump_model_input"
            )
            st.session_state.pump_model = pump_model
            
            pump_source = st.radio("Pump Data Source:", 
                                  ["Use Default Pump (ESP-3000)", "Upload Custom Pump Curve"],
                                  key="pump_source")
            
            if pump_source == "Use Default Pump (ESP-3000)":
                q_curve_data = DEFAULT_Q_CURVE
                h_curve_data = DEFAULT_H_CURVE
                st.success(f"✓ Loaded {len(q_curve_data)} data points from default pump")
                st.session_state.custom_pump_loaded = False
                
            else:  # Upload Custom Pump Curve
                st.info("📤 Upload an Excel file with pump performance data")
                st.markdown("""
                **Excel Format Requirements:**
                - Column 1: Flow Rate (bpd)
                - Column 2: Head per Stage (ft)
                - Data should start from row 1, Column A
                - No headers needed
                """)
                
                uploaded_file = st.file_uploader("Choose Excel file", type=['xlsx', 'xls'], key="pump_upload")
                
                if uploaded_file is not None:
                    try:
                        # Read the Excel file
                        df = pd.read_excel(uploaded_file, header=None)
                        
                        # Assume first column is flow, second is head
                        q_curve_data = df.iloc[:, 0].dropna().tolist()
                        h_curve_data = df.iloc[:, 1].dropna().tolist()
                        
                        # Validate data
                        if len(q_curve_data) != len(h_curve_data):
                            st.error("❌ Flow and Head data must have the same length!")
                            q_curve_data = DEFAULT_Q_CURVE
                            h_curve_data = DEFAULT_H_CURVE
                        elif len(q_curve_data) < 3:
                            st.error("❌ Need at least 3 data points for interpolation!")
                            q_curve_data = DEFAULT_Q_CURVE
                            h_curve_data = DEFAULT_H_CURVE
                        else:
                            st.success(f"✓ Successfully loaded {len(q_curve_data)} data points from Excel")
                            st.session_state.custom_pump_loaded = True
                            
                            # Show preview
                            preview_df = pd.DataFrame({
                                'Flow (bpd)': q_curve_data[:10],
                                'Head (ft)': h_curve_data[:10]
                            })
                            with st.expander("📊 Preview First 10 Points"):
                                st.dataframe(preview_df, width='stretch')
                    except Exception as e:
                        st.error(f"❌ Error reading Excel file: {str(e)}")
                        q_curve_data = DEFAULT_Q_CURVE
                        h_curve_data = DEFAULT_H_CURVE
                else:
                    q_curve_data = DEFAULT_Q_CURVE
                    h_curve_data = DEFAULT_H_CURVE
                    st.warning("⚠️ No file uploaded. Using default pump data.")
        
        with col2:
            st.markdown("### 📈 Performance Parameters")
            
            bep_flow = st.number_input(
                "BEP Flow Rate (bpd)", 
                value=st.session_state.bep_flow if st.session_state.bep_flow is not None else None,
                placeholder="e.g., 2500",
                step=10.0, 
                help="Best Efficiency Point flow rate"
            )
            st.session_state.bep_flow = bep_flow
            
            rec_min = st.number_input(
                "Recommended Min Flow (bpd)", 
                value=st.session_state.rec_min if st.session_state.rec_min is not None else None,
                placeholder="e.g., 2000",
                step=10.0,
                help="Minimum recommended operating flow"
            )
            st.session_state.rec_min = rec_min
            
            rec_max = st.number_input(
                "Recommended Max Flow (bpd)", 
                value=st.session_state.rec_max if st.session_state.rec_max is not None else None,
                placeholder="e.g., 3000",
                step=10.0,
                help="Maximum recommended operating flow"
            )
            st.session_state.rec_max = rec_max
            
            bhp_per_stage = st.number_input(
                "BHP per Stage (read from pump curve)", 
                value=st.session_state.bhp_per_stage if st.session_state.bhp_per_stage is not None else None,
                placeholder="e.g., 0.936",
                step=0.01,
                help="Brake horsepower per stage at design point"
            )
            st.session_state.bhp_per_stage = bhp_per_stage
    
    # ========== TAB 2: WELL & FLUID DATA ==========
    with tab2:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### 🏭 Well Data")
            
            well_name = st.text_input(
                "Well Name", 
                value=st.session_state.well_name,
                placeholder="e.g., NT3"
            )
            st.session_state.well_name = well_name
            
            st.markdown("#### 📏 Well Geometry")
            
            perf_start_depth_md = st.number_input(
                "Perforation Start Depth (MD, ft)", 
                value=st.session_state.perf_start_depth_md if st.session_state.perf_start_depth_md is not None else None,
                placeholder="e.g., 6200",
                step=100
            )
            st.session_state.perf_start_depth_md = perf_start_depth_md
            
            perf_start_depth_tvd = st.number_input(
                "Perforation Start Depth (TVD, ft)", 
                value=st.session_state.perf_start_depth_tvd if st.session_state.perf_start_depth_tvd is not None else None,
                placeholder="e.g., 6200",
                step=100
            )
            st.session_state.perf_start_depth_tvd = perf_start_depth_tvd
            
            pump_setting_depth_md = st.number_input(
                "Pump Setting Depth (MD, ft)", 
                value=st.session_state.pump_setting_depth_md if st.session_state.pump_setting_depth_md is not None else None,
                placeholder="e.g., 5695",
                step=100
            )
            st.session_state.pump_setting_depth_md = pump_setting_depth_md
            
            pump_setting_depth_tvd = st.number_input(
                "Pump Setting Depth (TVD, ft)", 
                value=st.session_state.pump_setting_depth_tvd if st.session_state.pump_setting_depth_tvd is not None else None,
                placeholder="e.g., 5695",
                step=100
            )
            st.session_state.pump_setting_depth_tvd = pump_setting_depth_tvd
            
            tubing_id = st.number_input(
                "Tubing ID (inch)", 
                value=st.session_state.tubing_id if st.session_state.tubing_id is not None else None,
                placeholder="e.g., 3.958",
                step=0.001, 
                format="%.3f"
            )
            st.session_state.tubing_id = tubing_id
            
            st.markdown("#### 💧 Production Data")
            
            target_rate = st.number_input(
                "Desired Surface Gross Rate (STBD)", 
                value=st.session_state.target_rate if st.session_state.target_rate is not None else None,
                placeholder="e.g., 800",
                step=50
            )
            st.session_state.target_rate = target_rate
            
            water_cut = st.number_input(
                "Water Cut (fraction, e.g., 0.02 for 2%)", 
                value=st.session_state.water_cut if st.session_state.water_cut is not None else None,
                placeholder="e.g., 0.02",
                step=0.01, 
                format="%.3f"
            )
            st.session_state.water_cut = water_cut
            
        with col2:
            st.markdown("### 🌡️ Pressure & Temperature")
            
            p_wh = st.number_input(
                "Wellhead Pressure (psi)", 
                value=st.session_state.p_wh if st.session_state.p_wh is not None else None,
                placeholder="e.g., 700",
                step=10
            )
            st.session_state.p_wh = p_wh
            
            static_pressure = st.number_input(
                "Reservoir Static Pressure (psi)", 
                value=st.session_state.static_pressure if st.session_state.static_pressure is not None else None,
                placeholder="e.g., 3000",
                step=100
            )
            st.session_state.static_pressure = static_pressure
            
            bottom_hole_temp = st.number_input(
                "Bottom Hole Temperature (°F)", 
                value=st.session_state.bottom_hole_temp if st.session_state.bottom_hole_temp is not None else None,
                placeholder="e.g., 230",
                step=10
            )
            st.session_state.bottom_hole_temp = bottom_hole_temp
            
            st.markdown("### 🔬 Well Fluid Properties")
            
            water_sg = st.number_input(
                "Water Specific Gravity", 
                value=st.session_state.water_sg if st.session_state.water_sg is not None else None,
                placeholder="e.g., 1.01",
                step=0.01, 
                format="%.3f"
            )
            st.session_state.water_sg = water_sg
            
            oil_api = st.number_input(
                "Oil API Gravity", 
                value=st.session_state.oil_api if st.session_state.oil_api is not None else None,
                placeholder="e.g., 27.0",
                step=1.0, 
                format="%.1f"
            )
            st.session_state.oil_api = oil_api
            
            gas_sg = st.number_input(
                "Gas Specific Gravity", 
                value=st.session_state.gas_sg if st.session_state.gas_sg is not None else None,
                placeholder="e.g., 0.88",
                step=0.01, 
                format="%.3f"
            )
            st.session_state.gas_sg = gas_sg
            
            bubble_point_pressure = st.number_input(
                "Well Fluid Bubble Point Pressure (psi)", 
                value=st.session_state.bubble_point_pressure if st.session_state.bubble_point_pressure is not None else None,
                placeholder="e.g., 1661",
                step=10
            )
            st.session_state.bubble_point_pressure = bubble_point_pressure
            
            gas_compressibility = st.number_input(
                "Gas Compressibility Factor (Z)", 
                value=st.session_state.gas_compressibility if st.session_state.gas_compressibility is not None else None,
                placeholder="e.g., 0.85",
                step=0.01, 
                format="%.3f"
            )
            st.session_state.gas_compressibility = gas_compressibility
            
            gor = st.number_input(
                "GOR (SCF/STB)", 
                value=st.session_state.gor if st.session_state.gor is not None else None,
                placeholder="e.g., 450",
                step=10
            )
            st.session_state.gor = gor
            
            productivity_index = st.number_input(
                "Productivity Index (STBD/psi)", 
                value=st.session_state.productivity_index if st.session_state.productivity_index is not None else None,
                placeholder="e.g., 1.0",
                step=0.1, 
                format="%.1f"
            )
            st.session_state.productivity_index = productivity_index
    
    # ========== TAB 3: EQUIPMENT & ELECTRICAL ==========
    with tab3:
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("### ⚙️ ESP Equipment")
            
            pump_od = st.number_input(
                "Pump OD (inch)", 
                value=st.session_state.pump_od if st.session_state.pump_od is not None else None,
                placeholder="e.g., 5.0",
                step=0.1, 
                format="%.1f"
            )
            st.session_state.pump_od = pump_od
            
            num_rgs_od400 = st.number_input(
                "No. of RGS used in BHA (OD400 Series)", 
                value=st.session_state.num_rgs_od400 if st.session_state.num_rgs_od400 is not None else 0,
                step=1
            )
            st.session_state.num_rgs_od400 = num_rgs_od400
            
            num_rgs_od500 = st.number_input(
                "No. of RGS used in BHA (OD500 Series)", 
                value=st.session_state.num_rgs_od500 if st.session_state.num_rgs_od500 is not None else 0,
                step=1
            )
            st.session_state.num_rgs_od500 = num_rgs_od500
            
            num_agh_od400 = st.number_input(
                "No. of AGH used in BHA (OD400 Series)", 
                value=st.session_state.num_agh_od400 if st.session_state.num_agh_od400 is not None else 0,
                step=1
            )
            st.session_state.num_agh_od400 = num_agh_od400
            
            num_agh_od500 = st.number_input(
                "No. of AGH used in BHA (OD500 Series)", 
                value=st.session_state.num_agh_od500 if st.session_state.num_agh_od500 is not None else 0,
                step=1
            )
            st.session_state.num_agh_od500 = num_agh_od500
            
            st.markdown("#### 🔌 ESP Cable Data")
            
            cable_number = st.number_input(
                "Cable #", 
                value=st.session_state.cable_number if st.session_state.cable_number is not None else None,
                placeholder="1 or 2",
                step=1, 
                help="1 or 2 for resistance calculation"
            )
            st.session_state.cable_number = cable_number
            
        with col2:
            st.markdown("### ⚡ ESP Electrical Data")
            
            motor_hp_nameplate = st.number_input(
                "Motor Nameplate HP @ 50 Hz", 
                value=st.session_state.motor_hp_nameplate if st.session_state.motor_hp_nameplate is not None else None,
                placeholder="e.g., 300",
                step=10
            )
            st.session_state.motor_hp_nameplate = motor_hp_nameplate
            
            motor_voltage_nameplate = st.number_input(
                "Motor Nameplate Voltage @ 50 Hz", 
                value=st.session_state.motor_voltage_nameplate if st.session_state.motor_voltage_nameplate is not None else None,
                placeholder="e.g., 2125",
                step=10
            )
            st.session_state.motor_voltage_nameplate = motor_voltage_nameplate
            
            motor_ampere_nameplate = st.number_input(
                "Motor Nameplate Ampere", 
                value=st.session_state.motor_ampere_nameplate if st.session_state.motor_ampere_nameplate is not None else None,
                placeholder="e.g., 89",
                step=1
            )
            st.session_state.motor_ampere_nameplate = motor_ampere_nameplate
            
            motor_frequency = st.number_input(
                "Motor Frequency (Hz)", 
                value=st.session_state.motor_frequency if st.session_state.motor_frequency is not None else None,
                placeholder="e.g., 50",
                step=1
            )
            st.session_state.motor_frequency = motor_frequency
            
            transformer_voltage = st.number_input(
                "Transformer Upstream Voltage (Volts)", 
                value=st.session_state.transformer_voltage if st.session_state.transformer_voltage is not None else None,
                placeholder="e.g., 15000",
                step=100
            )
            st.session_state.transformer_voltage = transformer_voltage
            
            st.markdown("#### 📊 Efficiency Parameters")
            
            motor_power_factor = st.number_input(
                "Motor Power Factor (KW/KVA)", 
                value=st.session_state.motor_power_factor if st.session_state.motor_power_factor is not None else None,
                placeholder="e.g., 0.84",
                step=0.01, 
                format="%.3f"
            )
            st.session_state.motor_power_factor = motor_power_factor
            
            motor_efficiency = st.number_input(
                "Motor Efficiency", 
                value=st.session_state.motor_efficiency if st.session_state.motor_efficiency is not None else None,
                placeholder="e.g., 0.80",
                step=0.01, 
                format="%.3f"
            )
            st.session_state.motor_efficiency = motor_efficiency
            
            pump_efficiency = st.number_input(
                "Pump Efficiency", 
                value=st.session_state.pump_efficiency if st.session_state.pump_efficiency is not None else None,
                placeholder="e.g., 0.56",
                step=0.01, 
                format="%.3f"
            )
            st.session_state.pump_efficiency = pump_efficiency
    
    # ========== CALCULATION BUTTON ==========
    st.markdown("---")
    
    # Validate all required inputs before allowing calculation
    required_fields = [
        ('bep_flow', 'BEP Flow Rate'),
        ('rec_min', 'Recommended Min Flow'),
        ('rec_max', 'Recommended Max Flow'),
        ('bhp_per_stage', 'BHP per Stage'),
        ('perf_start_depth_md', 'Perforation Start Depth (MD)'),
        ('perf_start_depth_tvd', 'Perforation Start Depth (TVD)'),
        ('pump_setting_depth_tvd', 'Pump Setting Depth (TVD)'),
        ('pump_setting_depth_md', 'Pump Setting Depth (MD)'),
        ('tubing_id', 'Tubing ID'),
        ('target_rate', 'Target Rate'),
        ('water_cut', 'Water Cut'),
        ('p_wh', 'Wellhead Pressure'),
        ('static_pressure', 'Static Pressure'),
        ('bottom_hole_temp', 'Bottom Hole Temperature'),
        ('water_sg', 'Water Specific Gravity'),
        ('oil_api', 'Oil API Gravity'),
        ('gas_sg', 'Gas Specific Gravity'),
        ('bubble_point_pressure', 'Bubble Point Pressure'),
        ('gas_compressibility', 'Gas Compressibility'),
        ('gor', 'GOR'),
        ('productivity_index', 'Productivity Index'),
        ('pump_od', 'Pump OD'),
        ('cable_number', 'Cable Number'),
        ('motor_hp_nameplate', 'Motor HP'),
        ('motor_voltage_nameplate', 'Motor Voltage'),
        ('motor_ampere_nameplate', 'Motor Ampere'),
        ('motor_frequency', 'Motor Frequency'),
        ('transformer_voltage', 'Transformer Voltage'),
        ('motor_power_factor', 'Motor Power Factor'),
        ('motor_efficiency', 'Motor Efficiency'),
        ('pump_efficiency', 'Pump Efficiency'),
    ]
    
    missing_fields = [label for field, label in required_fields if st.session_state[field] is None]
    
    if missing_fields:
        st.warning(f"⚠️ Please fill in all required fields. Missing: {', '.join(missing_fields[:5])}{'...' if len(missing_fields) > 5 else ''}")
    
    if st.button("🚀 Calculate Complete ESP Design", width='stretch', type="primary", disabled=bool(missing_fields)):
        with st.spinner("Performing comprehensive calculations..."):
            try:
                # Create interpolation function
                pump_curve = interp1d(q_curve_data, h_curve_data, kind="cubic", fill_value="extrapolate")
                
                # Get values from session state
                target_rate = st.session_state.target_rate
                water_cut = st.session_state.water_cut
                oil_api = st.session_state.oil_api
                static_pressure = st.session_state.static_pressure
                productivity_index = st.session_state.productivity_index
                bubble_point_pressure = st.session_state.bubble_point_pressure
                gas_sg = st.session_state.gas_sg
                bottom_hole_temp = st.session_state.bottom_hole_temp
                perf_start_depth_tvd = st.session_state.perf_start_depth_tvd
                pump_setting_depth_tvd = st.session_state.pump_setting_depth_tvd
                pump_setting_depth_md = st.session_state.pump_setting_depth_md
                p_wh = st.session_state.p_wh
                water_sg = st.session_state.water_sg
                gor = st.session_state.gor
                gas_compressibility = st.session_state.gas_compressibility
                tubing_id = st.session_state.tubing_id
                motor_ampere_nameplate = st.session_state.motor_ampere_nameplate
                motor_hp_nameplate = st.session_state.motor_hp_nameplate
                motor_voltage_nameplate = st.session_state.motor_voltage_nameplate
                cable_number = st.session_state.cable_number
                transformer_voltage = st.session_state.transformer_voltage
                motor_power_factor = st.session_state.motor_power_factor
                motor_efficiency = st.session_state.motor_efficiency
                bhp_per_stage = st.session_state.bhp_per_stage
                pump_od = st.session_state.pump_od
                num_rgs_od400 = st.session_state.num_rgs_od400
                num_rgs_od500 = st.session_state.num_rgs_od500
                num_agh_od400 = st.session_state.num_agh_od400
                num_agh_od500 = st.session_state.num_agh_od500
                
                # ===== FLUID PROPERTIES CALCULATIONS =====
                # Oil specific gravity
                oil_sg = 141.5 / (131.5 + oil_api)
                
                # Flowing bottom hole pressure
                flowing_bhp = static_pressure - (target_rate / productivity_index)
                
                # Rs - Solution GOR (Standing correlation)
                rs = gas_sg * ((bubble_point_pressure / 18) * 
                              (10**(0.0125 * ((141.5/oil_sg) - 131.5)) / 
                               (10**(0.00091 * bottom_hole_temp))))**1.2048
                
                # Bo - Oil Formation Volume Factor (Standing correlation)
                bo = 0.972 + 0.000147 * (rs * (gas_sg/oil_sg)**0.5 + 1.25*bottom_hole_temp)**1.175
                
                # Bg - Gas Formation Volume Factor (calculated later at pump intake pressure)
                # Will be calculated after we know pump intake pressure
                
                # Bow - Oil-water mix formation volume factor
                bow = water_cut * 1/100 + (1 - water_cut/100) * bo
                
                # Total ESP downhole rate
                total_esp_downhole_rate = target_rate * bow
                
                # Fluid specific gravity (composite)
                fluid_sg = oil_sg * (1 - water_cut/100) + water_sg * water_cut/100
                
                # ===== PRODUCTION DATA =====
                # Surface oil rate
                surface_oil_rate = (1 - water_cut) * target_rate
                
                # Downhole oil rate
                downhole_oil_rate = surface_oil_rate * bo
                
                # Water production downhole
                water_prod_downhole = water_cut * target_rate
                
                # Total produced gas
                total_prod_gas = (1 - water_cut/100) * target_rate * gor / 1000
                
                # Gas in solution
                gas_in_solution = (1 - water_cut/100) * target_rate * rs / 1000
                
                # Free gas volume
                free_gas_volume = total_prod_gas - gas_in_solution
                
                # ===== HEAD CALCULATION (INITIAL) =====
                # Initial pump intake pressure (assuming no drawdown initially)
                initial_pip = static_pressure - ((perf_start_depth_tvd - pump_setting_depth_tvd) * 0.433)
                
                # Now calculate Bg at pump intake pressure
                # We'll use initial_pip for first iteration
                # Will be recalculated after we determine actual pump intake pressure
                
                # For now, use a placeholder for friction
                friction_factor = 45.0  # ft/1000ft - will be refined
                
                # Calculate required head
                h_lift = pump_setting_depth_tvd - (initial_pip / (0.433 * fluid_sg))
                h_surf = p_wh / (0.433 * fluid_sg)
                h_friction = friction_factor * (pump_setting_depth_md / 1000)
                TDH_initial = h_lift + h_surf + h_friction
                
                # Get head per stage at target rate
                head_per_stage = float(pump_curve(target_rate))
                
                # Calculate required stages
                n_stages_estimated = TDH_initial / head_per_stage
                n_stages = int(np.ceil(n_stages_estimated))
                
                # ===== ITERATIVE CALCULATION FOR PUMP INTAKE PRESSURE =====
                # Now we can calculate actual pump intake pressure
                # This is iterative but we'll do one iteration
                
                # Pump intake pressure (considering fluid column)
                pump_intake_pressure = flowing_bhp - ((perf_start_depth_tvd - pump_setting_depth_tvd) * fluid_sg * 0.433)
                
                # Bg at pump intake pressure
                bg = 28.27 * gas_compressibility * (bottom_hole_temp + 460) / pump_intake_pressure
                
                # Gas production downhole
                gas_prod_downhole = free_gas_volume * bg
                
                # Total fluid volume at pump intake
                total_fluid_volume = downhole_oil_rate + water_prod_downhole + gas_prod_downhole
                
                # Free gas percentage at pump intake
                free_gas_pct_intake = gas_prod_downhole * 100 / total_fluid_volume if total_fluid_volume > 0 else 0
                
                # Gas not separated (20% if RGS efficiency is 80%)
                gas_not_separated = gas_prod_downhole * 0.2
                
                # Total volume of fluid mixture ingested into pump
                total_fluid_to_pump = gas_not_separated + downhole_oil_rate + water_prod_downhole
                
                # Free gas percentage entering first stage
                free_gas_pct_first_stage = gas_not_separated / total_fluid_to_pump * 100 if total_fluid_to_pump > 0 else 0
                
                # Gas volume entering tubing
                gas_vol_tubing = gas_in_solution + (gas_not_separated / bg)
                
                # Tubing GOR
                tubing_gor = gas_vol_tubing * 1000 / surface_oil_rate if surface_oil_rate > 0 else 0
                
                # Total mass of produced fluid
                total_mass_prod = ((surface_oil_rate * oil_sg + water_prod_downhole * water_sg) * 62.4 * 5.615 + 
                                  tubing_gor * surface_oil_rate * gas_sg * 0.0752)
                
                # Inside tubing composite specific gravity
                tubing_composite_sg = total_mass_prod / (total_fluid_to_pump * 5.615 * 62.4) if total_fluid_to_pump > 0 else fluid_sg
                
                # ===== RECALCULATE TDH WITH ACCURATE PARAMETERS =====
                # Net dynamic lift
                net_dynamic_lift = pump_setting_depth_tvd - (pump_intake_pressure / (0.433 * fluid_sg))
                
                # Fluid level above pump intake
                fluid_level_above_pump = pump_intake_pressure / (0.433 * fluid_sg)
                
                # Total dynamic head
                TDH_design = net_dynamic_lift + (p_wh / (0.433 * tubing_composite_sg))
                
                # Estimated number of stages
                n_stages_estimated_final = TDH_design / head_per_stage
                n_stages = int(np.ceil(n_stages_estimated_final))
                
                # ===== HORSEPOWER CALCULATIONS =====
                # Required HP at first startup
                if pump_od == 4:
                    required_hp_startup = (n_stages * bhp_per_stage) + (4.5 * num_rgs_od400 / 1.2) + (30 * num_agh_od400) 
                else:
                    required_hp_startup = (n_stages * bhp_per_stage + num_rgs_od500 * 11/1.2 + num_agh_od500 * 30)
                
                # Pump brake horsepower (normal operation)
                pump_bhp_normal = bhp_per_stage * n_stages * tubing_composite_sg
                
                # Hydraulic horsepower
                hydraulic_hp = total_esp_downhole_rate * 0.02917 * TDH_design * fluid_sg / 3960
                
                # ===== ELECTRICAL CALCULATIONS =====
                # Pump-up time (no check valve)
                pumpup_time = ((tubing_id**2 / 1029.4) * (pump_setting_depth_md - (initial_pip / 0.433)) / 
                              (total_esp_downhole_rate / 1440)) if total_esp_downhole_rate > 0 else 0
                
                # Startup working ampere
                startup_ampere = motor_ampere_nameplate * required_hp_startup / motor_hp_nameplate if motor_hp_nameplate > 0 else 0
                
                # Normal working ampere
                normal_ampere = motor_ampere_nameplate * pump_bhp_normal / motor_hp_nameplate if motor_hp_nameplate > 0 else 0
                
                # Voltage drop
                if cable_number == 1:
                    voltage_drop = ((0.22077 * startup_ampere - 0.4661) * pump_setting_depth_md / 1000) * (((bottom_hole_temp - 60) * 0.002) + 1)
                else:
                    voltage_drop = ((0.27423 * normal_ampere - 0.49627) * pump_setting_depth_md / 1000) * (((bottom_hole_temp - 60) * 0.002) + 1)
                
                # Required surface voltage
                required_surface_voltage = voltage_drop + motor_voltage_nameplate
                
                # Total system KVA
                total_system_kva = required_surface_voltage * motor_ampere_nameplate * 1.73 / 1000
                
                # Sea cable ampere
                sea_cable_ampere = required_surface_voltage * normal_ampere / transformer_voltage if transformer_voltage > 0 else 0
                
                # True power (kW)
                true_power_kw = total_system_kva * motor_power_factor * motor_efficiency
                
                # Cable resistance at downhole temp
                if cable_number == 2:
                    cable_resistance = (pump_setting_depth_md * 0.169 / 1000) * (1 + 0.00214 * (bottom_hole_temp - 77))
                else:
                    cable_resistance = (pump_setting_depth_md * 0.134 / 1000) * (1 + 0.00214 * (bottom_hole_temp - 77))
                
                # Voltage drop across cable
                voltage_drop_cable = 1.732 * cable_resistance * normal_ampere
                
                # Voltage at motor terminals during startup
                vstart = motor_voltage_nameplate - 4 * startup_ampere * cable_resistance
                
                # Vstart / Vnameplate ratio
                vstart_ratio = vstart / motor_voltage_nameplate if motor_voltage_nameplate > 0 else 0
                
                # Store all results in session state
                st.session_state.design_calculated = True
                st.session_state.pump_curve = pump_curve
                st.session_state.q_curve_data = q_curve_data
                st.session_state.h_curve_data = h_curve_data
                st.session_state.TDH_design = TDH_design
                st.session_state.n_stages = n_stages
                st.session_state.head_per_stage = head_per_stage
                st.session_state.friction_factor = friction_factor
                
                # Store all calculated values
                st.session_state.calc = {
                    # Fluid properties
                    'oil_sg': oil_sg,
                    'flowing_bhp': flowing_bhp,
                    'rs': rs,
                    'bo': bo,
                    'bg': bg,
                    'bow': bow,
                    'fluid_sg': fluid_sg,
                    'tubing_composite_sg': tubing_composite_sg,
                    
                    # Production
                    'total_esp_downhole_rate': total_esp_downhole_rate,
                    'surface_oil_rate': surface_oil_rate,
                    'downhole_oil_rate': downhole_oil_rate,
                    'water_prod_downhole': water_prod_downhole,
                    'total_prod_gas': total_prod_gas,
                    'gas_in_solution': gas_in_solution,
                    'free_gas_volume': free_gas_volume,
                    'gas_prod_downhole': gas_prod_downhole,
                    'total_fluid_volume': total_fluid_volume,
                    'free_gas_pct_intake': free_gas_pct_intake,
                    'gas_not_separated': gas_not_separated,
                    'total_fluid_to_pump': total_fluid_to_pump,
                    'free_gas_pct_first_stage': free_gas_pct_first_stage,
                    'gas_vol_tubing': gas_vol_tubing,
                    'tubing_gor': tubing_gor,
                    'total_mass_prod': total_mass_prod,
                    
                    # Pressures and heads
                    'initial_pip': initial_pip,
                    'pump_intake_pressure': pump_intake_pressure,
                    'net_dynamic_lift': net_dynamic_lift,
                    'fluid_level_above_pump': fluid_level_above_pump,
                    'h_lift': net_dynamic_lift,
                    'h_surf': p_wh / (0.433 * tubing_composite_sg),
                    'h_friction': h_friction,
                    
                    # Power
                    'required_hp_startup': required_hp_startup,
                    'pump_bhp_normal': pump_bhp_normal,
                    'hydraulic_hp': hydraulic_hp,
                    
                    # Electrical
                    'pumpup_time': pumpup_time,
                    'startup_ampere': startup_ampere,
                    'normal_ampere': normal_ampere,
                    'voltage_drop': voltage_drop,
                    'required_surface_voltage': required_surface_voltage,
                    'total_system_kva': total_system_kva,
                    'sea_cable_ampere': sea_cable_ampere,
                    'true_power_kw': true_power_kw,
                    'cable_resistance': cable_resistance,
                    'voltage_drop_cable': voltage_drop_cable,
                    'vstart': vstart,
                    'vstart_ratio': vstart_ratio,
                }
                
                st.success("✅ Complete design calculation finished!")
                
            except Exception as e:
                st.error(f"❌ Calculation error: {str(e)}")
                import traceback
                st.code(traceback.format_exc())
    
    # ========== TAB 4: RESULTS & ANALYSIS ==========
    with tab4:
        if st.session_state.design_calculated:
            st.subheader("📊 Design Results")
            
            # Key Metrics
            col1, col2, col3, col4, col5 = st.columns(5)
            with col1:
                st.metric("Required Stages", f"{st.session_state.n_stages}")
            with col2:
                st.metric("Head/Stage", f"{st.session_state.head_per_stage:.2f} ft")
            with col3:
                st.metric("Total Head", f"{st.session_state.TDH_design:.0f} ft")
            with col4:
                st.metric("Pump BHP", f"{st.session_state.calc['pump_bhp_normal']:.1f} HP")
            with col5:
                st.metric("Hydraulic HP", f"{st.session_state.calc['hydraulic_hp']:.1f} HP")
            
            # Detailed Results in Expandable Sections
            st.markdown("---")
            
            # Well & Fluid Properties
            with st.expander("🔬 Well Fluid Properties & PVT", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Basic Properties:**")
                    st.write(f"• Oil Sp. Gr: {st.session_state.calc['oil_sg']:.4f}")
                    st.write(f"• Fluid Sp. Gr: {st.session_state.calc['fluid_sg']:.4f}")
                    st.write(f"• Tubing Composite Sp. Gr: {st.session_state.calc['tubing_composite_sg']:.4f}")
                with col2:
                    st.markdown("**PVT Properties(Based on Standing Correlation):**")
                    st.write(f"• Rs (SCF/STB): {st.session_state.calc['rs']:.2f}")
                    st.write(f"• Bo (bbl/STB): {st.session_state.calc['bo']:.4f}")
                    st.write(f"• Bg (bbl/mcf): {st.session_state.calc['bg']:.4f}")
                    st.write(f"• Bow (mix): {st.session_state.calc['bow']:.4f}")
                with col3:
                    st.markdown("**Pressures:**")
                    st.write(f"• Flowing BHP: {st.session_state.calc['flowing_bhp']:.1f} psi")
                    st.write(f"• Pump Intake: {st.session_state.calc['pump_intake_pressure']:.1f} psi")
                    st.write(f"• Initial PIP: {st.session_state.calc['initial_pip']:.1f} psi")
            
            # Production Data
            with st.expander("🛢️ Production Data", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Surface Rates:**")
                    st.write(f"• Oil: {st.session_state.calc['surface_oil_rate']:.1f} bpd")
                    st.write(f"• Water: {st.session_state.calc['water_prod_downhole']:.1f} bpd")
                    st.write(f"• Gas: {st.session_state.calc['total_prod_gas']:.3f} mcf/d")
                with col2:
                    st.markdown("**Downhole Rates:**")
                    st.write(f"• Oil: {st.session_state.calc['downhole_oil_rate']:.1f} bbl/d")
                    st.write(f"• Gas: {st.session_state.calc['gas_prod_downhole']:.1f} bbl/d")
                    st.write(f"• Total ESP: {st.session_state.calc['total_esp_downhole_rate']:.1f} bpd")
                with col3:
                    st.markdown("**Gas Analysis:**")
                    st.write(f"• Free Gas: {st.session_state.calc['free_gas_volume']:.3f} mcf/d")
                    st.write(f"• Gas in Solution: {st.session_state.calc['gas_in_solution']:.3f} mcf/d")
                    st.write(f"• Free Gas % @ Intake: {st.session_state.calc['free_gas_pct_intake']:.2f}%")
                    st.write(f"• Free Gas % 1st Stage: {st.session_state.calc['free_gas_pct_first_stage']:.2f}%")
                    st.write(f"• Tubing GOR: {st.session_state.calc['tubing_gor']:.1f} scf/stb")
            
            # Head Breakdown
            with st.expander("📐 Head Breakdown", expanded=True):
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown("**TDH Components:**")
                    st.write(f"• Net Dynamic Lift: {st.session_state.calc['net_dynamic_lift']:.0f} ft")
                    st.write(f"• Surface Pressure Head: {st.session_state.calc['h_surf']:.0f} ft")
                    st.write(f"• Friction Loss: {st.session_state.calc['h_friction']:.0f} ft")
                    st.write(f"• **Total Dynamic Head: {st.session_state.TDH_design:.0f} ft**")
                with col2:
                    st.markdown("**Fluid Levels:**")
                    st.write(f"• Fluid Level Above Pump: {st.session_state.calc['fluid_level_above_pump']:.0f} ft")
                    st.write(f"• Estimated Stages: {st.session_state.n_stages}")
                    st.write(f"• Head per Stage: {st.session_state.head_per_stage:.2f} ft")
            
            # Electrical Parameters
            with st.expander("⚡ Electrical Analysis", expanded=True):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.markdown("**Power Requirements:**")
                    st.write(f"• Startup HP: {st.session_state.calc['required_hp_startup']:.1f} HP")
                    st.write(f"• Normal BHP: {st.session_state.calc['pump_bhp_normal']:.1f} HP")
                    st.write(f"• Hydraulic HP: {st.session_state.calc['hydraulic_hp']:.1f} HP")
                with col2:
                    st.markdown("**Current & Voltage:**")
                    st.write(f"• Startup Ampere: {st.session_state.calc['startup_ampere']:.1f} A")
                    st.write(f"• Normal Ampere: {st.session_state.calc['normal_ampere']:.1f} A")
                    st.write(f"• Required Surface V: {st.session_state.calc['required_surface_voltage']:.0f} V")
                    st.write(f"• Voltage Drop: {st.session_state.calc['voltage_drop']:.1f} V")
                with col3:
                    st.markdown("**System Parameters:**")
                    st.write(f"• Total KVA: {st.session_state.calc['total_system_kva']:.2f} KVA")
                    st.write(f"• True Power: {st.session_state.calc['true_power_kw']:.2f} kW")
                    st.write(f"• Cable Resistance: {st.session_state.calc['cable_resistance']:.4f} Ω")
                    st.write(f"• Vstart/Vnameplate: {st.session_state.calc['vstart_ratio']:.3f}")
            
            # Performance Chart
            st.markdown("---")
            st.subheader("📈 ESP Performance Curve")
            
            # Use monotonic interpolation to prevent oscillations
            from scipy.interpolate import PchipInterpolator

            max_q = max(st.session_state.q_curve_data)
            q_range = np.linspace(0, max_q, 100)

            # Use PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) 
            # which preserves monotonicity and prevents oscillations
            pchip_curve = PchipInterpolator(st.session_state.q_curve_data, st.session_state.h_curve_data)
            h_single_stage = pchip_curve(q_range)

            # Clip negative heads to zero
            h_single_stage = np.maximum(h_single_stage, 0)
            h_full_pump = h_single_stage * st.session_state.n_stages
            
            # Create system curve
            def calculate_tdh(q):
                if q == 0:
                    return st.session_state.calc['h_lift'] + st.session_state.calc['h_surf']
                friction_at_q = st.session_state.friction_factor * (st.session_state.pump_setting_depth_md / 1000) * (q / st.session_state.target_rate) ** 1.85
                return st.session_state.calc['h_lift'] + st.session_state.calc['h_surf'] + friction_at_q
            
            system_tdh = [calculate_tdh(q) for q in q_range]
            bep_head = st.session_state.pump_curve(st.session_state.bep_flow) * st.session_state.n_stages
            
            # Create figure
            fig = go.Figure()
            
            # Recommended range
            fig.add_vrect(
                x0=st.session_state.rec_min, 
                x1=st.session_state.rec_max,
                fillcolor="rgba(0, 255, 136, 0.1)",
                layer="below",
                line_width=0,
                annotation_text="Recommended Range",
                annotation_position="top left",
                annotation=dict(font=dict(size=11, color="#00FF88"))
            )
            
            # Pump curve
            fig.add_trace(go.Scatter(
                x=q_range, y=h_full_pump,
                mode='lines',
                name=f'Pump Curve ({st.session_state.n_stages} stages)',
                line=dict(color='#00E5FF', width=3),
                hovertemplate='<b>Flow:</b> %{x:.0f} bpd<br><b>Head:</b> %{y:.0f} ft<extra></extra>'
            ))
            
            # System curve
            fig.add_trace(go.Scatter(
                x=q_range, y=system_tdh,
                mode='lines',
                name='System Curve',
                line=dict(color='#FF6B6B', width=2.5, dash='dash'),
                hovertemplate='<b>Flow:</b> %{x:.0f} bpd<br><b>Required Head:</b> %{y:.0f} ft<extra></extra>'
            ))
            
            # BEP
            fig.add_trace(go.Scatter(
                x=[st.session_state.bep_flow], y=[bep_head],
                mode='markers',
                name='BEP',
                marker=dict(size=14, color='#FFD700', line=dict(color='white', width=2)),
                hovertemplate='<b>BEP</b><br>Flow: %{x:.0f} bpd<br>Head: %{y:.0f} ft<extra></extra>'
            ))
            
            # Design point
            fig.add_trace(go.Scatter(
                x=[st.session_state.target_rate], y=[st.session_state.TDH_design],
                mode='markers',
                name='Design Point',
                marker=dict(size=16, color='#00FF88', symbol='square', line=dict(color='white', width=2)),
                hovertemplate='<b>Design Point</b><br>Flow: %{x:.0f} bpd<br>Head: %{y:.0f} ft<extra></extra>'
            ))
            
            fig.update_layout(
                title=dict(
                    text=f"ESP Performance - Well {st.session_state.well_name} | {st.session_state.pump_model}",
                    font=dict(size=18, color='#E6EDF3')
                ),
                xaxis_title="Flow Rate (bpd)",
                yaxis_title="Total Dynamic Head (ft)",
                hovermode='closest',
                template='plotly_dark',
                paper_bgcolor='#0D1117',
                plot_bgcolor='#161B22',
                font=dict(color='#E6EDF3', size=12),
                legend=dict(
                    yanchor="top", y=0.99,
                    xanchor="right", x=0.99,
                    bgcolor="rgba(22, 27, 34, 0.8)",
                    bordercolor="#30363D",
                    borderwidth=1,
                    font=dict(color='#E6EDF3', size=11)
                ),
                height=600,
                xaxis=dict(
                    title_font=dict(color='#E6EDF3', size=13),
                    tickfont=dict(color='#C9D1D9', size=11)
                ),
                yaxis=dict(
                    title_font=dict(color='#E6EDF3', size=13),
                    tickfont=dict(color='#C9D1D9', size=11)
                )
            )
            
            fig.update_xaxes(gridcolor='rgba(48, 54, 61, 0.3)', showline=True, linecolor='#30363D')
            fig.update_yaxes(gridcolor='rgba(48, 54, 61, 0.3)', showline=True, linecolor='#30363D')
            
            st.plotly_chart(fig, width='stretch')
            
        else:
            st.info("👈 Please fill in all data in the tabs above and click 'Calculate Complete ESP Design' to see results")

# ==================== PART 2: LIVE MONITORING ====================
elif page == "🔴 Part 2: Live Monitoring":
    st.header("🔴 Part 2: Live ESP Monitoring")
    
    if not st.session_state.design_calculated:
        st.warning("⚠️ Please complete Part 1 (Design & Sizing) first before using live monitoring.")
        st.stop()
    
    # Enhanced header with system info
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Well", st.session_state.well_name)
    with col2:
        st.metric("Pump Model", st.session_state.pump_model)
    with col3:
        st.metric("Installed Stages", st.session_state.n_stages)
    with col4:
        st.metric("Design Rate", f"{st.session_state.target_rate} bpd")
    
    st.markdown("---")
    
    # Live data input in professional layout
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📡 Live Sensor Data")
        
        with st.container():
            st.markdown('<div class="calculation-section">', unsafe_allow_html=True)
            st.markdown("#### Pump Pressures")
            pip = st.number_input(
                "Pump Intake Pressure (psi)", 
                value=st.session_state.pip_value,
                placeholder="e.g., 639.4", 
                step=10.0, 
                key="pip"
            )
            st.session_state.pip_value = pip
            
            pdp = st.number_input(
                "Pump Discharge Pressure (psi)", 
                value=st.session_state.pdp_value,
                placeholder="e.g., 2646.9", 
                step=10.0, 
                key="pdp"
            )
            st.session_state.pdp_value = pdp
            
            if pip is not None and pdp is not None:
                delta_p = pdp - pip
                st.metric("Pump Differential Pressure (ΔP)", f"{delta_p:.1f} psi", 
                         delta=f"{delta_p - 2000:.1f} psi from baseline" if 'baseline_dp' in st.session_state else None)
            st.markdown('</div>', unsafe_allow_html=True)
        
    with col2:
        st.markdown("### 📊 Operating Info")
        
        with st.container():
            st.markdown('<div class="calculation-section">', unsafe_allow_html=True)
            actual_stages = st.number_input(
                "Stages Currently Operating", 
                value=st.session_state.actual_stages_value if st.session_state.actual_stages_value is not None else (st.session_state.n_stages if st.session_state.design_calculated else None),
                placeholder=f"e.g., {st.session_state.n_stages if st.session_state.design_calculated else 'Enter stages'}",
                step=1, 
                key="stages_input"
            )
            st.session_state.actual_stages_value = actual_stages
            st.markdown('</div>', unsafe_allow_html=True)
            st.markdown("#### Fluid Properties")
            p_gradient = st.number_input(
                "Tubing Fluid Pressure Gradient (psi/ft)", 
                value=st.session_state.p_gradient_value,
                placeholder="e.g., 0.4051", 
                step=0.001, 
                format="%.4f", 
                key="pg"
            )
            st.session_state.p_gradient_value = p_gradient
            st.markdown('</div>', unsafe_allow_html=True)
    
    # Update button with enhanced styling
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        # Check if all required fields are filled
        can_update = all([pip is not None, pdp is not None, p_gradient is not None, actual_stages is not None])
        if not can_update:
            st.warning("⚠️ Please fill in all sensor data fields above")
        
        update_button = st.button("🔄 Update Live Data & Analyze Performance", 
                                  width='stretch', type="primary", disabled=not can_update)
    
    if update_button and can_update:
        with st.spinner("Processing sensor data and analyzing performance..."):
            # Calculate actual operating point
            delta_p = pdp - pip
            H_actual_stages = delta_p / p_gradient
            H_per_stage = H_actual_stages / actual_stages
            H_actual = H_per_stage
            
            # Get flow from head using inverse interpolation
            Q_from_H = interp1d(st.session_state.h_curve_data, st.session_state.q_curve_data, 
                               fill_value="extrapolate")
            Q_actual_sensor = float(Q_from_H(H_actual))
            H_total_sensor = H_actual * actual_stages
            
            # Store live data
            st.session_state.live_pip = pip
            st.session_state.live_pdp = pdp
            st.session_state.live_delta_p = delta_p
            st.session_state.live_Q = Q_actual_sensor
            st.session_state.live_H = H_total_sensor
            st.session_state.live_H_per_stage = H_actual
            st.session_state.live_stages = actual_stages
            st.session_state.live_updated = True
            st.session_state.timestamp = datetime.now()
            
            # Calculate deviations and status
            deviation_from_design = Q_actual_sensor - st.session_state.target_rate
            deviation_pct = (deviation_from_design / st.session_state.target_rate) * 100
            deviation_from_bep = Q_actual_sensor - st.session_state.bep_flow
            deviation_bep_pct = (deviation_from_bep / st.session_state.bep_flow) * 100
            
            st.session_state.live_deviation = deviation_from_design
            st.session_state.live_deviation_pct = deviation_pct
            st.session_state.live_deviation_bep_pct = deviation_bep_pct
            
            st.success("✅ Live data updated and analyzed!")
    
    # Display live results with enhanced dashboard
    if st.session_state.get('live_updated', False):
        st.markdown("---")
        
        # Status indicator
        in_range = (st.session_state.rec_min <= st.session_state.live_Q <= st.session_state.rec_max)
        status = "OPTIMAL OPERATION" if in_range else "OUT OF RANGE"
        status_color = "#00FF88" if in_range else "#FF1744"
        status_icon = "✅" if in_range else "⚠️"
        
        st.markdown(f"""
        <div style='background-color: #161B22; padding: 20px; border-radius: 10px; border-left: 5px solid {status_color}; margin-bottom: 20px;'>
            <h2 style='color: {status_color}; margin: 0;'>{status_icon} System Status: {status}</h2>
            <p style='color: #8B949E; margin: 5px 0 0 0;'>Last Update: {st.session_state.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Live metrics dashboard
        st.subheader("🎯 Current Operating Point")
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Flow Rate", f"{st.session_state.live_Q:.0f} bpd",
                     delta=f"{st.session_state.live_deviation:+.0f} bpd")
        with col2:
            st.metric("Total Head", f"{st.session_state.live_H:.0f} ft")
        with col3:
            st.metric("Head/Stage", f"{st.session_state.live_H_per_stage:.2f} ft")
        with col4:
            st.metric("vs Design", f"{st.session_state.live_deviation_pct:+.1f}%",
                     delta=f"{st.session_state.live_deviation:+.0f} bpd")
        with col5:
            st.metric("vs BEP", f"{st.session_state.live_deviation_bep_pct:+.1f}%")
        
        # Detailed sensor readings
        st.markdown("---")
        with st.expander("📋 Detailed Sensor Readings & Analysis", expanded=True):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.markdown("**Pressure Data:**")
                st.write(f"• Pump Intake: {st.session_state.live_pip:.1f} psi")
                st.write(f"• Pump Discharge: {st.session_state.live_pdp:.1f} psi")
                st.write(f"• Differential: {st.session_state.live_delta_p:.1f} psi")
                st.write(f"• Pressure Gradient: {p_gradient:.4f} psi/ft")
            
            with col2:
                st.markdown("**Performance:**")
                st.write(f"• Live Flow: {st.session_state.live_Q:.0f} bpd")
                st.write(f"• Total Head: {st.session_state.live_H:.0f} ft")
                st.write(f"• Head per Stage: {st.session_state.live_H_per_stage:.2f} ft")
                st.write(f"• Operating Stages: {st.session_state.live_stages}")
            
            with col3:
                st.markdown("**Design Comparison:**")
                st.write(f"• Design Flow: {st.session_state.target_rate} bpd")
                st.write(f"• Design Head: {st.session_state.TDH_design:.0f} ft")
                st.write(f"• BEP Flow: {st.session_state.bep_flow:.0f} bpd")
                st.write(f"• Recommended Range: {st.session_state.rec_min:.0f}-{st.session_state.rec_max:.0f} bpd")
        
        # Performance insights
        st.markdown("---")
        st.subheader("💡 Performance Insights & Recommendations")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown('<div class="calculation-section">', unsafe_allow_html=True)
            st.markdown("#### Operating Range Analysis")
            if in_range:
                st.success(f"✅ Operating within recommended flow range ({st.session_state.rec_min:.0f} - {st.session_state.rec_max:.0f} bpd)")
            else:
                if st.session_state.live_Q < st.session_state.rec_min:
                    shortage = st.session_state.rec_min - st.session_state.live_Q
                    st.error(f"⚠️ Flow too low by {shortage:.0f} bpd (minimum: {st.session_state.rec_min:.0f} bpd)")
                    st.warning("**Recommendations:**\n- Check for pump wear\n- Verify reservoir pressure\n- Inspect for blockages")
                else:
                    excess = st.session_state.live_Q - st.session_state.rec_max
                    st.error(f"⚠️ Flow too high by {excess:.0f} bpd (maximum: {st.session_state.rec_max:.0f} bpd)")
                    st.warning("**Recommendations:**\n- Reduce pump speed if VSD equipped\n- Check for gas slugging\n- Verify stage count")
            st.markdown('</div>', unsafe_allow_html=True)
        
        with col2:
            st.markdown('<div class="calculation-section">', unsafe_allow_html=True)
            st.markdown("#### BEP Deviation Analysis")
            abs_bep_dev = abs(st.session_state.live_deviation_bep_pct)
            if abs_bep_dev <= 10:
                st.success(f"✅ Excellent! Operating near BEP ({st.session_state.live_deviation_bep_pct:+.1f}% deviation)")
                st.info("System is operating at optimal efficiency")
            elif abs_bep_dev <= 20:
                st.warning(f"⚠️ Moderate deviation from BEP ({st.session_state.live_deviation_bep_pct:+.1f}%)")
                st.info("Efficiency is acceptable but could be improved")
            else:
                st.error(f"❌ Significant deviation from BEP ({st.session_state.live_deviation_bep_pct:+.1f}%)")
                st.warning("**Recommendations:**\n- Review operating parameters\n- Consider pump resizing\n- Check for component wear")
            st.markdown('</div>', unsafe_allow_html=True)
        
        # Live performance chart
        st.markdown("---")
        st.subheader("📈 Live Performance Visualization")
        
        # Use monotonic interpolation to prevent oscillations
        from scipy.interpolate import PchipInterpolator

        max_q = max(st.session_state.q_curve_data)
        q_range = np.linspace(0, max_q, 100)

        # Use PCHIP (Piecewise Cubic Hermite Interpolating Polynomial) 
        # which preserves monotonicity and prevents oscillations
        pchip_curve = PchipInterpolator(st.session_state.q_curve_data, st.session_state.h_curve_data)
        h_single_stage = pchip_curve(q_range)

        # Clip negative heads to zero
        h_single_stage = np.maximum(h_single_stage, 0)
        h_full_pump = h_single_stage * st.session_state.n_stages
        
        bep_head = st.session_state.pump_curve(st.session_state.bep_flow) * st.session_state.live_stages
        
        # Create figure
        fig = go.Figure()
        
        # Recommended range shading
        fig.add_vrect(
            x0=st.session_state.rec_min, 
            x1=st.session_state.rec_max,
            fillcolor="rgba(0, 255, 136, 0.15)",
            layer="below",
            line_width=0,
            annotation_text="Recommended Operating Range",
            annotation_position="top left",
            annotation=dict(font=dict(size=12, color="#00FF88"))
        )
        
        # Pump curve
        fig.add_trace(go.Scatter(
            x=q_range, y=h_full_pump,
            mode='lines',
            name=f'Pump Curve ({st.session_state.live_stages} stages)',
            line=dict(color='#00E5FF', width=3.5),
            hovertemplate='<b>Flow:</b> %{x:.0f} bpd<br><b>Head:</b> %{y:.0f} ft<extra></extra>'
        ))
        
        # BEP
        fig.add_trace(go.Scatter(
            x=[st.session_state.bep_flow], y=[bep_head],
            mode='markers+text',
            name='BEP',
            marker=dict(size=16, color='#FFD700', line=dict(color='white', width=2.5)),
            text=['BEP'],
            textposition='top center',
            textfont=dict(size=11, color='#FFD700'),
            hovertemplate='<b>BEP</b><br>%{x:.0f} bpd, %{y:.0f} ft<extra></extra>'
        ))
        
        # Design point
        fig.add_trace(go.Scatter(
            x=[st.session_state.target_rate], y=[st.session_state.TDH_design],
            mode='markers+text',
            name='Design Point',
            marker=dict(size=16, color='#00FF88', symbol='square', line=dict(color='white', width=2.5)),
            text=['Design'],
            textposition='bottom center',
            textfont=dict(size=11, color='#00FF88'),
            hovertemplate='<b>Design Point</b><br>%{x:.0f} bpd, %{y:.0f} ft<extra></extra>'
        ))
        
        # LIVE operating point - HIGHLIGHTED
        fig.add_trace(go.Scatter(
            x=[st.session_state.live_Q], y=[st.session_state.live_H],
            mode='markers+text',
            name='LIVE Operating Point',
            marker=dict(size=22, color='#FF1744', symbol='diamond', 
                       line=dict(color='white', width=3)),
            text=['LIVE'],
            textposition='top center',
            textfont=dict(size=13, color='#FF1744', family='Arial Black'),
            hovertemplate='<b>🔴 LIVE OPERATING POINT</b><br>Flow: %{x:.0f} bpd<br>Head: %{y:.0f} ft<extra></extra>'
        ))
        
        # Enhanced layout
        fig.update_layout(
            title=dict(
                text=f"<b>Live ESP Monitoring - Well {st.session_state.well_name}</b><br><sub>Last Update: {st.session_state.timestamp.strftime('%Y-%m-%d %H:%M:%S')}</sub>",
                font=dict(size=20, color='#E6EDF3'),
                x=0.5,
                xanchor='center'
            ),
            xaxis_title="Flow Rate (bpd)",
            yaxis_title="Total Dynamic Head (ft)",
            hovermode='closest',
            template='plotly_dark',
            paper_bgcolor='#0D1117',
            plot_bgcolor='#161B22',
            font=dict(color='#E6EDF3', size=13),
            legend=dict(
                yanchor="top", y=0.99,
                xanchor="right", x=0.99,
                bgcolor="rgba(22, 27, 34, 0.95)",
                bordercolor="#30363D",
                borderwidth=2,
                font=dict(color='#E6EDF3', size=12)
            ),
            height=700,
            xaxis=dict(
                title_font=dict(color='#E6EDF3', size=14),
                tickfont=dict(color='#C9D1D9', size=12),
                gridcolor='rgba(48, 54, 61, 0.4)',
                showline=True,
                linecolor='#30363D',
                linewidth=2
            ),
            yaxis=dict(
                title_font=dict(color='#E6EDF3', size=14),
                tickfont=dict(color='#C9D1D9', size=12),
                gridcolor='rgba(48, 54, 61, 0.4)',
                showline=True,
                linecolor='#30363D',
                linewidth=2
            )
        )
        
        st.plotly_chart(fig, width='stretch')
        
        # Additional metrics in cards
        st.markdown("---")
        st.subheader("📊 Additional Performance Metrics")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            efficiency = min(100, (st.session_state.live_Q / st.session_state.bep_flow) * 100) if st.session_state.live_Q < st.session_state.bep_flow else min(100, (st.session_state.bep_flow / st.session_state.live_Q) * 100)
            st.metric("Relative Efficiency", f"{efficiency:.1f}%")
        
        with col2:
            utilization = (st.session_state.live_Q / st.session_state.target_rate) * 100
            st.metric("Capacity Utilization", f"{utilization:.1f}%")
        
        with col3:
            head_margin = ((st.session_state.live_H - st.session_state.TDH_design) / st.session_state.TDH_design) * 100
            st.metric("Head Margin", f"{head_margin:+.1f}%")
        
        with col4:
            operating_hours = 24  # Placeholder - could be tracked
            st.metric("Hours Since Update", f"{(datetime.now() - st.session_state.timestamp).seconds / 60:.0f} min")

# Footer
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        "<p style='text-align: center; color: #7D8590;'>ESP Dashboard v2.0 | Enhanced with ESP Running Sheet Calculations | Built with Streamlit & Plotly</p>",
        unsafe_allow_html=True
    )
