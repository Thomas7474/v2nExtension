from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled
from deep_translator import GoogleTranslator
import re
from flask_cors import CORS
import json
import requests
from fuzzywuzzy import fuzz

app = Flask(__name__)
CORS(app)

def fetch_transcript(youtube_url, supported_languages=["en", "hi", "es", "fr", "ml"], target_language="en"):
    """Fetches the transcript for a given YouTube video, translates if needed, and returns a timestamped dictionary."""
    try:
        video_id = youtube_url.split("v=")[-1]
        transcript_data = None
        detected_language = None

        for lang in supported_languages:
            try:
                transcript_data = YouTubeTranscriptApi.get_transcript(video_id, languages=[lang])
                detected_language = lang
                break
            except:
                continue

        if not transcript_data:
            return None, "No transcript available."

        transcript_with_timestamps = []
        for entry in transcript_data:
            start_time = entry["start"]
            minutes = int(start_time // 60)
            seconds = int(start_time % 60)
            formatted_time = f"{minutes:02d}:{seconds:02d}"
            text = entry["text"]

            if detected_language != target_language:
                text = GoogleTranslator(source=detected_language, target=target_language).translate(text)
            
            transcript_with_timestamps.append({"timestamp": formatted_time, "text": text})
        
        return transcript_with_timestamps, None
    except TranscriptsDisabled:
        return None, "Transcripts are disabled for this video."
    except Exception as e:
        return None, f"Error fetching transcript: {e}"

@app.route("/process", methods=["POST"])
def process_youtube_video():
    """Processes a YouTube video link and returns a transcript formatted for the extension."""
    try:
        request_data = request.get_json()
        youtube_link = request_data.get("link")

        print("Received link:", youtube_link)
        if "v=" not in youtube_link:
            return jsonify({"error": "Invalid YouTube link."}), 400

        transcript, error = fetch_transcript(youtube_link)
        if error:
            return jsonify({"error": error}), 400

        if not transcript:
            return jsonify({"error": "No transcript available."}), 400

        # Format transcript into "segments" as expected by popup.js
        formatted_transcript = [
            {"timestamp": entry["timestamp"], "summary": entry["text"]}
            for entry in transcript
        ]

        return jsonify({"segments": formatted_transcript, "status": "success"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
