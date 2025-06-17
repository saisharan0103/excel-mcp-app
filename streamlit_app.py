import streamlit as st
import os
import google.generativeai as genai
import requests
import json

# ======= CONFIG =======
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyB6IkuZk_gHSQjz4p0ixOBcUKYkxiugktg"
BASE_URL = os.getenv("BASE_URL") or "https://excel-mcp.onrender.com"
MODEL_ID = "models/gemini-1.5-flash"

genai.configure(api_key=GEMINI_KEY, transport="rest")

# ======= MCP Write Function =======
def mcp_write(data, sheet_name):
    payload = {"data": data, "sheet_name": sheet_name}
    res = requests.post(f"{BASE_URL}/write-data", json=payload, timeout=30)
    res.raise_for_status()
    return res.json()

# ======= Gemini Agent Function =======
def run_agent(prompt: str):
    model = genai.GenerativeModel(MODEL_ID)
    schema_instruction = (
        "Return ONLY this JSON:\n"
        '{"data": [[1,2],[3,4]], "sheet_name": "Sheet1"}\n'
        f'for this instruction:\n"""{prompt}"""'
    )

    response = model.generate_content(schema_instruction)
    cleaned = (
        response.text.strip()
        .replace("```json", "")
        .replace("```", "")
        .strip()
    )
    parsed = json.loads(cleaned)

    result = mcp_write(parsed["data"], parsed["sheet_name"])
    return parsed, result, f"{BASE_URL}/download"

# ======= Streamlit UI =======
st.set_page_config(page_title="Excel Writer AI", layout="centered")
st.title("📊 Gemini Excel Writer")

prompt = st.text_area("Enter your natural-language instruction to generate Excel:", height=180)

if st.button("Generate Excel"):
    if not prompt.strip():
        st.error("Please enter a prompt.")
    else:
        try:
            with st.spinner("Processing with Gemini + writing Excel..."):
                parsed, result, download_link = run_agent(prompt)

            st.success("✅ Excel updated successfully!")
            st.code(json.dumps(parsed, indent=2), language="json")
            st.markdown(f"[📥 Click to download Excel]({download_link})")

        except Exception as e:
            st.error(f"❌ Error: {e}")