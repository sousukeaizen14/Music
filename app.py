from fastapi import FastAPI, Query
from fastapi.responses import FileResponse, JSONResponse
import yt_dlp
import os
import glob

app = FastAPI()

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

@app.get("/download")
def download(
    query: str = Query(...),
    format: str = "best"
):
    outtmpl = f"{DOWNLOAD_DIR}/%(artist|uploader)s - %(title)s.%(ext)s"

    # FORMAT LOGIC (NO RE-ENCODE)
    if format == "opus":
        ytdlp_format = "bestaudio[ext=opus]/bestaudio"
    elif format == "m4a":
        ytdlp_format = "bestaudio[ext=m4a]/bestaudio"
    else:
        ytdlp_format = "bestaudio/best"

    ydl_opts = {
        "format": ytdlp_format,
        "outtmpl": outtmpl,

        # YouTube / YT Music FIX
        "geo_bypass": True,
        "quiet": True,
        "extractor_args": {
            "youtube": {
                "player_client": ["android"]
            }
        },

        # METADATA
        "addmetadata": True,
        "embedmetadata": True,
        "writethumbnail": True,
        "embedthumbnail": True,

        # REMUX ONLY (NO CONVERT)
        "postprocessors": [
            {"key": "FFmpegMetadata"},
            {
                "key": "FFmpegThumbnailsConvertor",
                "format": "jpg"
            }
        ]
    }

    # SEARCH MODE (STABIL)
    if not query.startswith("http"):
        query = f"ytsearch1:{query}"

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([query])

        files = sorted(
            glob.glob(f"{DOWNLOAD_DIR}/*"),
            key=os.path.getmtime,
            reverse=True
        )

        return FileResponse(
            files[0],
            filename=os.path.basename(files[0]),
            media_type="application/octet-stream"
        )

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)
