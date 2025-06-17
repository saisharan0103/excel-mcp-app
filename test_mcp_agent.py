"""
test_mcp_agent.py
Use Gemini to parse natural prompts and write to Excel via your MCP FastAPI server.

Usage:
    python test_mcp_agent.py
    → prompts you for input

    OR

    python test_mcp_agent.py "Write [[10, 20], [30, 40]] to sheet 'Revenue'"
"""

import os
import sys
import json
import requests
import google.generativeai as genai

# ========= CONFIG =========
GEMINI_KEY = os.getenv("GEMINI_API_KEY") or "AIzaSyB6IkuZk_gHSQjz4p0ixOBcUKYkxiugktg"  # replace with your valid key
BASE_URL   = "https://excel-mcp.onrender.com"  # your live FastAPI server

# Configure Gemini to use REST + correct model path
genai.configure(api_key=GEMINI_KEY, transport="rest")
MODEL_ID = "models/gemini-1.5-flash"  # ✅ must use full model path!

# ========= MCP WRAPPERS =========
def mcp_write(data, sheet_name):
    payload = {
        "data": data,
        "sheet_name": sheet_name
    }
    res = requests.post(f"{BASE_URL}/write-data", json=payload, timeout=30)
    res.raise_for_status()
    return res.json()

def download_link():
    return f"{BASE_URL}/download"

# ========= AGENT =========
def agent(prompt: str):
    model = genai.GenerativeModel(MODEL_ID)
    sys.stderr.write("🧠 Gemini is parsing your instruction...\n")

    
    schema_instruction = (
        "Return ONLY valid JSON like this:\n"
        '{"data": [[1,2],[3,4]], "sheet_name": "Sheet1"}\n'
        f'Now generate the correct JSON that matches this instruction:\n"""{prompt}"""'
    )   


    try:
        response = model.generate_content(schema_instruction)
        print("🔎 Gemini Raw Response:", repr(response.text))

        # Clean the markdown code block stuff
        cleaned = (
            response.text.strip()
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        print("🧪 Cleaned Response:", cleaned)
        parsed = json.loads(cleaned)

    except Exception as e:
        raise ValueError(f"❌ Failed to parse Gemini response:\n{e}")

    print("✅ Parsed:", parsed)

    print("📤 Writing via MCP...")
    result = mcp_write(parsed["data"], parsed["sheet_name"])
    print("✅ MCP:", result)

    link = download_link()
    print("📥 Download link:", link)
    return link

# ========= CLI ENTRY =========
if __name__ == "__main__":
    if len(sys.argv) > 1:
        prompt_text = " ".join(sys.argv[1:])
    else:
        prompt_text = input("Prompt for Gemini ➜ ")

    try:
        agent(prompt_text)
    except Exception as e:
        print("❌ Error:", e)


