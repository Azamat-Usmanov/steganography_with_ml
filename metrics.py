import skimage.measure as skmes
from skimage.metrics import structural_similarity as ssim
from PIL import Image
import numpy as np
import wave

class Metrics:
    # Подсчет энтропии
    @staticmethod
    def open_audio(path):
        with wave.open(path, 'r') as wf:
            num_channels = wf.getnchannels()
            sample_width = wf.getsampwidth()
            frame_rate = wf.getframerate()
            num_frames = wf.getnframes()
            
            # Читаем данные аудио
            audio_data = wf.readframes(num_frames)

        dt = np.dtype(f'int{8 * sample_width}')  # int16, int24, int32 в зависимости от sample_width
        audio_array = np.frombuffer(audio_data, dtype=dt)
        return audio_array

    @staticmethod
    def entropy(path):
        # Для музыки
        if path.endswith("wav"):
            audio_array = Metrics.open_audio(path)
            entropy = skmes.shannon_entropy(audio_array)
            return entropy
        else: # Для изображения
            img = Image.open(path)
            entropy = skmes.shannon_entropy(img)
            return entropy
    
    # Подсчет разности энтропии
    @staticmethod
    def diff_entropy(path1, path2):
        # Для аудио
        if path1.endswith("wav"):
            audio_array1 = Metrics.open_audio(path1)
            audio_array2 = Metrics.open_audio(path2)

            entropy1 = skmes.shannon_entropy(audio_array1)
            entropy2 = skmes.shannon_entropy(audio_array2)

            entropy_diff = abs(entropy2 - entropy1)

            return entropy_diff
        else: # Для изображения
            img1 = Image.open(path1)
            img2 = Image.open(path2)

            entropy1 = skmes.shannon_entropy(img1)
            entropy2 = skmes.shannon_entropy(img2)

            entropy_diff = abs(entropy2 - entropy1)

            return entropy_diff
    
    # Подсчет метрики SSIM (Только для изображений)
    @staticmethod
    def SSIM(path1, path2):
        img1 = Image.open(path1)
        img2 = Image.open(path2)

        img1 = np.array(img1)
        img2 = np.array(img2)

        ssima = ssim(img1, img2, channel_axis=0, win_size=3)
        return ssima
    

if __name__ == "__main__":

    metrics = Metrics()

    # Для изображений
    img_path1 = "image/cat.png"
    img_path2 = "image/output_image.png"
    print(f"Разница энтропий для изображений {metrics.diff_entropy(img_path1, img_path2):2f}")
    print(f"Энтропия до кодирования: {metrics.entropy(img_path1):2f} и после: {metrics.entropy(img_path2):2f}")
    print(f"SSIM изображений до кодирования и после: {metrics.SSIM(img_path1, img_path2):2f}")


    # Для аудио 
    audio_path1 = 'image/melodia.wav'
    audio_path2 = 'image/melodia_output.wav'
    print(f"Разница энтропий для аудио: {metrics.diff_entropy(audio_path1, audio_path2):2f}")
    print(f"Энтропия до кодирования: {metrics.entropy(audio_path1):2f} и после:{metrics.entropy(audio_path2):2f}")



