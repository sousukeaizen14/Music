from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import yt_dlp
import os
import glob

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

# Serve static UI
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
def ui():
    with open("static/index.html", encoding="utf-8") as f:
        return f.read()

@app.get("/download")
def download(query: str = Query(...)):
    outtmpl = f"{DOWNLOAD_DIR}/%(artist|uploader)s - %(title)s.%(ext)s"

    ydl_opts = {
        # Ambil audio terbaik dulu
        "format": "bestaudio/best",
        "outtmpl": outtmpl,

        # FIX YouTube Music
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },

        "geo_bypass": True,

        # Metadata & cover
        "addmetadata": True,
        "embedmetadata": True,
        "writethumbnail": True,
        "embedthumbnail": True,

        # Convert ke MP3 320 kbps
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "320",
            },
            {
                "key": "FFmpegMetadata"
            },
            {
                "key": "EmbedThumbnail"
            }
        ],

        "quiet": True
    }

    # Kalau bukan URL → search otomatis
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])

        files = sorted(
            glob.glob(f"{DOWNLOAD_DIR}/*.mp3"),
            key=os.path.getmtime,
            reverse=True
        )

        return FileResponse(
            files[0],
            filename=os.path.basename(files[0]),
            media_type="audio/mpeg"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
