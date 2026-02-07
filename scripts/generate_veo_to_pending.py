import os
import time
import requests
from google import genai
from google.genai import types
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# =========================
# ENV VARIABLES (REQUIRED)
# =========================
# Google sets this automatically in Actions if key is present
# export GOOGLE_API_KEY=xxxx

DRIVE_SERVICE_ACCOUNT_JSON = os.environ["DRIVE_SERVICE_ACCOUNT_JSON"]
DRIVE_PENDING_FOLDER_ID = os.environ["DRIVE_PENDING_FOLDER_ID"]

# =========================
# 1️⃣ INIT CLIENT
# =========================
client = genai.Client()

# =========================
# 2️⃣ GENERATE VIDEO (VEO 3)
# =========================
operation = client.models.generate_videos(
    model="veo-3.1-fast-generate-preview",
    prompt="a close-up shot of a golden retriever playing in a field of sunflowers",
    config=types.GenerateVideosConfig(
        negative_prompt="barking, woofing",
        aspect_ratio="9:16",
        resolution="720p",
    ),
)

print("🎬 Veo generation started, waiting for completion...")

# =========================
# 3️⃣ WAIT FOR VIDEO
# =========================
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation.name)
    print("⏳ still processing...")

result = operation.result

# =========================
# 4️⃣ DOWNLOAD VIDEO
# =========================
video_url = result.generated_videos[0].video.uri

print("⬇️ Downloading video from:", video_url)

video_path = "veo_output.mp4"

with requests.get(video_url, stream=True) as r:
    r.raise_for_status()
    with open(video_path, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

print("✅ Video downloaded:", video_path)

# =========================
# 5️⃣ UPLOAD TO GOOGLE DRIVE (pending/)
# =========================
creds = Credentials.from_service_account_info(
    eval(DRIVE_SERVICE_ACCOUNT_JSON),
    scopes=["https://www.googleapis.com/auth/drive"]
)

drive = build("drive", "v3", credentials=creds)

media = MediaFileUpload(video_path, mimetype="video/mp4", resumable=True)

file = drive.files().create(
    body={
        "name": f"veo_{int(time.time())}.mp4",
        "parents": [DRIVE_PENDING_FOLDER_ID],
    },
    media_body=media,
    fields="id,name"
).execute()

print("📁 Uploaded to Drive pending folder:", file["name"])
