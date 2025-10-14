import streamlit as st
import requests

# Get your OpenAI API key
openai_key = st.secrets["api_keys"]["OPENAI_API_KEY"]

# Simple example: Get available OpenAI models
def get_openai_models():
    headers = {
        "Authorization": f"Bearer {openai_key}",
        "Content-Type": "application/json"
    }
    
    response = requests.get("https://api.openai.com/v1/models", headers=headers)
    if response.status_code == 200:
        models = response.json()
        return [model["id"] for model in models["data"] if "gpt" in model["id"]]
    return []

# Use it in your Streamlit app
if st.button("Check Available AI Models"):
    with st.spinner("Fetching models..."):
        models = get_openai_models()
        if models:
            st.success(f"Found {len(models)} GPT models!")
            st.write(models[:5])  # Show first 5 models
        else:
            st.error("Could not fetch models. Check your API key.")