from flask import Flask, request, jsonify,Response,stream_with_context
from flask_cors import CORS
import certifi
from pytube import YouTube
import ssl
import os
import requests

ssl._create_default_https_context = ssl._create_stdlib_context

app = Flask(__name__)
CORS(app)

SAVE_PATH = os.path.join(os.getcwd(), "Downloads") # Changed to relative path

@app.route('/getData')
def getData():
    return "This is your data "



@app.route('/getVideoInfo', methods=['POST'])
def getVideo():
    try:
        ctx = ssl.create_default_context(cafile=certifi.where())
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided or data is not in JSON format'}), 400

        url = data['url']
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        # Stream the video content
        r = requests.get(video.url, stream=True)

        def generate():
            for chunk in r.iter_content(chunk_size=4096):
                yield chunk

        return Response(generate(), content_type=r.headers['Content-Type'],
                        headers={'Content-Disposition': f'attachment; filename="{yt.title}.mp4"'})

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500





@app.route('/downloadVideo', methods=['POST'])
def downloadVideo():
    try:
        data = request.json
        if not data or 'url' not in data:
            return jsonify({'error': 'No URL provided'}), 400

        url = data['url']
        yt = YouTube(url)
        video = yt.streams.filter(progressive=True, file_extension='mp4').order_by('resolution').desc().first()

        def generate():
            response = requests.get(video.url, stream=True)
            for chunk in response.iter_content(chunk_size=4096):
                yield chunk

        # Sanitize the filename
        safe_title = "".join([c for c in yt.title if c.isalpha() or c.isdigit() or c==' ']).rstrip()
        filename = f"{safe_title}.mp4"

        return Response(stream_with_context(generate()),
                        headers={
                            "Content-Disposition": f"attachment; filename=\"{filename}\"",
                            "Content-Type": "video/mp4"
                        })

    except Exception as e:
        app.logger.error(f"An error occurred: {str(e)}")
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Flask server...")
    app.run(debug=True, host='0.0.0.0', port=5000)