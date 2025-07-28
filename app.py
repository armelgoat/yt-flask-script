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
        print("❌ ERREUR : aucune URL reçue")
        return jsonify({"error": "No URL provided"}), 400

    filename = f"{uuid.uuid4()}.mp4"
    ydl_opts = {
        'outtmpl': filename,
        'format': 'mp4/best'
    }

    # 🥇 Étape 1 – Téléchargement
    try:
        print(f"🎯 DÉBUT DU TÉLÉCHARGEMENT : {url}")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        print(f"✅ TÉLÉCHARGEMENT TERMINÉ : {filename}")
    except Exception as e:
        print("❌ ERREUR yt_dlp :", e)
        return jsonify({"error": f"Download failed: {str(e)}"}), 500

    # 🥈 Étape 2 – Upload vers File.io
    try:
        print("📤 UPLOAD VERS FILE.IO EN COURS...")
        with open(filename, 'rb') as f:
            files = {'file': f}
            r = requests.post("https://file.io", files=files)
        os.remove(filename)

        response_data = r.json()
        if not response_data.get("success"):
            print("❌ ERREUR file.io :", response_data)
            return jsonify({"error": "Upload to file.io failed", "details": response_data}), 500

        print("✅ UPLOAD TERMINÉ :", response_data["link"])
        return jsonify({"link": response_data["link"]})
    except Exception as e:
        print("❌ ERREUR file.io :", e)
        return jsonify({"error": f"Upload failed: {str(e)}"}), 500

@app.route('/')
def home():
    return '✅ YT-DLP Flask API with File.io is running'

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    app.run(host="0.0.0.0", port=port)
