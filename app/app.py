
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


def preprocess_image(img):
    """Preprocess images for better stitching results while preserving color"""
    # Apply CLAHE to each color channel separately for better color preservation
    lab = cv2.cvtColor(img, cv2.COLOR_BGR2LAB)
    l, a, b = cv2.split(lab)
    
    # Apply CLAHE to the L channel only
    clahe = cv2.createCLAHE(clipLimit=3.0, tileGridSize=(8,8))
    l = clahe.apply(l)
    
    # Merge channels back and convert to BGR
    enhanced = cv2.merge([l, a, b])
    return cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

def resize_image_for_processing(img, max_dimension=2000):
    """Resize image while maintaining aspect ratio for high-quality processing"""
    height, width = img.shape[:2]
    if max(height, width) > max_dimension:
        if height > width:
            new_height = max_dimension
            new_width = int(width * (max_dimension / height))
        else:
            new_width = max_dimension
            new_height = int(height * (max_dimension / width))
        return cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
    return img

@app.route("/stitchPanorama", methods=["POST"])
@cross_origin(origins=origins)
def stitchPanorama():
    image_files = request.files.getlist("images")
    if not image_files:
        return jsonify({"error": "No images provided"}), 400
    if len(image_files) < 2:
        return jsonify({"error": "At least 2 images are required to stitch a panorama"}), 400

    imgs = []
    original_imgs = []

    try:
        for image_file in image_files:
            # Decode image
            img_array = np.frombuffer(image_file.read(), np.uint8)
            img = cv2.imdecode(img_array, cv2.IMREAD_COLOR)
            
            if img is None:
                return jsonify({"error": f"Failed to decode image: {image_file.filename}"}), 400
            
            # Store original for final high-quality stitching
            original_imgs.append(img.copy())
            
            # Resize for processing to improve performance
            resized = resize_image_for_processing(img)
            
            # Preprocess for better feature detection
            preprocessed = preprocess_image(resized)
            
            imgs.append(preprocessed)
            
    except Exception as e:
        return jsonify({"error": f"Image processing error: {str(e)}"}), 500

    # Try different stitching modes for better results
    stitching_modes = [cv2.STITCHER_PANORAMA, cv2.STITCHER_SCANS]
    
    for mode in stitching_modes:
        try:
            stitcher = cv2.Stitcher.create(mode)
            
            # Configure stitcher for high-quality results
            stitcher.setRegistrationResol(0.8)
            stitcher.setSeamEstimationResol(0.2)
            stitcher.setCompositingResol(1.0)
            stitcher.setPanoConfidenceThresh(0.8)
            
            # First attempt with preprocessed images for better feature detection
            status, output = stitcher.stitch(imgs)
            
            if status == cv2.STITCHER_OK:
                # Re-stitch with original colors using the same stitcher parameters
                resized_originals = [resize_image_for_processing(img) for img in original_imgs]
                original_status, original_output = stitcher.stitch(resized_originals)
                if original_status == cv2.STITCHER_OK:
                    output = original_output
                break
                
            # If preprocessed fails, try with original resized images
            resized_originals = [resize_image_for_processing(img) for img in original_imgs]
            status, output = stitcher.stitch(resized_originals)
            
            if status == cv2.STITCHER_OK:
                break
                
        except Exception as e:
            continue
    
    # Handle stitching results
    if status != cv2.STITCHER_OK:
        error_messages = {
            cv2.STITCHER_ERR_NEED_MORE_IMGS: "Need more images for stitching",
            cv2.STITCHER_ERR_HOMOGRAPHY_EST_FAIL: "Homography estimation failed - images may not overlap enough",
            cv2.STITCHER_ERR_CAMERA_PARAMS_ADJUST_FAIL: "Camera parameter adjustment failed"
        }
        error_msg = error_messages.get(status, f"Stitching failed with status code: {status}")
        return jsonify({"error": error_msg}), 500
    
    # Post-process the result
    try:
        # Crop black borders
        gray = cv2.cvtColor(output, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 1, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        if contours:
            # Find the largest contour (the panorama)
            largest_contour = max(contours, key=cv2.contourArea)
            x, y, w, h = cv2.boundingRect(largest_contour)
            output = output[y:y+h, x:x+w]
        
        # Generate unique filename and save with high quality
        output_filename = f"stitched_panorama_{uuid.uuid4().hex[:8]}.png"
        cv2.imwrite(output_filename, output, [cv2.IMWRITE_PNG_COMPRESSION, 0])
        
        return send_file(output_filename, mimetype="image/png"), 200
        
    except Exception as e:
        return jsonify({"error": f"Post-processing error: {str(e)}"}), 500


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
