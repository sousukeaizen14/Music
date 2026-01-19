from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import glob

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

TIDAL_USER = os.getenv("TIDAL_USERNAME")
TIDAL_PASS = os.getenv("TIDAL_PASSWORD")

@app.get("/download/tidal")
def download_tidal(url: str = Query(...)):
    if not TIDAL_USER or not TIDAL_PASS:
        return JSONResponse(
            {"error": "TIDAL credentials not set"},
            status_code=500
        )

    ydl_opts = {
        # 👉 FLAC ASLI (TIDAK CONVERT)
        "format": "bestaudio[acodec=flac]/bestaudio",

        "outtmpl": f"{DOWNLOAD_DIR}/%(artist)s - %(title)s.%(ext)s",

        # 👉 LOGIN TIDAL
        "username": TIDAL_USER,
        "password": TIDAL_PASS,

        # 👉 METADATA
        "addmetadata": True,
        "embedmetadata": True,
        "writethumbnail": True,
        "embedthumbnail": True,

        # 👉 NO CONVERSION
        "postprocessors": [
            {"key": "FFmpegMetadata"},
            {"key": "EmbedThumbnail"}
        ],

        "quiet": True
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        files = sorted(
            glob.glob(f"{DOWNLOAD_DIR}/*.flac"),
            key=os.path.getmtime,
            reverse=True
        )

        return FileResponse(
            files[0],
            filename=os.path.basename(files[0]),
            media_type="audio/flac"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
