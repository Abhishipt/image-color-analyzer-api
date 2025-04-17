
from flask import Flask, request, jsonify
from flask_cors import CORS
from PIL import Image
import os
import uuid
import io
from collections import Counter
import threading
import time

app = Flask(__name__)
CORS(app)

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Auto delete file after 1 minutes
def delete_file_later(path, delay=60):
    def remove():
        time.sleep(delay)
        if os.path.exists(path):
            os.remove(path)
    threading.Thread(target=remove).start()

# Convert RGB tuple to HEX
def rgb_to_hex(rgb):
    return '#%02x%02x%02x' % rgb

# Get dominant colors from image
def get_dominant_colors(image_path, num_colors=5):
    image = Image.open(image_path)
    image = image.convert('RGB')
    image = image.resize((150, 150))  # Resize for speed
    pixels = list(image.getdata())
    most_common = Counter(pixels).most_common(num_colors)
    return [
        {'hex': rgb_to_hex(color), 'rgb': color}
        for color, count in most_common
    ]

@app.route('/')
def home():
    return jsonify({"status": "Image Color Analyzer API is alive ✅"}), 200

@app.route('/analyze', methods=['POST'])
def analyze_image():
    if 'image' not in request.files:
        return jsonify({'error': 'No image uploaded'}), 400

    image_file = request.files['image']
    if not image_file:
        return jsonify({'error': 'Empty file'}), 400

    image_id = str(uuid.uuid4())
    filename = f"{image_id}_{image_file.filename}"
    image_path = os.path.join(UPLOAD_FOLDER, filename)
    image_file.save(image_path)

    # Schedule deletion
    delete_file_later(image_path)

    # Dominant colors
    try:
        dominant_colors = get_dominant_colors(image_path)
    except Exception as e:
        return jsonify({'error': 'Error processing image', 'details': str(e)}), 500

    return jsonify({
        'dominant_colors': dominant_colors
    })

if __name__ == "__main__":
    app.run(debug=False)
