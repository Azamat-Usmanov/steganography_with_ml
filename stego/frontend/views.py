from aiohttp.web import Response, View, FileResponse
from aiohttp_jinja2 import render_template

from image import image_to_img_src, open_image, audio_to_src
from mlapi import MLApi
from PIL import Image
import os
import tempfile

TEMP_DIR = tempfile.gettempdir()


def process_simple_image_steganography(*image):
    return Image.open('/app/stego/frontend/static/0.png')

def process_simple_audio_steganography(*file):
    return None

def process_audio_file(*file):
    return None

def decode_image(*file):
    return '<Распознанный текст>'

def decode_audio(*file):
    return '<Распознанный текст>'

class IndexView(View):
    template = "index.html"

    async def get(self) -> Response:
        # Render the template, passing request as part of the context
        ctx = {"request": self.request, "action": None}  # Add an 'action' key to check in the template
        return render_template(self.template, self.request, ctx)

    async def post(self) -> Response:
        try:
            form = await self.request.post()
            action = form.get("action")
            stego_type = form.get("stego_type")
            algorithm = form.get("algorithm")
            uploaded_file = form["file"].file
            input_text = form.get("input_text", "")  # Get the text to encode

            # Pass the action and other form data into the context
            ctx = {"request": self.request, "action": action}

            if action == "encode":
                if stego_type == "image":
                    image = open_image(uploaded_file)
                    if algorithm == "simple":
                        result = process_simple_image_steganography(image, input_text)
                    elif algorithm == "neural":
                        result = MLApi().run_model(image, input_text)
                    temp_file = os.path.join(TEMP_DIR, "encoded_image.png")
                    result.save(temp_file)

                    image_b64 = image_to_img_src(result)
                    ctx["processed_image"] = image_b64
                    ctx["download_link"] = f"/download?file={temp_file}"

                elif stego_type == "audio":
                    if algorithm == "simple":
                        result = process_simple_audio_steganography(uploaded_file, input_text)
                    elif algorithm == "neural":
                        result = process_audio_file(uploaded_file, input_text)

                    temp_file = os.path.join(TEMP_DIR, "encoded_audio.mp3")
                    with open(temp_file, "wb") as f:
                        f.write(result)

                    audio_src = audio_to_src(result)
                    ctx["processed_audio"] = audio_src
                    ctx["download_link"] = f"/download?file={temp_file}"

            elif action == "decode":
                if stego_type == "image":
                    decoded_text = decode_image(uploaded_file, algorithm)
                    ctx["decoded_text"] = decoded_text

                elif stego_type == "audio":
                    decoded_text = decode_audio(uploaded_file, algorithm)
                    ctx["decoded_text"] = decoded_text

        except Exception as err:
            ctx = {"error": f"Обработка файла не удалась по причине: {err}", "request": self.request}

        return render_template(self.template, self.request, ctx)


async def download_file(request):
    file_path = request.query.get("file")
    if file_path and os.path.exists(file_path):
        return FileResponse(file_path)
    return Response(status=404, text="Файл не найден")
