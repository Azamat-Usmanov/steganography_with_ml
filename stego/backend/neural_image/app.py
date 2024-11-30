from flask import Flask, request, jsonify, send_file
from steganogan import SteganoGAN
import os
import numpy as np
from skimage.measure import shannon_entropy
from PIL import Image, ImageOps
import io
import torch
torch.backends.cudnn.enabled = False
torch.cuda.is_available = lambda : False

app = Flask(__name__)
UPLOAD_FOLDER = '/tmp/uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

class SteganoService:
    def __init__(self):
        self.steganogan = SteganoGAN.load(architecture='dense')
        self.steganogan.set_device('cpu')
        self.steganogan.verbose = False

    def encode(self, input_path, secret_message):
        output_path = input_path.replace('.png', '_encoded.png')
        self.steganogan.encode(input_path, output_path, secret_message)
        return output_path

    def decode(self, input_path):
        return self.steganogan.decode(input_path)

    @staticmethod
    def calculate_entropy(image_path):
        img = Image.open(image_path).convert("L")  # Преобразование в оттенки серого
        img_array = np.array(img)
        return {"entropy": shannon_entropy(img_array)}

    @staticmethod
    def image_difference(img1_path, img2_path, tol=0):
        img1 = np.array(Image.open(img1_path))
        img2 = np.array(Image.open(img2_path))
        diff = np.where(np.isclose(img1, img2, atol=tol), 0, img2)
        entropy_diff = shannon_entropy(diff)
        return {"difference_entropy": entropy_diff, "same_pixels": np.sum(diff == 0)}

stegano_service = SteganoService()

def save_uploaded_file(file, filename):
    file_path = os.path.join(UPLOAD_FOLDER, filename)
    file.save(file_path)
    return file_path

@app.route('/encode', methods=['POST'])
def encode():
    try:
        secret_message = request.form['message']
        input_file = request.files['input_image']
        if not input_file:
            return jsonify({"error": "No input image provided"}), 400
        
        input_path = save_uploaded_file(input_file, 'input.png')
        output_path = stegano_service.encode(input_path, secret_message)
        
        with open(output_path, 'rb') as f:
            encoded_image = f.read()
        
        return send_file(io.BytesIO(encoded_image), mimetype='image/png')
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/decode', methods=['POST'])
def decode():
    try:
        input_file = request.files['input_image']
        if not input_file:
            return jsonify({"error": "No input image provided"}), 400

        input_path = save_uploaded_file(input_file, 'input_to_decode.png')
        decoded_message = stegano_service.decode(input_path)
        return jsonify({"decoded_message": decoded_message})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/entropy', methods=['POST'])
def calculate_entropy():
    try:
        input_file = request.files['image']
        input_path = save_uploaded_file(input_file, 'entropy_image.png')

        response = stegano_service.calculate_entropy(input_path)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/image_difference', methods=['POST'])
def image_difference():
    try:
        img1_file = request.files['image1']
        img2_file = request.files['image2']
        tol = float(request.form.get('tol', 0))

        img1_path = save_uploaded_file(img1_file, 'image1.png')
        img2_path = save_uploaded_file(img2_file, 'image2.png')

        response = stegano_service.image_difference(img1_path, img2_path, tol)
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
