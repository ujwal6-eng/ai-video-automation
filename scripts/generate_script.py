import os
import json
from datetime import datetime
import google.generativeai as genai

# ===============================
# API KEY
# ===============================
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found")

genai.configure(api_key=API_KEY)

# ===============================
# MODEL (OFFICIAL & STABLE)
# ===============================
model = genai.GenerativeModel("gemini-pro")

# ===============================
# PROMPT (STRICT JSON)
# ===============================
prompt = """
You are an AI video director.

Create a YouTube Shorts video plan (30–40 seconds).

Rules:
- Output ONLY valid JSON
- No markdown
- No explanation
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

# ===============================
# GENERATE
# ===============================
response = model.generate_content(prompt)

text = response.text.strip()

# Remove accidental code fences
if text.startswith("```"):
    text = text.replace("```json", "").replace("```", "").strip()

# ===============================
# PARSE JSON
# ===============================
try:
    video_plan = json.loads(text)
except json.JSONDecodeError:
    print("❌ Gemini raw output:")
    print(text)
    raise RuntimeError("Gemini returned invalid JSON")

# ===============================
# SAVE OUTPUT
# ===============================
output = {
    "generated_at": datetime.utcnow().isoformat(),
    "video_plan": video_plan
}

with open("video_plan.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

# ===============================
# SUCCESS LOG
# ===============================
print("✅ Gemini SDK call successful")
print("🎬 Video plan saved to video_plan.json")
print("📌 Title:", video_plan.get("title"))
print("🎞️ Scenes:", len(video_plan.get("scenes", [])))
