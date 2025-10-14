import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Page setup
st.set_page_config(page_title="AI Network Dashboard", layout="wide")
st.title("AI Network Dashboard")

# Check for API key
try:
    openai_key = st.secrets["api_keys"]["OPENAI_API_KEY"]
    st.success("AI Ready")
except:
    st.error("Add OpenAI API key to .streamlit/secrets.toml")
    st.stop()

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
    # Latency over time
    latency_chart = px.line(df, x='timestamp', y='latency_ms', color='device_name', 
                           title="Latency Over Time")
    st.plotly_chart(latency_chart, use_container_width=True)

with col2:
    # CPU usage by device
    cpu_chart = px.bar(df.groupby('device_name')['cpu_usage'].mean().reset_index(),
                       x='device_name', y='cpu_usage', title="Average CPU Usage")
    st.plotly_chart(cpu_chart, use_container_width=True)

# Bandwidth chart
bandwidth_chart = px.area(df, x='timestamp', y='bandwidth_mbps', color='device_name',
                         title="Bandwidth Usage")
st.plotly_chart(bandwidth_chart, use_container_width=True)

# AI Chat Section
st.subheader("Ask AI About Your Data")

# Create data summary
data_summary = f"""
Devices: {', '.join(df['device_name'].unique())}
Average Latency: {df['latency_ms'].mean():.1f}ms
Average CPU: {df['cpu_usage'].mean():.1f}%
Average Bandwidth: {df['bandwidth_mbps'].mean():.1f}Mbps
Max Packet Loss: {df['packet_loss'].max():.1f}%
"""

# Chat interface
user_question = st.text_input("Ask about your network data:", 
                             placeholder="Which device has the highest latency?")

if st.button("Ask AI") and user_question:
    # Prepare prompt
    prompt = f"""
    You are a network engineer. Here's network data summary:
    {data_summary}
    
    Question: {user_question}
    
    Give a brief, helpful answer.
    """
    
    # Call OpenAI
    headers = {"Authorization": f"Bearer {openai_key}", "Content-Type": "application/json"}
    data = {
        "model": "gpt-3.5-turbo",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 150
    }
    
    with st.spinner("AI thinking..."):
        try:
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=data)
            if response.status_code == 200:
                ai_answer = response.json()["choices"][0]["message"]["content"]
                st.write("**AI Answer:**")
                st.write(ai_answer)
            else:
                st.error(f"Error: {response.status_code}")
        except Exception as e:
            st.error(f"Error: {e}")

# Show example questions
st.markdown("**Try asking:**")
st.markdown("- Which device has the best performance?")
st.markdown("- What's the trend in network usage?")
st.markdown("- Are there any issues I should know about?")

# Show data
with st.expander("View Raw Data"):
    st.dataframe(df)