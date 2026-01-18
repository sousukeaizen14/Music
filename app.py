from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import uuid

app = FastAPI(title="Music Downloader API")

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/")
def root():
    return {"status": "ok", "message": "Music Downloader Backend running"}

@app.get("/download")
def download(
    query: str = Query(..., description="Artist - Title or URL"),
    format: str = "mp3",
    quality: str = "192"
):
    file_id = str(uuid.uuid4())
    output_template = f"{DOWNLOAD_DIR}/{file_id}.%(ext)s"

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,

        # FIX YOUTUBE / YT MUSIC
        "geo_bypass": True,
        "nocheckcertificate": True,
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },

        # Metadata & cover
        "addmetadata": True,
        "embedmetadata": True,
        "writethumbnail": True,
        "embedthumbnail": True,
    }

    # Postprocessing
    if format == "flac":
        ydl_opts["postprocessors"] = [
            {"key": "FFmpegExtractAudio", "preferredcodec": "flac"}
        ]
    else:
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": format,
                "preferredquality": quality,
            }
        ]

    # SEARCH MODE (ANTI ERROR)
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])

        # Cari file hasil download
        for file in os.listdir(DOWNLOAD_DIR):
            if file.startswith(file_id):
                return FileResponse(
                    path=f"{DOWNLOAD_DIR}/{file}",
                    filename=file,
                    media_type="application/octet-stream"
                )

        return JSONResponse({"error": "File not found"}, status_code=500)

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
