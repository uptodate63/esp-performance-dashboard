# ⚡ ESP Performance Dashboard v 1.0

<div align="center">

**Real-time Electric Submersible Pump Monitoring & Analysis System**

</div>

---
## 🎯 Overview

The **ESP Performance Dashboard v2.0** is a comprehensive web-based application designed for petroleum engineers and ESP (Electric Submersible Pump) specialists to design, monitor, and optimize ESP systems in oil and gas production wells. 

This professional-grade tool combines advanced engineering calculations with real-time monitoring capabilities, providing a complete solution for ESP system analysis from initial design through operational monitoring.

### Why This Dashboard?

- **Complete ESP Design**: Implements full ESP running sheet calculations including PVT properties, production forecasting, and electrical analysis
- **Real-time Monitoring**: Live sensor data integration for continuous performance tracking
- **Custom Pump Curves**: Upload and use any pump model with Excel-based curve data
- **Professional Analysis**: Automated performance insights and operational recommendations
- **Modern Interface**: Dark-themed, responsive UI built with Streamlit and Plotly

---

## ✨ Features

### 🔧 Part 1: Design & Sizing

#### **Pump Selection & Configuration**
- ✅ Default pump curve library (ESP-3000)
- ✅ Custom pump curve upload via Excel
- ✅ User-defined BEP (Best Efficiency Point)
- ✅ Customizable operating range (min/max flow)
- ✅ Pump performance visualization

#### **Well & Fluid Data Management**
- ✅ Complete well geometry input (MD, TVD, depths)
- ✅ Comprehensive fluid properties (oil API, water cut, GOR)
- ✅ PVT calculations based on Standing Correlation (Rs, Bo, Bg, Bow)
- ✅ Pressure and temperature parameters
- ✅ Productivity index integration

#### **Equipment & Electrical Configuration**
- ✅ ESP equipment specifications (pump OD, RGS, AGH)
- ✅ Motor nameplate data
- ✅ Cable specifications and calculations
- ✅ Transformer and power factor settings
- ✅ Efficiency parameters (pump, motor)

#### **Comprehensive Calculations**
- ✅ **Fluid Properties**: Oil/water/gas specific gravities, formation volume factors
- ✅ **Production Forecasting**: Surface and downhole rates for oil, water, and gas
- ✅ **Pressure Analysis**: Flowing BHP, pump intake pressure, fluid levels
- ✅ **Head Calculations**: Net lift, surface pressure head, friction losses, TDH
- ✅ **Stage Determination**: Automated stage count calculation
- ✅ **Horsepower Requirements**: Startup HP, brake HP, hydraulic HP
- ✅ **Electrical Analysis**: Amperage, voltage drops, KVA, power consumption
- ✅ **Gas Handling**: Free gas percentages, gas separation efficiency
- ✅ **Performance Curves**: Interactive pump curve vs system curve plotting

### 🔴 Part 2: Live Monitoring

#### **Real-time Data Acquisition**
- ✅ Pump intake pressure (PIP) monitoring
- ✅ Pump discharge pressure (PDP) monitoring
- ✅ Differential pressure calculation
- ✅ Pressure gradient tracking
- ✅ Wellhead pressure updates
- ✅ Fluid level monitoring

#### **Performance Analysis**
- ✅ Real-time flow rate calculation from sensor data
- ✅ Operating point determination on pump curve
- ✅ Deviation analysis (vs. design and BEP)
- ✅ Operating range compliance checking
- ✅ Efficiency calculations
- ✅ Capacity utilization metrics

#### **Intelligent Insights**
- ✅ Automated status determination (Optimal/Warning)
- ✅ Performance recommendations
- ✅ Operating range alerts
- ✅ BEP deviation analysis
- ✅ Historical timestamp tracking
- ✅ Color-coded status indicators

#### **Advanced Visualization**
- ✅ Live operating point on performance curve
- ✅ Multiple reference points (BEP, Design, Current)
- ✅ Recommended range highlighting
- ✅ Interactive hover information
- ✅ Real-time chart updates
- ✅ Professional dark theme

---

## 🛠 Technology Stack

### Core Technologies
- **Python 3.8+**: Programming language
- **Streamlit 1.28+**: Web framework for interactive dashboards
- **Plotly 5.0+**: Interactive data visualization
- **NumPy**: Numerical computations
- **Pandas**: Data manipulation and Excel processing
- **SciPy**: Scientific computing and interpolation

