from flask import Flask, render_template, request, jsonify
import requests

app = Flask(__name__)

# Constants
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjBmZGU2YWYtNGFmNS00MjU0LWFkNGItMzQwZGU3OTY5NDI4IiwidHlwZSI6ImFwaV90b2tlbiJ9.ZnnPNRuk5l60DRi_E8Sayn_AfGioXmABVNAQCLs6j8k"
OCR_ENDPOINT = "https://api.edenai.run/v2/ocr/ocr"


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    files = {'file': (file.filename, file.stream, file.mimetype)}
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {"providers": "google", "language": "en", "fallback_providers": "google"}

    try:
        response = requests.post(OCR_ENDPOINT, data=data, files=files, headers=headers)
        response.raise_for_status()
        ocr_text = response.json().get("google", {}).get("text", "")
        return jsonify({"ocr_text": ocr_text})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)
