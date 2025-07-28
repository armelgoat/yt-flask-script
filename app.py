from flask import Flask, request, jsonify
import yt_dlp
import os
import requests
import uuid

app = Flask(__name__)

@app.route('/convert', methods=['POST'])
def convert():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No URL provided"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        'outtmpl': filename,
        'format': 'mp4/best'
    }

    # 🥇 Téléchargement de la vidéo avec yt_dlp
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        print("❌ ERREUR yt_dlp :", e)
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

    # 🥈 Upload vers transfer.sh
    try:
        with open(filename, 'rb') as f:
            headers = {'User-Agent': 'Mozilla/5.0'}
            r = requests.put(f"https://transfer.sh/{filename}", data=f, headers=headers)
        os.remove(filename)
        return jsonify({"link": r.text})
    except Exception as e:
        print("❌ ERREUR transfer.sh :", e)
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/')
def home():
    return '✅ YT-DLP Flask API is running'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
