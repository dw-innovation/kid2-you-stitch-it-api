from flask import Flask

app = Flask(__name__)

@app.route("/stitchPanorama", methods=["POST"])
def stitchPanorama():
    return "<h1>trying to stitch</h1>"

if __name__ == "__main__":
    from waitress import serve
    serve(app, host="0.0.0.0", port=8080)