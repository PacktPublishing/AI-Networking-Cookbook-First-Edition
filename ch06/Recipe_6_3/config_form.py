import streamlit as st
import requests

# Page setup
st.set_page_config(page_title="Network Config Form")
st.title("Network Configuration Form")

openai_key = st.secrets["api_keys"]["OPENAI_API_KEY"]


# Input fields
st.subheader("Device Information")

device_name = st.text_input("Device Name:", value="router-01")
device_ip = st.text_input("IP Address:", placeholder="192.168.1.1")

device_type = st.selectbox("Device Type:", ["Router", "Switch", "Firewall"])
vendor = st.selectbox("Vendor:", ["Cisco", "Juniper", "Arista"])

vlan_id = st.number_input("VLAN ID:", min_value=1, max_value=4094, value=100)
port_count = st.slider("Number of Ports:", 1, 48, 24)

enable_ssh = st.checkbox("Enable SSH", value=True)
enable_snmp = st.checkbox("Enable SNMP", value=False)

protocols = st.multiselect("Routing Protocols:", ["OSPF", "BGP", "EIGRP", "Static"])

# Generate configuration
if st.button("Generate Configuration"):
    if device_name and device_ip:
        # Create prompt for AI
        prompt = f"""
Generate network configuration commands for:
- Device: {device_name} ({device_type}, {vendor})
- IP: {device_ip}
- VLAN: {vlan_id}
- Ports: {port_count}
- SSH: {enable_ssh}
- SNMP: {enable_snmp}
- Protocols: {', '.join(protocols) if protocols else 'None'}

Create realistic CLI commands for this device.
        """
        
        # Call OpenAI
        headers = {"Authorization": f"Bearer {openai_key}"}
        data = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 300
        }
        
        with st.spinner("Generating configuration..."):
            response = requests.post("https://api.openai.com/v1/chat/completions", 
                                   headers=headers, json=data)
            
            if response.status_code == 200:
                config = response.json()["choices"][0]["message"]["content"]
                st.subheader("Generated Configuration:")
                st.code(config, language="bash")
            else:
                st.error("Failed to generate configuration")
    else:
        st.error("Please fill in device name and IP address")