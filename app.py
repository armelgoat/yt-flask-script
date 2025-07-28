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

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

    try:
        with open(filename, 'rb') as f:
            r = requests.put(f"https://transfer.sh/{filename}", data=f)
        os.remove(filename)
        return jsonify({"link": r.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/')
def home():
    return 'YT-DLP Flask API is running ✅'
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)

