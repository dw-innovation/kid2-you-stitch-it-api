
import os
from flask import Flask, send_file, request, jsonify
import cv2
import numpy as np
from flask_cors import CORS, cross_origin
import youtube_dl
import uuid

file_base_url= os.environ.get("FILES_BASE_URL", "")
origins = os.environ.get("ORIGINS", "").split(",")
download_path = os.environ.get("DOWNLOAD_PATH", '')

app = Flask(__name__)
CORS(app, resources={
     r"/*": {"origins": origins}})


@app.route("/stitchPanorama", methods=["POST"])
@cross_origin(origins=origins)
def stitchPanorama():
    image_files = request.files.getlist("images")
    if not image_files:
        return jsonify({"error": "No images provided"}), 400
    if len(image_files) < 2:
        return jsonify({"error": "At least 2 images are required to stitch a panorama"}), 400

    imgs = []

    try:
        for image_file in image_files:
            img = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), 1)
            imgs.append(img)
    except Exception as e:
        return jsonify(error="An error occurred: {}".format(e)), 500

    stitchy = cv2.Stitcher.create()

    try:
        (dummy, output) = stitchy.stitch(imgs)
    except Exception as e:
        return jsonify(error="An error occurred: {}".format(e)), 500

    if dummy != cv2.STITCHER_OK:
        return jsonify({"error": "Stitching not successful"}), 500
    else:
        cv2.imwrite("stitched_panorama.png", output)
        return send_file("stitched_panorama.png", mimetype="image/png"), 200


@app.route('/download', methods=['GET'])
@cross_origin(origins=origins)
def download():
    url = request.args.get('url')
    if not url:
        return "Error: No URL provided. Please provide a valid URL as a query parameter.", 400

    uuid_string = str(uuid.uuid4())
    ydl_opts = {
        'outtmpl': f'{download_path + uuid_string}.%(ext)s',
        'format': 'bestaudio/best',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)

    file_url = f'{file_base_url}{uuid_string}.{info["ext"]}'

    return jsonify({'file_url': file_url})


@app.route('/files/<path:file_name>')
@cross_origin(origins=origins)
def serve_file(file_name):
    file_path = download_path + file_name

    try:
        return send_file(file_path, as_attachment=True), 200
    except Exception as e:
        return jsonify(error="An error occurred: {}".format(e)), 500


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
