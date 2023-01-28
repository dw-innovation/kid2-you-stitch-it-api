from flask import Flask, send_file, request
import cv2
import numpy as np
from flask_cors import CORS
import logging

logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)
CORS(app)

@app.route("/stitchPanorama", methods=["POST"])
def stitchPanorama():
    image_files = request.files.getlist("images")
    imgs = []
    logging.debug("image_files", image_files)

    for image_file in image_files:
        # img = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        img = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), 1)
        imgs.append(img)
        logging.debug("image_file appended")

    
    stitchy=cv2.Stitcher.create()

    (dummy,output)=stitchy.stitch(imgs)
    
    if dummy != cv2.STITCHER_OK:
        return "not successful"
    else: 
        cv2.imwrite('stitched_panorama.png', output)
        return send_file('stitched_panorama.png', mimetype='image/png')

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)