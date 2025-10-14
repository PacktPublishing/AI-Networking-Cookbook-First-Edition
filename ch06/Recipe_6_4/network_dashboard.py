# network_dashboard.py
import streamlit as st
import pandas as pd
import plotly.express as px

def show_dashboard():
    st.title("Network Dashboard")
    
    # Load data
    df = pd.read_csv('mock_data/network_metrics.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Show basic info
    st.subheader("Network Overview")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Devices", df['device_name'].nunique())
    with col2:
        st.metric("Data Points", len(df))
    with col3:
        st.metric("Avg Latency", f"{df['latency_ms'].mean():.1f}ms")
    
    # Create charts
    st.subheader("Performance Charts")
    
    col1, col2 = st.columns(2)
    
    with col1:
        latency_chart = px.line(df, x='timestamp', y='latency_ms', color='device_name', 
                               title="Latency Over Time")
        st.plotly_chart(latency_chart, use_container_width=True)
    
    with col2:
        cpu_chart = px.bar(df.groupby('device_name')['cpu_usage'].mean().reset_index(),
                           x='device_name', y='cpu_usage', title="Average CPU Usage")
        st.plotly_chart(cpu_chart, use_container_width=True)
    
    # Bandwidth chart
    bandwidth_chart = px.area(df, x='timestamp', y='bandwidth_mbps', color='device_name',
                             title="Bandwidth Usage")
    st.plotly_chart(bandwidth_chart, use_container_width=True)
    
    # Show data
    with st.expander("View Raw Data"):
        st.dataframe(df)

# Only run if this file is executed directly
if __name__ == "__main__":
    st.set_page_config(page_title="Network Dashboard", layout="wide")
    show_dashboard()