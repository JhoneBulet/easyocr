# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
import easyocr
import numpy as np
import base64
from PIL import Image
import io
import re
import os  # Import the os module

app = Flask(__name__)
CORS(app)

# Initialize OCR reader once
# The model files will be downloaded to /opt/render/.cache/easyocr/
# Render's filesystem is ephemeral, so models might be re-downloaded on new deploys
reader = easyocr.Reader(['en'])

def extract_3_digits(text):
    """Extract 3-digit numbers from text"""
    # This regex is improved to avoid capturing parts of larger numbers
    numbers = re.findall(r'(?<!\d)\d{3}(?!\d)', text)
    return numbers

@app.route('/')
def index():
    # A simple route to confirm the server is running
    return "OCR Server is running!"

@app.route('/ocr', methods=['POST'])
def process_image():
    try:
        data = request.get_json()
        if 'image' not in data:
            return jsonify({"error": "No image data found in request"}), 400

        image_data = base64.b64decode(data['image'])
        image = Image.open(io.BytesIO(image_data))
        image_np = np.array(image)

        # OCR processing
        results = reader.readtext(image_np, allowlist='0123456789')
        all_text = ' '.join([text for (_, text, _) in results])

        # Find 3-digit numbers
        three_digit_numbers = extract_3_digits(all_text)

        return jsonify({
            "numbers": three_digit_numbers,
            "count": len(three_digit_numbers)
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# The __main__ block is removed for production; Gunicorn will run the app