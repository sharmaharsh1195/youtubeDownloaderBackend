from flask import Flask, request, jsonify, Response, stream_with_context, send_file
from flask_cors import CORS
import ssl
import os
import requests
import io
from pytubefix import YouTube
from pytubefix.cli import on_progress

ssl._create_default_https_context = ssl._create_stdlib_context

app = Flask(__name__)
CORS(app)

@app.route('/getData')
def getData():
    return "This is your data"

@app.route('/downloadVideo', methods=['POST'])
def downloadVideo():
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        url = data['url']
        yt = YouTube(url, on_progress_callback=on_progress)
        video = yt.streams.get_highest_resolution()

        def generate():
            response = requests.get(video.url, stream=True)
            for chunk in response.iter_content(chunk_size=4096):
                yield chunk

        safe_title = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        filename = f"{safe_title}.mp4"

        return Response(stream_with_context(generate()),
                        headers={
                            "Content-Disposition": f"attachment; filename=\"{filename}\"",
                            "Content-Type": "video/mp4"
                        })

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/downloadMp3', methods=['POST'])
def downloadMp3():
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        url = data['url']
        yt = YouTube(url, on_progress_callback=on_progress)
        audio = yt.streams.get_audio_only()

        def generate():
            response = requests.get(audio.url, stream=True)
            for chunk in response.iter_content(chunk_size=4096):
                yield chunk

        safe_title = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c == ' ']).rstrip()
        filename = f"{safe_title}.mp3"

        return Response(stream_with_context(generate()),
                        headers={
                            "Content-Disposition": f"attachment; filename=\"{filename}\"",
                            "Content-Type": "audio/mpeg"
                        })

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)
