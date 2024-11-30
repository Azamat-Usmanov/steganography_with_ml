from PIL import Image
from typing import Optional


class ImageLSB:
    def __init__(self):
        pass

    def text_to_bin(self, text):
        """Преобразует текст в двоичный формат."""
        return ''.join(format(ord(i), '016b') for i in text)

    def encode_image(self, secret_text, output_path=None, image_path=None, input_img=None):
        """Кодирует текст в изображение."""
        if input_img is None:
            img = Image.open(image_path)
            output_as_image = False
        else:
            output_as_image = True
            img = input_img
        binary_secret_text = self.text_to_bin(secret_text) + '1111111111111110'  # Конец сообщения
        encoded_img = img.copy()
        data_index = 0

        if img.mode == "RGB":
            RGBA_index = 3
        elif img.mode == "RGBA":
            RGBA_index = 4

        for y in range(img.height):
            if data_index >= len(binary_secret_text):
                break
            for x in range(img.width):
                pixel = list(img.getpixel((x, y)))
                # Количество каналов
                for i in range(RGBA_index):  # RGBA каналы
                    if data_index < len(binary_secret_text):
                        # Заменяем LSB на бит из текста
                        pixel[i] = (pixel[i] & ~1) | int(binary_secret_text[data_index])
                        data_index += 1
                # Устанавливаем закодированный пиксель
                encoded_img.putpixel((x, y), tuple(pixel))

        if output_as_image:
            return encoded_img
        encoded_img.save(output_path)
        print(f"Текст успешно закодирован в {output_path}")

    def decode_image(self, image_path=None, image: Image = None):
        """Декодирует текст из изображения."""
        if image is None:
            img = Image.open(image_path)
        else:
            img = image
        binary_secret_text = ''

        if img.mode == "RGB":
            RGBA_index = 3
        elif img.mode == "RGBA":
            RGBA_index = 4
        
        for y in range(img.height):
            for x in range(img.width):
                pixel = img.getpixel((x, y))
                for i in range(RGBA_index):  # RGBA каналы
                    binary_secret_text += str(pixel[i] & 1)
        secret_text = ''
        for i in range(0, len(binary_secret_text), 16):
            byte = binary_secret_text[i:i+16]
            if byte == '1111111111111110':  # Конец сообщения
                break
            secret_text += chr(int(byte, 2))

        return secret_text

if __name__ == "__main__":

    # Путь к исходному изображению
    image_path = '/home/yaroslav/infdef/steganography_with_ml/stego/frontend/static/0.png'
    # Сообщение
    secret_text = 'хуй'
    # Путь к изображению с текстом
    output_path = '/home/yaroslav/infdef/steganography_with_ml/stego/frontend/static/output_image.png'
    img_lsb = ImageLSB()
    # Кодирование текста в изображение
    img_lsb.encode_image(image_path, secret_text, output_path)
    
    # Декодирование текста из изображения
    decoded_text = img_lsb.decode_image(output_path)
    print(f"Декодированный текст: {decoded_text}")
    