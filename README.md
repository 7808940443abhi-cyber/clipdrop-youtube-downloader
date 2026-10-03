# ClipDrop — YouTube Link Downloader

A small Flask web app with a polished frontend and a server-side `yt-dlp` downloader.

## Run locally

1. Install Python 3.11+.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Start:

```bash
python app.py
```

4. Open `http://localhost:5000`.

## Deployment

Deploy the project to a Python-capable host such as Render, Railway, or a VPS. The start command is:

```bash
gunicorn app:app
```

## Important

Only use the downloader for videos you own or are authorized to download. YouTube's terms and individual video rights can restrict downloading or redistribution. Do not use this to bypass access controls, DRM, or private/restricted content.
