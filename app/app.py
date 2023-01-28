from flask import Flask, send_file, request, jsonify
import cv2
import numpy as np
from flask_cors import CORS, cross_origin
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app, resources={
     r"/*": {"origins": ["http://localhost:3000", "http://localhost:3001", "https://kid2-video-panorama-stitcher.vercel.app/"]}})


@app.route("/stitchPanorama", methods=["POST"])
@cross_origin(origins=["http://localhost:3000", "http://localhost:3001", "https://kid2-video-panorama-stitcher.vercel.app/"])
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


if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)
