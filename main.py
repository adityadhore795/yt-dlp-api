from fastapi import FastAPI
import yt_dlp
import os

app = FastAPI()

# === CONFIG ===
YOUTUBE_CHANNEL_URL = "https://www.youtube.com/@Knot_Master/shorts"
UPLOADED_IDS_FILE = "uploaded_ids.txt"
COOKIES_FILE = "cookies.txt"

def get_uploaded_ids():
    if not os.path.exists(UPLOADED_IDS_FILE):
        return set()
    with open(UPLOADED_IDS_FILE, "r") as f:
        return set(line.strip() for line in f)

def save_uploaded_id(video_id):
    with open(UPLOADED_IDS_FILE, "a") as f:
        f.write(video_id + "\n")

@app.get("/get-latest-short")
def download_short():
    uploaded_ids = get_uploaded_ids()

    # === GET VIDEO LIST FROM CHANNEL ===
    ydl_opts = {
        'quiet': True,
        'extract_flat': True,
        'force_generic_extractor': False
    }

    with yt_dlp.YoutubeDL(ydl_opts) as yt_dl:
        result = yt_dl.extract_info(YOUTUBE_CHANNEL_URL, download=False)
        entries = result.get('entries', [])

    for entry in entries:
        video_id = entry['id']
        if video_id in uploaded_ids:
            continue

        video_url = entry['url']
        print("✅ Found new video:", video_url)

        # === DOWNLOAD VIDEO with PROXY ===
        ydl_opts_download = {
            'format': 'best[ext=mp4]/best',
            'outtmpl': 'latest_short.%(ext)s',
            'cookies': COOKIES_FILE,
            'proxy': 'https://us.proxymesh.com:31280'  # ✅ FREE PROXY
        }

        with yt_dlp.YoutubeDL(ydl_opts_download) as ydl:
            info = ydl.extract_info(video_url, download=True)

        save_uploaded_id(video_id)

        return {
            "video_id": video_id,
            "title": info.get("title", ""),
            "description": info.get("description", ""),
            "filename": "latest_short.mp4"
        }

    return {"message": "No new video found."}

