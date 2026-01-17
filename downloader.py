import yt_dlp

def choose_format():
    print("\nPilih format audio:")
    print("1. MP3")
    print("2. M4A (AAC)")
    print("3. OPUS")
    print("4. FLAC (Lossless)")

    return {
        "1": "mp3",
        "2": "m4a",
        "3": "opus",
        "4": "flac"
    }.get(input("Masukkan pilihan (1-4): ").strip(), "mp3")

def choose_quality():
    print("\nPilih kualitas audio:")
    print("1. 128 kbps")
    print("2. 192 kbps")
    print("3. 256 kbps")
    print("4. 320 kbps")

    return {
        "1": "128",
        "2": "192",
        "3": "256",
        "4": "320"
    }.get(input("Masukkan pilihan (1-4): ").strip(), "192")

def download_music(url, audio_format, quality, output_path="downloads"):
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": f"{output_path}/%(artist)s - %(title)s.%(ext)s",

        # Metadata & cover
        "addmetadata": True,
        "embedmetadata": True,
        "writethumbnail": True,
        "embedthumbnail": True,

        # Lyrics (jika tersedia)
        "writesubtitles": True,
        "writeautomaticsub": True,
        "subtitlesformat": "lrc",
        "subtitleslangs": ["en", "id"],

        # Embed lyric ke audio
        "embedsubtitles": True,

        "quiet": False,
    }

    # Post-processing audio
    if audio_format == "flac":
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "flac",
            }
        ]
    else:
        ydl_opts["postprocessors"] = [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": audio_format,
                "preferredquality": quality,
            }
        ]

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    print("=== Music Downloader Advanced ===")

    url = input("Masukkan URL musik/video: ").strip()
    audio_format = choose_format()

    if audio_format == "flac":
        quality = None
        print("\nFLAC dipilih (lossless)")
    else:
        quality = choose_quality()
        print(f"\nFormat: {audio_format.upper()} | {quality} kbps")

    print("\nFitur aktif:")
    print("- Embed cover album")
    print("- Metadata artist & album")
    print("- Embed lyric (jika tersedia)\n")

    download_music(url, audio_format, quality)

    print("\nDownload selesai!")
