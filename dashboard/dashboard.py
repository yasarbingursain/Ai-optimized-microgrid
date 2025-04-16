import streamlit as st
import requests
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import time
import json

# Configuration
API_URL = "http://localhost:8000"
REFRESH_INTERVAL = 300  # 5 minutes

st.set_page_config(
    page_title="Microgrid Energy Dashboard",
    page_icon="⚡",
    layout="wide"
)

# Session state for authentication
if 'token' not in st.session_state:
    st.session_state.token = None
if 'username' not in st.session_state:
    st.session_state.username = None

def login():
    """Login form"""
    with st.form("login_form"):
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        submitted = st.form_submit_button("Login")
        
        if submitted:
            try:
                response = requests.post(
                    f"{API_URL}/token",
                    data={"username": username, "password": password}
                )
                if response.status_code == 200:
                    st.session_state.token = response.json()["access_token"]
                    st.session_state.username = username
                    st.success("Logged in successfully!")
                    st.experimental_rerun()
                else:
                    st.error("Invalid credentials")
            except Exception as e:
                st.error(f"Error logging in: {str(e)}")

def logout():
    """Logout function"""
    st.session_state.token = None
    st.session_state.username = None
    st.experimental_rerun()

def fetch_forecast():
    """Fetch energy demand forecast from API"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/forecast", headers=headers)
        if response.status_code == 200:
            return response.json()["forecast"]
    except Exception as e:
        st.error(f"Error fetching forecast: {str(e)}")
    return None

def fetch_metrics():
    """Fetch current energy metrics from API"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/metrics", headers=headers)
        if response.status_code == 200:
            return response.json()["metrics"]
    except Exception as e:
        st.error(f"Error fetching metrics: {str(e)}")
    return None

def fetch_systems():
    """Fetch system status from API"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/systems", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching systems: {str(e)}")
    return None

def fetch_power_quality(system_id):
    """Fetch power quality metrics"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/power-quality/{system_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching power quality: {str(e)}")
    return None

def fetch_grid_stability(system_id):
    """Fetch grid stability metrics"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/grid-stability/{system_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching grid stability: {str(e)}")
    return None

def fetch_load_balancing(system_id):
    """Fetch load balancing metrics"""
    try:
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.get(f"{API_URL}/load-balancing/{system_id}", headers=headers)
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(f"Error fetching load balancing: {str(e)}")
    return None

def main():
    st.title("⚡ Microgrid Energy Dashboard")
    
    # Authentication
    if not st.session_state.token:
        login()
        return
    
    # Logout button
    st.sidebar.title(f"Welcome, {st.session_state.username}")
    if st.sidebar.button("Logout"):
        logout()
    
    # Create three columns for metrics
    col1, col2, col3 = st.columns(3)
    
    # Fetch and display current metrics
    metrics = fetch_metrics()
    if metrics:
        with col1:
            st.metric("Solar Generation", f"{metrics.get('solar_power', 0):.1f} kW")
        with col2:
            st.metric("Wind Generation", f"{metrics.get('wind_power', 0):.1f} kW")
        with col3:
            st.metric("Battery Level", f"{metrics.get('battery_level', 0):.1f}%")
    
    # Create tabs for different visualizations
    tab1, tab2, tab3 = st.tabs(["Forecast", "System Status", "Advanced Metrics"])
    
    with tab1:
        st.subheader("24-Hour Energy Demand Forecast")
        forecast = fetch_forecast()
        if forecast:
            df = pd.DataFrame(forecast)
            df['datetime'] = pd.to_datetime(df['datetime'])
            
            # Create figure with secondary y-axis
            fig = go.Figure()
            
            # Add energy demand trace
            fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=df['predicted_demand'],
                    name="Energy Demand",
                    line=dict(color="blue")
                )
            )
            
            # Add weather data
            weather = df.iloc[0]['weather']
            fig.add_trace(
                go.Scatter(
                    x=df['datetime'],
                    y=[weather['temperature']] * len(df),
                    name="Temperature (°C)",
                    line=dict(color="red"),
                    yaxis="y2"
                )
            )
            
            # Update layout
            fig.update_layout(
                title="Energy Demand Forecast with Temperature",
                xaxis_title="Time",
                yaxis_title="Energy Demand (kW)",
                yaxis2=dict(
                    title="Temperature (°C)",
                    overlaying="y",
                    side="right"
                )
            )
            
            st.plotly_chart(fig, use_container_width=True)
    
    with tab2:
        st.subheader("System Status")
        systems = fetch_systems()
        if systems:
            for system in systems:
                status_color = "green" if system["status"] == "online" else "red"
                st.markdown(f"""
                **Location:** {system["location"]}  
                **Status:** <span style="color:{status_color}">{system["status"]}</span>  
                **Last Update:** {system["last_update"]}  
                **Solar Capacity:** {system["solar_capacity"]} kW  
                **Wind Capacity:** {system["wind_capacity"]} kW  
                **Battery Capacity:** {system["battery_capacity"]} kWh
                """, unsafe_allow_html=True)
                
                # Power Quality
                power_quality = fetch_power_quality(system["id"])
                if power_quality:
                    st.subheader("Power Quality")
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Voltage", f"{power_quality['voltage']:.1f} V")
                    with col2:
                        st.metric("Frequency", f"{power_quality['frequency']:.1f} Hz")
                    with col3:
                        st.metric("Harmonic Distortion", f"{power_quality['harmonic_distortion']:.1f}%")
                    with col4:
                        st.metric("Power Factor", f"{power_quality['power_factor']:.2f}")
                
                st.divider()
    
    with tab3:
        st.subheader("Advanced Metrics")
        if systems:
            for system in systems:
                st.subheader(f"System: {system['location']}")
                
                # Grid Stability
                grid_stability = fetch_grid_stability(system["id"])
                if grid_stability:
                    st.subheader("Grid Stability")
                    fig = go.Figure()
                    fig.add_trace(go.Indicator(
                        mode="gauge+number",
                        value=grid_stability['voltage_stability'],
                        title={'text': "Voltage Stability"},
                        domain={'x': [0, 0.33], 'y': [0, 1]}
                    ))
                    fig.add_trace(go.Indicator(
                        mode="gauge+number",
                        value=grid_stability['frequency_stability'],
                        title={'text': "Frequency Stability"},
                        domain={'x': [0.33, 0.66], 'y': [0, 1]}
                    ))
                    fig.add_trace(go.Indicator(
                        mode="gauge+number",
                        value=grid_stability['phase_balance'],
                        title={'text': "Phase Balance"},
                        domain={'x': [0.66, 1], 'y': [0, 1]}
                    ))
                    st.plotly_chart(fig, use_container_width=True)
                
                # Load Balancing
                load_balancing = fetch_load_balancing(system["id"])
                if load_balancing:
                    st.subheader("Load Balancing")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Load Imbalance", f"{load_balancing['load_imbalance']:.1f}%")
                    with col2:
                        st.metric("Generation Imbalance", f"{load_balancing['generation_imbalance']:.1f}%")
                    with col3:
                        st.metric("Battery Utilization", f"{load_balancing['battery_utilization']:.1f}%")
                
                st.divider()
    
    # Auto-refresh
    time.sleep(REFRESH_INTERVAL)
    st.experimental_rerun()

if __name__ == "__main__":
    main() 