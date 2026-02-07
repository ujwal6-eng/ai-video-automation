import os
import json
import requests
from datetime import datetime

API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found in environment variables")

# Gemini API endpoint (text generation)
URL = (
    "https://generativelanguage.googleapis.com/v1beta/models/"
    "gemini-1.5-flash:generateContent"
)

headers = {
    "Content-Type": "application/json",
}

prompt = """
You are an AI video director.
Create a YouTube Shorts video plan (30–40 seconds).

Return ONLY valid JSON in this exact format:

{
  "title": "...",
  "scenes": [
    { "prompt": "...", "duration": 5 },
    { "prompt": "...", "duration": 6 }
  ],
  "voiceover": "..."
}

Topic: One surprising fact about artificial intelligence.
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

response = requests.post(
    f"{URL}?key={API_KEY}",
    headers=headers,
    json=payload,
    timeout=30
)

response.raise_for_status()

data = response.json()

# Extract text output
text_output = data["candidates"][0]["content"]["parts"][0]["text"]

# Gemini kabhi kabhi ```json ``` ke andar deta hai – clean karo
cleaned = text_output.strip()
cleaned = cleaned.removeprefix("```json").removesuffix("```").strip()

video_plan = json.loads(cleaned)

# Save output
output = {
    "generated_at": datetime.utcnow().isoformat(),
    "video_plan": video_plan
}

with open("video_plan.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print("✅ Gemini API call successful")
print("🎬 Video plan saved to video_plan.json")
print("📌 Title:", video_plan["title"])
