import numpy as np
from PIL import Image, ImageDraw, ImageFont
import librosa
import librosa.display
import soundfile as sf
import matplotlib.pyplot as plt

# Constants
DEFAULT_FONT_PATH = "/Users/azamath/Library/Fonts/DejaVuSans-Bold.ttf"
DEFAULT_SAMPLE_RATE = 22050
HEIGHT = 256  # Высота изображения
MAX_FONT_SIZE = 50  # Максимальный размер шрифта
MARGIN = 10  # Отступы
CHAR_WIDTH_ESTIMATE = 20  # Примерная ширина одного символа
MIN_WIDTH = 512  # Минимальная ширина изображения

# Функция для создания изображения с текстом
# Функция для создания изображения с текстом
def text_to_image(text, height=HEIGHT, max_font_size=MAX_FONT_SIZE, margin=MARGIN):
    # Попытка загрузить шрифт
    try:
        font = ImageFont.truetype(DEFAULT_FONT_PATH, max_font_size)
    except IOError:
        font = ImageFont.load_default()

    # Используем getbbox для точной оценки ширины текста
    text_width = font.getbbox(text)[2] + 2 * margin
    image_width = max(MIN_WIDTH, text_width)  # Ширина изображения должна быть не меньше минимальной

    # Создание изображения
    image = Image.new("L", (image_width, height), "black")
    draw = ImageDraw.Draw(image)

    # Центрирование текста по высоте
    text_y = (height - max_font_size) // 2
    draw.text((margin, text_y), text, fill="white", font=font)

    return np.array(image)

# Преобразование изображения в аудио
def image_to_audio(image):
    flipped_image = np.flipud(image)
    S = flipped_image.astype(np.float32) / 255.0 * 100.0
    y = librosa.griffinlim(S)
    return y

# Основная функция
def text_to_audio_and_spectrogram(text):
    # Генерация изображения с текстом
    image = text_to_image(text)
    
    # Создание аудиофайла
    audio = image_to_audio(image)
    audio_filename = "output_audio.wav"
    sf.write(audio_filename, audio, DEFAULT_SAMPLE_RATE)
    
    # Создание и сохранение спектрограммы
    S = librosa.feature.melspectrogram(y=audio, sr=DEFAULT_SAMPLE_RATE)
    S_dB = librosa.power_to_db(S, ref=np.max)
    
    plt.figure(figsize=(image.shape[1] / 100, HEIGHT / 100))  # Масштабируем график под размер изображения
    librosa.display.specshow(S_dB, sr=DEFAULT_SAMPLE_RATE, x_axis='time', y_axis='mel', cmap='magma')
    plt.axis("off")
    plt.tight_layout(pad=0)
    spectrogram_filename = "output_spectrogram.png"
    plt.savefig(spectrogram_filename, bbox_inches="tight", pad_inches=0, transparent=True)
    plt.close()
    
    print(f"Audio saved to: {audio_filename}")
    print(f"Spectrogram saved to: {spectrogram_filename}")

# Ввод текста
if __name__ == "__main__":
    text = input("Enter text to convert to audio and spectrogram: ")
    text_to_audio_and_spectrogram(text)