### Key Libraries
```python
streamlit>=1.28.0
plotly>=5.0.0
numpy>=1.24.0
pandas>=2.0.0
scipy>=1.10.0
openpyxl>=3.1.0  # For Excel file handling
```

### Design & UI
- Custom CSS for modern dark theme
- Responsive layout design
- GitHub-inspired color scheme
- Professional metric cards
- Status indicators and alerts

---

## 🚀 Quick Start

### Running the Dashboard

1. **Navigate to project directory:**
   ```bash
   cd esp-performance-dashboard
   ```

2. **Activate virtual environment** (if created):
   ```bash
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Launch the dashboard:**
   ```bash
   streamlit run esp_dashboard.py
   ```

4. **Access the dashboard:**
   - The browser should open automatically
   - If not, navigate to: `http://localhost:8501`

### First Run Example

1. **Part 1 - Design Mode:**
   - Use default pump curve 
   - Enter well name: "Well name"
   - Set target flow rate: STBD
   - Configure well depths and pressures
   - Click "Calculate Complete ESP Design"

2. **Part 2 - Live Monitoring:**
   - Enter PIP
   - Enter PDP
   - Enter Fluid Pressure Gradient
   - Click "Update Live Data & Analyze Performance"
   - Review real-time performance insights

---

## 📚 Detailed Usage Guide

### Part 1: Design & Sizing

#### Tab 1: Pump Selection

**Option A: Use Default Pump**
1. Select "Use Default Pump (ESP-3000)"
2. System loads 51 data points automatically
3. View confirmation message

**Option B: Upload Custom Pump**
1. Select "Upload Custom Pump Curve"
2. Prepare Excel file with format:
   ```
   Column A: Flow Rate (bpd)
   Column B: Head per Stage (ft)
   No headers required
   ```
3. Click "Browse files" and select your Excel file
4. System validates and displays preview
5. Enter performance parameters:
   - **BEP Flow Rate**: Optimal operating flow (e.g., 2502.2 bpd)
   - **Recommended Min**: Minimum safe flow (e.g., 2001.76 bpd)
   - **Recommended Max**: Maximum safe flow (e.g., 3009.60 bpd)
   - **BHP per Stage**: Brake horsepower per stage (e.g., 0.936)

#### Tab 2: Well & Fluid Data

**Well Geometry:**
- **Well Name**: Identifier for the well (e.g., "WELL-A1")
- **Perforation Start Depth (MD)**: Measured depth to perforations (ft)
- **Perforation Start Depth (TVD)**: True vertical depth to perforations (ft)
- **Pump Setting Depth (MD)**: Measured depth to pump (ft)
- **Pump Setting Depth (TVD)**: True vertical pump depth (ft)
- **Tubing ID**: Internal diameter of production tubing (inches)

**Production Data:**
- **Desired Surface Gross Rate**: Target production rate (STBD)
- **Water Cut**: Fraction of water in production (0.02 = 2%)

**Pressure & Temperature:**
- **Wellhead Pressure**: Surface pressure at wellhead (psi)
- **Static Pressure**: Reservoir static pressure (psi)
- **Bottom Hole Temperature**: Formation temperature (°F)

**Fluid Properties:**
- **Water Specific Gravity**: Typically 1.0-1.1
- **Oil API Gravity**: American Petroleum Institute gravity (degrees)
- **Gas Specific Gravity**: Relative to air (typically 0.6-0.9)
- **Bubble Point Pressure**: Pressure at which gas comes out of solution (psi)
- **Gas Compressibility Factor (Z)**: Typically 0.8-0.95
- **GOR**: Gas-Oil Ratio (SCF/STB)
- **Productivity Index**: Well deliverability (bpd/psi)

#### Tab 3: Equipment & Electrical

**ESP Equipment:**
- **Pump OD**: Outer diameter in inches (4, 5, etc.)
- **RGS (Rotary Gas Separator)**: Number of units for gas handling
- **AGH (Advanced Gas Handler)**: Number of units
- **Cable Number**: Type 1 or 2 for resistance calculations

**Electrical Data:**
- **Motor HP Nameplate**: Motor horsepower rating @ rated frequency
- **Motor Voltage Nameplate**: Rated voltage (typically 1000-4000V)
- **Motor Ampere Nameplate**: Rated current (A)
- **Motor Frequency**: Operating frequency (Hz, typically 50 or 60)
- **Transformer Voltage**: Upstream transformer voltage (V)

