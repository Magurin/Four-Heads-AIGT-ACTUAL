import os
from flask import Flask, render_template, request, jsonify
from google.cloud import vision
import requests

app = Flask(__name__)

# Constants
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiMjBmZGU2YWYtNGFmNS00MjU0LWFkNGItMzQwZGU3OTY5NDI4IiwidHlwZSI6ImFwaV90b2tlbiJ9.ZnnPNRuk5l60DRi_E8Sayn_AfGioXmABVNAQCLs6j8k"
OCR_ENDPOINT = "https://api.edenai.run/v2/ocr/ocr"

os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = 'kuickhackhackatonimagelabels-57374b99c466.json'


FORBIDDEN_LABELS = [
    "meat", "cigarette", "fast food", "casino", "alcohol", "drugs",
    "gambling", "junk food", "sugar", "soda", "smoking", "overeating",
    "sedentary", "lack of exercise", "sleep deprivation", "red meat",
    "tobacco", "casino", "advertisement", "poster", "gas", "fire"
]


def detect_labels(image_content):
    client = vision.ImageAnnotatorClient()
    image = vision.Image(content=image_content)
    response = client.label_detection(image=image)
    labels = response.label_annotations

    detected_labels = [label.description.lower() for label in labels]
    has_forbidden_label = any(label in detected_labels for label in FORBIDDEN_LABELS)

    return detected_labels, has_forbidden_label


@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        if 'file' not in request.files:
            return jsonify({'error': 'No file part'})
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No selected file'})
        content = file.read()
        labels, has_forbidden_label = detect_labels(content)
        return jsonify({'labels': labels, 'forbidden': has_forbidden_label})

    return render_template('index.html')


@app.route('/upload', methods=['POST'])
def upload():
    file = request.files.get('file')
    if not file:
        return jsonify({"error": "No file uploaded"}), 400

    files = {'file': (file.filename, file.stream, file.mimetype)}
    headers = {"Authorization": f"Bearer {API_KEY}"}
    data = {"providers": "google", "language": "ru", "fallback_providers": "google"}

    try:
        response = requests.post(OCR_ENDPOINT, data=data, files=files, headers=headers)
        response.raise_for_status()
        ocr_text = response.json().get("google", {}).get("text", "")
        return jsonify({"ocr_text": ocr_text})
    except requests.RequestException as e:
        return jsonify({"error": str(e)}), 500

@app.route('/update_forbidden_labels', methods=['POST'])
def update_forbidden_labels():
    data = request.get_json()
    forbidden_labels = data.get('forbidden_labels', [])

    global FORBIDDEN_LABELS
    FORBIDDEN_LABELS = forbidden_labels

    return jsonify({'message': 'Forbidden labels updated successfully'})


@app.route('/reset_forbidden_labels', methods=['GET'])
def reset_forbidden_labels():
    global FORBIDDEN_LABELS
    FORBIDDEN_LABELS = [
        "meat", "cigarette", "fast food", "casino", "alcohol", "drugs",
        "gambling", "junk food", "sugar", "soda", "smoking", "overeating",
        "sedentary", "lack of exercise", "sleep deprivation", "red meat",
        "tobacco", "casino", "advertisement", "poster", "gas", "fire"
    ]
    return jsonify({'message': 'Default forbidden labels restored'})


if __name__ == '__main__':
    app.run(debug=True)