import requests
from PIL import Image

class ImageBackend:
    def __init__(self):
        self.BACKEND_URL = "http://stego-backend:5000"
    
    def encode_image(self, text, input_path=None, output_path=None, img=None):
        if img is not None:
            img.save('/tmp/input_neural.png')
            input_path = '/tmp/input_neural.png'

        with open(input_path, 'rb') as input_file:
            response = requests.post(
                f"{self.BACKEND_URL}/encode",
                files={'input_image': input_file},
                data={'message': text}, timeout=300
            )
        
        if output_path is None:
            output_path = '/tmp/output_neural_image.png'
        if response.status_code == 200:
            with open(output_path, 'wb') as output_file:
                output_file.write(response.content)
            print(f"Encoded image saved to {output_path}")
        else:
            print(f"Error during encoding: {response.status_code}")
            print(response.text)
        if img is not None:
            return Image.open(output_path)
        return output_path

    def decode_image(self, input_path=None, img=None):
        if img is not None:
            input_path = '/tmp/temp_int_neural_image.png'
            img.save(input_path)
        with open(input_path, 'rb') as input_file:
            response = requests.post(
                f"{self.BACKEND_URL}/decode",
                files={'input_image': input_file}, timeout=300
            )
        
        if response.status_code == 200:
            decoded_message = response.json().get("decoded_message")
            print(f"Decoded message: {decoded_message}")
            return decoded_message
        else:
            print(f"Error during decoding: {response.status_code}")
            return response.text

if __name__ == '__main__':
    img_back = ImageBackend()
    img_back.encode_image("/app/stego/frontend/static/0.png", "./output_back.png", "Secret message")
    img_back.decode_image("./output_back.png")