**Efficiency Parameters:**
- **Motor Power Factor**: KW/KVA ratio (typically 0.8-0.9)
- **Motor Efficiency**: Decimal form (0.80 = 80%)
- **Pump Efficiency**: Decimal form (0.50-0.70 typical)

#### Tab 4: Results & Analysis

After clicking "Calculate Complete ESP Design", this tab displays:

1. **Key Metrics Dashboard**
   - Required number of stages
   - Head per stage
   - Total dynamic head
   - Power requirements

2. **Well Fluid Properties & PVT** (Expandable)
   - Calculated specific gravities
   - Formation volume factors (Rs, Bo, Bg, Bow)
   - Pressure analysis (flowing BHP, pump intake)

3. **Production Data** (Expandable)
   - Surface and downhole oil rates
   - Water and gas production
   - Free gas calculations
   - Tubing GOR

4. **Head Breakdown** (Expandable)
   - Net dynamic lift
   - Surface pressure head
   - Friction losses
   - Fluid level calculations

5. **Electrical Analysis** (Expandable)
   - Startup and normal amperage
   - Voltage drops and requirements
   - System KVA and true power
   - Cable resistance calculations

6. **Performance Curve** (Interactive Plot)
   - Pump curve for calculated stages
   - System curve
   - Best Efficiency Point (BEP)
   - Design operating point
   - Recommended operating range (shaded)

### Part 2: Live Monitoring

#### Setting Up Monitoring

1. **Complete Part 1 first** - Design must be calculated before monitoring
2. **Verify system info** displayed at top:
   - Well name
   - Pump model
   - Installed stages
   - Design rate

#### Entering Live Data

**Left Panel - Live Sensor Data:**
1. **Pump Intake Pressure (PIP)**: Current downhole intake pressure (psi)
2. **Pump Discharge Pressure (PDP)**: Current discharge pressure (psi)
3. **Differential Pressure**: Automatically calculated (ΔP = PDP - PIP)
4. **Pressure Gradient**: psi/ft, typically 0.4-0.5 for oil wells

**Right Panel - Current Wellhead Data:**
1. **Current Wellhead Pressure**: Real-time surface pressure (psi)
2. **Current Fluid Level**: Measured or calculated fluid level (ft)
3. **Stages Currently Operating**: May differ from design if stages failed

#### Analyzing Results

After clicking "Update Live Data & Analyze Performance":

1. **System Status Banner**
   - ✅ Green "OPTIMAL OPERATION" = Within recommended range
   - ⚠️ Red "OUT OF RANGE" = Outside safe operating limits
   - Timestamp of last update

2. **Current Operating Point Metrics**
   - **Flow Rate**: Calculated from differential pressure
   - **Total Head**: Current head being generated
   - **Head/Stage**: Per-stage performance
   - **vs Design**: Deviation from design point
   - **vs BEP**: Deviation from best efficiency point

3. **Performance Insights**
   - **Operating Range Analysis**: 
     - In-range confirmation
     - Out-of-range warnings with recommendations
   - **BEP Deviation Analysis**:
     - Excellent (<10% deviation)
     - Acceptable (10-20% deviation)
     - Poor (>20% deviation)
     - Specific recommendations for each case

4. **Live Performance Visualization**
   - All design curves with live operating point highlighted
   - Large red diamond marker shows current operation
   - Interactive hover for detailed information

5. **Additional Performance Metrics**
   - **Relative Efficiency**: Based on proximity to BEP
   - **Capacity Utilization**: Percentage of design rate
   - **Head Margin**: Excess or deficit vs. design
   - **Hours Since Update**: Time tracking

---

## 📁 Project Structure

```
esp-performance-dashboard/
├── esp_dashboard.py         
├── requirements.txt             
├── README.md                      
```

---

## 📞 Contact

### Author
- **GitHub**: [@uptodate63](https://github.com/uptodate63)
- **Email**: [uptodate63@gmail.com](mailto:uptodate63@gmail.com)
- **LinkedIn**: [Fazlollah Koohi](https://www.linkedin.com/in/fazlollah-koohi)

---

<div align="center">

**⚡ Made with passion for petroleum engineers ⚡**

If you find this project useful, please consider giving it a ⭐!

[⬆ Back to Top](#-esp-performance-dashboard-v20)

</div>
