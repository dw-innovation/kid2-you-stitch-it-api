<img width="1280" height="200" alt="492729813-74b7f12b-450c-41bb-8c47-bbf31402eff8" src="https://github.com/user-attachments/assets/1369c5d8-13b4-4a81-bac4-0f5112183d65" />

# KID2 – You Stitch It API

A Flask-based REST API for stitching multiple images into panoramic views using OpenCV. This service provides high-quality image stitching with intelligent preprocessing and post-processing capabilities.

## Features

- **Multi-image panorama stitching** - Combines 2 or more overlapping images into seamless panoramas
- **Intelligent preprocessing** - CLAHE enhancement and optimal resizing for better feature detection
- **High-quality output** - Alpha channel support with transparent border cropping
- **Multiple stitching modes** - Automatic fallback between PANORAMA and SCANS modes
- **CORS support** - Configurable cross-origin resource sharing
- **Docker ready** - Containerized deployment support

## API Endpoints

### POST /stitchPanorama

Stitches multiple images into a panoramic view.

**Request:**
- Method: `POST`
- Content-Type: `multipart/form-data`
- Body: Multiple image files under the `images` field

**Response:**
- Success: PNG image file with alpha channel
- Error: JSON object with error message

**Example using curl:**
```bash
curl -X POST \
  -F "images=@image1.jpg" \
  -F "images=@image2.jpg" \
  -F "images=@image3.jpg" \
  http://localhost:8080/stitchPanorama \
  --output panorama.png
```

## Requirements

- Python 3.8+
- OpenCV
- Flask
- NumPy
- Pillow
- Waitress
- Flask-CORS

## Installation

### Local Development

1. Clone the repository:
```bash
git clone https://github.com/dw-innovation/kid2-you-stitch-it-api
cd kid2-you-stitch-it-api
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python app/app.py
```

The API will be available at `http://localhost:8080`

### Docker Deployment

1. Build the Docker image:
```bash
docker build -t you-stitch-it-api .
```

2. Run the container:
```bash
docker run -p 8080:8080 -e ORIGINS="*" you-stitch-it-api
```

## Configuration

### Environment Variables

- `ORIGINS`: Comma-separated list of allowed CORS origins (default: "*")

Example:
```bash
export ORIGINS="http://localhost:3000,https://youstitch.it"
```

## Image Processing Pipeline

1. **Input Validation** - Ensures minimum 2 images are provided
2. **Preprocessing** - CLAHE enhancement on LAB color space L-channel
3. **Resizing** - Intelligent resizing to max 2000px dimension for optimal processing
4. **Stitching** - Multi-mode stitching with automatic fallback
5. **Post-processing** - Alpha channel creation and transparent border cropping
6. **Output** - High-quality PNG with transparency support

## Error Handling

The API provides detailed error messages for common issues:

- `Need more images for stitching` - Insufficient overlap between images
- `Homography estimation failed` - Images don't have enough matching features
- `Camera parameter adjustment failed` - Internal stitching algorithm failure

## Performance Notes

- Images are automatically resized to 2000px max dimension for processing
- CLAHE preprocessing improves feature detection in challenging lighting
- Multiple stitching modes ensure best results for different image sets
- Transparent output allows seamless integration into other applications

## License

MIT License

Copyright (c) 2024

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
