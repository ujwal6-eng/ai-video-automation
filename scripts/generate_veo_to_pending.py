import os
import json
import time
import requests

from google import genai
from google.genai import types

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload


# =================================================
# ENV (GitHub Secrets se aata hai)
# =================================================
# GOOGLE_API_KEY        -> Veo API key
# GOOGLE_TOKEN_JSON     -> OAuth token.json (string)
# PENDING_FOLDER_ID     -> Drive folder ID

GOOGLE_API_KEY = os.environ["GOOGLE_API_KEY"]
TOKEN_JSON = os.environ["GOOGLE_TOKEN_JSON"]
PENDING_FOLDER_ID = os.environ["PENDING_FOLDER_ID"]


# =================================================
# 1️⃣ INIT VEO CLIENT  (<<< यही FIX है >>>)
# =================================================
client = genai.Client(api_key=GOOGLE_API_KEY)


# =================================================
# 2️⃣ GENERATE VIDEO WITH VEO 3
# =================================================
operation = client.models.generate_videos(
    model="veo-3.1-fast-generate-preview",
    prompt="a close-up shot of a golden retriever playing in a field of sunflowers",
    config=types.GenerateVideosConfig(
        aspect_ratio="9:16",
        resolution="720p",
    ),
)

print("🎬 Veo video generation started...")


# =================================================
# 3️⃣ WAIT FOR COMPLETION
# =================================================
while not operation.done:
    time.sleep(10)
    operation = client.operations.get(operation.name)
    print("⏳ processing...")


result = operation.result
video_url = result.generated_videos[0].video.uri


# =================================================
# 4️⃣ DOWNLOAD VIDEO
# =================================================
video_file = "veo_output.mp4"

with requests.get(video_url, stream=True) as r:
    r.raise_for_status()
    with open(video_file, "wb") as f:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)

print("⬇️ Video downloaded:", video_file)


# =================================================
# 5️⃣ UPLOAD TO GOOGLE DRIVE (OAuth token.json)
# =================================================
creds = Credentials.from_authorized_user_info(
    json.loads(TOKEN_JSON),
    scopes=["https://www.googleapis.com/auth/drive"]
)

drive = build("drive", "v3", credentials=creds)

media = MediaFileUpload(video_file, mimetype="video/mp4", resumable=True)

uploaded = drive.files().create(
    body={
        "name": f"veo_{int(time.time())}.mp4",
        "parents": [PENDING_FOLDER_ID],
    },
    media_body=media,
    fields="id,name"
).execute()

print("✅ Uploaded to Drive pending folder:", uploaded["name"])
