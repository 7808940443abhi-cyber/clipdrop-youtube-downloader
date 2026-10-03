from flask import Flask, render_template, request, jsonify, send_file
import os, uuid, threading
import yt_dlp

app = Flask(__name__)
DOWNLOAD_DIR = os.path.join(os.path.dirname(__file__), "downloads")
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

def valid_url(url):
    return isinstance(url, str) and ("youtube.com/" in url or "youtu.be/" in url)

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/api/info")
def info():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not valid_url(url):
        return jsonify(error="Please enter a valid YouTube URL."), 400

    try:
        opts = {"quiet": True, "no_warnings": True, "skip_download": True}
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
        return jsonify({
            "title": info.get("title"),
            "thumbnail": info.get("thumbnail"),
            "duration": info.get("duration"),
            "uploader": info.get("uploader"),
        })
    except Exception as e:
        return jsonify(error="Could not read this video. It may be unavailable or restricted."), 400

@app.post("/api/download")
def download():
    data = request.get_json(silent=True) or {}
    url = (data.get("url") or "").strip()
    if not valid_url(url):
        return jsonify(error="Please enter a valid YouTube URL."), 400

    job_id = uuid.uuid4().hex
    outtmpl = os.path.join(DOWNLOAD_DIR, f"{job_id}.%(ext)s")

    try:
        # MP4 video download. Use only for videos you are allowed to download.
        opts = {
            "quiet": True,
            "no_warnings": True,
            "outtmpl": outtmpl,
            "format": "best[ext=mp4]/best",
            "noplaylist": True,
        }
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=True)
            path = ydl.prepare_filename(info)
            if not os.path.exists(path):
                candidates = [os.path.join(DOWNLOAD_DIR, f) for f in os.listdir(DOWNLOAD_DIR)
                              if f.startswith(job_id + ".")]
                path = candidates[0] if candidates else path

        if not os.path.exists(path):
            return jsonify(error="Download completed but the file could not be located."), 500

        return jsonify({
            "download_url": f"/api/file/{os.path.basename(path)}",
            "filename": os.path.basename(path)
        })
    except Exception:
        return jsonify(error="Download failed. Check the URL and try again."), 400

@app.get("/api/file/<name>")
def get_file(name):
    # Prevent path traversal
    safe = os.path.basename(name)
    path = os.path.join(DOWNLOAD_DIR, safe)
    if not os.path.isfile(path):
        return "File not found", 404
    return send_file(path, as_attachment=True, download_name=safe)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
