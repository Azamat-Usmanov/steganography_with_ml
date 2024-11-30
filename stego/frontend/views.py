from __future__ import annotations
import logging
from aiohttp.web import Response, View, FileResponse
from aiohttp_jinja2 import render_template

from image import image_to_img_src, open_image, audio_to_src
from mlapi import MLApi
from PIL import Image
import os
import tempfile
from pathlib import Path
from algo.lsb_audio import AudioLSB
from algo.lsb_image import ImageLSB
from algo.dct_image import ImageDCT
from audio_neural.predict import AudioNeural
from image_neural.iface import ImageBackend
from algo.audio_phase import AudioPhase


# Настройка логирования
if Path('/app').exists():
    Path("/app/stego/frontend/logs/").mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    filename="/app/stego/frontend/logs/web_app.log", # shared
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)

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
    
    def __init__(self, request):
        super().__init__(request)
        self.img_lsb = ImageLSB()
        self.audio_lsb = AudioLSB()
        self.img_dct = ImageDCT()
        self.audio_neural = AudioNeural()
        self.image_neural = ImageBackend()
        self.audio_phase = AudioPhase()

    async def get(self) -> Response:
        logging.info("GET запрос получен.")
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

            tmp_filename = 'tmp_file'

            # Логируем входные данные
            logging.info(f'Полученный файл: {uploaded_file}')
            logging.info(f"POST запрос получен: action={action}, stego_type={stego_type}, algorithm={algorithm}, input_text={input_text}")

            ctx = {"request": self.request, "action": action}

            if action == "encode":
                if stego_type == "image":
                    image = open_image(uploaded_file)
                    logging.info("Начата обработка изображения с текстом.")

                    if algorithm == "lsb": 
                        """ LSB """
                        result = self.img_lsb.encode_image(input_img=image, secret_text=input_text)
                        logging.info(f"Закодирован текст в изображение с помощью метода lsb. Текст: {input_text}.")

                    elif algorithm == "dct":
                        result = self.img_dct.encoder(img=image, message=input_text)
                        logging.info(f"Закодирован текст в изображение с помощью метода dct. Текст: {input_text}.")

                    elif algorithm == "neural":
                        result = self.image_neural.encode_image(img=image, text=input_text)
                        logging.info(f"Закодирован текст в изображение с помощью метода neural image. Текст: {input_text}.")
                    
                    temp_file = os.path.join(TEMP_DIR, "encoded_image.png")
                    result.save(temp_file)


                    image_b64 = image_to_img_src(result)
                    ctx["processed_image"] = image_b64
                    ctx["download_link"] = f"/download?file={temp_file}"
                    logging.info(f"Изображение успешно обработано и сохранено: {temp_file}")

                elif stego_type == "audio":
                    temp_file = os.path.join(TEMP_DIR, "encoded_audio.wav")
                    uploaded_file_content = uploaded_file.read()  # Преобразование в байты
                    with open(tmp_filename, "wb") as f:
                        f.write(uploaded_file_content)
                        logging.info(f"Загруженный аудиофайл сохранен в {tmp_filename}.")
                    
                    logging.info("Начата обработка аудиофайла с текстом.")

                    if algorithm == "lsb":
                        result = self.audio_lsb.embeded_message_audio(tmp_filename, input_text, temp_file)
                        logging.info(f"Аудиофайл закодирован с помощью LSB. {result=}")
                        with open(result, "rb") as wav_file:
                            audio_src = audio_to_src(wav_file, audio_format="wav")
                        ctx["processed_audio"] = audio_src
                        ctx["download_link"] = f"/download?file={temp_file}"
                        logging.info(f"Аудиофайл успешно обработан и сохранён: {temp_file}")

                    elif algorithm == "phase":
                        result = self.audio_phase.encode(tmp_filename, input_text)
                        logging.info(f"Аудиофайл закодирован с помощью PHASE. {result=}")
                        with open(result, "rb") as wav_file:
                            audio_src = audio_to_src(wav_file, audio_format="wav")
                        ctx["processed_audio"] = audio_src
                        ctx["download_link"] = f"/download?file={result}"
                        logging.info(f"Аудиофайл успешно обработан и сохранён: {result}")

                    elif algorithm == "neural":
                        result = self.audio_neural.encode(tmp_filename, input_text)
                        logging.info(f"Аудиофайл закодирован с помощью NEURAL. {result=}")
                        with open(result, "rb") as wav_file:
                            audio_src = audio_to_src(wav_file, audio_format="wav")
                        ctx["processed_audio"] = audio_src
                        ctx["download_link"] = f"/download?file={result}"
                        logging.info(f"Аудиофайл успешно обработан и сохранён: {result}")

                    else:
                        result = self.audio_lsb.embeded_message_audio(tmp_filename, input_text, temp_file)
                        logging.info(f"Аудиофайл закодирован с помощью default:LSB. {result=}")
                        with open(result, "rb") as wav_file:
                            audio_src = audio_to_src(wav_file, audio_format="wav")
                        ctx["processed_audio"] = audio_src
                        ctx["download_link"] = f"/download?file={temp_file}"
                        logging.info(f"Аудиофайл успешно обработан и сохранён: {temp_file}")

                    # with open(temp_file, "wb") as f:
                    #     f.write(result)
                    

            elif action == "decode":
                logging.info(f"Начата декодировка изображения. {action=}, {stego_type=}, {algorithm=}.")

                if stego_type == "image":

                    if algorithm == "lsb":
                        # РАБОТАЕТ
                        try: 
                            decoded_text = self.img_lsb.decode_image(image=open_image(uploaded_file))
                            ctx["decoded_text"] = decoded_text
                            logging.info(f"Изображение декодировано методом lsb. Текст: {decoded_text}")
                        except:
                            raise ValueError('Изображение какое-то странное... Похоже закодировано другим методом, попробуйте выбрать другой метод.')
                   
                    elif algorithm == "dct":
                        # РАБОТАЕТ
                        opened_img = open_image(uploaded_file)
                        logging.info(f'{opened_img.size=}')
                        decoded_text = self.img_dct.decoder(image=opened_img)
                        ctx["decoded_text"] = decoded_text
                        logging.info(f"Изображение декодировано методом dct. Текст: {decoded_text}")

                    elif algorithm == "neural":
                        # РАБОТАЕТ
                        opened_img = open_image(uploaded_file)
                        logging.info(f'{opened_img.size=}')
                        decoded_text = self.image_neural.decode_image(img=opened_img)
                        ctx["decoded_text"] = decoded_text
                        logging.info(f"Изображение декодировано методом neural. Текст: {decoded_text}")

                    else:
                        # НА ВСЯКИЙ СЛУЧАЙ
                        decoded_text = decode_image(uploaded_file, algorithm)
                        ctx["decoded_text"] = decoded_text
                        logging.info("Изображение декодировано методом default.")

                elif stego_type == "audio":
                    temp_file = os.path.join(TEMP_DIR, "encoded_audio.wav")
                    uploaded_file_content = uploaded_file.read()  # Преобразование в байты
                    with open(temp_file, "wb") as f:
                        f.write(uploaded_file_content)
                        logging.info(f"Загруженный аудиофайл сохранен в {temp_file}.")

                    logging.info("Начата обработка аудиофайла с закодированным текстом.")

                    if algorithm == "lsb":
                        # РАБОТАЕТ
                        decoded_text = self.audio_lsb.decode_audio(temp_file)
                        logging.info(f"Аудиофайл раскодирован с помощью LSB. {decoded_text=}")
                        ctx["decoded_text"] = decoded_text

                    elif algorithm == "phase":
                        # ПРОВЕРКА
                        logging.info(f'{temp_file=}')
                        logging.info(f'{Path(temp_file).exists()=}')
                        decoded_text = self.audio_phase.decode(temp_file)
                        logging.info(f"Аудиофайл раскодирован с помощью PHASE. {decoded_text=}")
                        ctx["decoded_text"] = decoded_text

                    elif algorithm == "neural":
                        # ПРОВЕРКА
                        decoded_text = self.audio_neural.decode()
                        logging.info(f"Аудиофайл раскодирован с помощью LSB. {decoded_text=}")
                        ctx["decoded_text"] = decoded_text

                    else:
                        # НА ВСЯКИЙ СЛУЧАЙ
                        decoded_text = decode_audio(uploaded_file, algorithm)
                        ctx["decoded_text"] = decoded_text
                        logging.info("Аудиофайл декодирован c помощью метода default:<не имплементировано>.")

        except Exception as err:
            error_message = f"Ошибка обработки файла: {err}"
            logging.error(error_message)
            ctx = {"error": error_message, "request": self.request}

        try:
            return render_template(self.template, self.request, ctx)
        except:
            ctx = {
                'error':(
                    'Изображение какое-то странное... Похоже закодировано другим методом, либо не содержит скрытого текста.'
                    'Попробуйте выбрать другой метод.'
                ),
                'request': self.request
                }
            return render_template(self.template, self.request, ctx)

async def download_file(request):
    file_path = request.query.get("file")
    if file_path and os.path.exists(file_path):
        logging.info(f"Запрос на скачивание файла: {file_path}")
        
        # Извлекаем имя файла из пути
        file_name = os.path.basename(file_path)
        
        # Возвращаем файл с указанием имени файла в заголовке Content-Disposition
        return FileResponse(file_path, headers={'Content-Disposition': f'attachment; filename={file_name}'})
    
    logging.error(f"Файл не найден: {file_path}")
    return Response(status=404, text="Файл не найден")
