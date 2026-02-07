import os
import json
import requests
from datetime import datetime

# ===============================
# ENV CHECK
# ===============================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

# ===============================
# GEMINI API CONFIG
# ===============================
URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-pro:generateContent"
)

headers = {
    "Content-Type": "application/json"
}

# ===============================
# PROMPT (STRICT JSON OUTPUT)
# ===============================
prompt = """
You are an AI video director.

Create a YouTube Shorts video plan (30–40 seconds).

Rules:
- Return ONLY valid JSON
- No explanations
- No markdown
- No extra text

JSON format MUST be exactly:

{
  "title": "string",
  "scenes": [
    { "prompt": "string", "duration": number }
  ],
  "voiceover": "string"
}

Topic: One shocking fact about Artificial Intelligence.
"""

payload = {
    "contents": [
        {
            "parts": [
                {"text": prompt}
            ]
        }
    ]
}

# ===============================
# API CALL
# ===============================
response = requests.post(
    f"{URL}?key={API_KEY}",
    headers=headers,
    json=payload,
    timeout=60
)

# Raise error if API fails
response.raise_for_status()

data = response.json()

# ===============================
# EXTRACT & CLEAN RESPONSE
# ===============================
raw_text = data["candidates"][0]["content"]["parts"][0]["text"]

cleaned = raw_text.strip()

# Remove accidental markdown
if cleaned.startswith("```"):
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

# ===============================
# PARSE JSON
# ===============================
try:
    video_plan = json.loads(cleaned)
except json.JSONDecodeError as e:
    print("❌ Raw Gemini Output:")
    print(cleaned)
    raise RuntimeError("Gemini returned invalid JSON") from e

# ===============================
# SAVE OUTPUT
# ===============================
final_output = {
    "generated_at": datetime.utcnow().isoformat(),
    "video_plan": video_plan
}

with open("video_plan.json", "w", encoding="utf-8") as f:
    json.dump(final_output, f, indent=2, ensure_ascii=False)

# ===============================
# LOG SUCCESS
# ===============================
print("✅ Gemini API call successful")
print("🎬 Video plan saved to video_plan.json")
print("📌 Title:", video_plan.get("title"))
print("🎞️ Scenes:", len(video_plan.get("scenes", [])))
