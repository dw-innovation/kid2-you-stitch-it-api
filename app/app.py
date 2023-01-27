from flask import Flask, send_file, request
import cv2
import numpy as np

app = Flask(__name__)

@app.route("/stitchPanorama", methods=["POST"])
def stitchPanorama():
    image_files = request.files.getlist("images")
    imgs = []

    for image_file in image_files:
        img = cv2.imdecode(np.fromstring(image_file.read(), np.uint8), cv2.IMREAD_UNCHANGED)
        imgs.append(img)
    
    stitchy=cv2.Stitcher.create()

    (dummy,output)=stitchy.stitch(imgs)
    
    if dummy != cv2.STITCHER_OK:
        return "not successful"
    else: 
        cv2.imwrite('stitched_panorama.jpg', output)
        return send_file('stitched_panorama.jpg', mimetype='image/jpeg')

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)