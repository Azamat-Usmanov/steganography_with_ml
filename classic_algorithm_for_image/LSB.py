from PIL import Image

def text_to_bin(text):
    """Преобразует текст в двоичный формат, поддерживая символы разных языков."""
    return ''.join(format(ord(i), '016b') for i in text)

def encode_image(image_path, secret_text, output_path):
    """Кодирует текст в изображение."""
    binary_secret_text = text_to_bin(secret_text) + '1111111111111110'  # Конец сообщения
    img = Image.open(image_path)
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
            for i in range(RGBA_index):  # RGB или RGBA каналы
                if data_index < len(binary_secret_text):
                    # Заменяем LSB на бит из текста
                    pixel[i] = (pixel[i] & ~1) | int(binary_secret_text[data_index])
                    data_index += 1
            # Устанавливаем закодированный пиксель
            encoded_img.putpixel((x, y), tuple(pixel))

    # Сохраняем изображение
    encoded_img.save(output_path)
    print(f"Текст успешно закодирован в {output_path}")

def decode_image(image_path):
    """Декодирует текст из изображения."""
    img = Image.open(image_path)
    binary_secret_text = ''

    if img.mode == "RGB":
        RGBA_index = 3
    elif img.mode == "RGBA":
        RGBA_index = 4

    for y in range(img.height):
        for x in range(img.width):
            pixel = img.getpixel((x, y))
            for i in range(RGBA_index):  # RGB или RGBA каналы
                binary_secret_text += str(pixel[i] & 1)

    # Разделяем двоичное сообщение на символы по 16 бит
    secret_text = ''
    for i in range(0, len(binary_secret_text), 16):
        byte = binary_secret_text[i:i+16]
        if byte == '1111111111111110':  # Конец сообщения
            break
        secret_text += chr(int(byte, 2))

    return secret_text

# Пример использования
if __name__ == "__main__":

    # Путь к исходному изображению
    image_path = 'cat.png'
    # Сообщение
    secret_text = 'x'*int(1562500)#int(6250000)
    # Путь к изображению с текстом
    output_path = 'output_image.png'
    # Кодирование текста в изображение
    encode_image(image_path, secret_text, output_path)
    
    # Декодирование текста из изображения
    decoded_text = decode_image('output_image.png')
    print(f'{(secret_text == decoded_text)=}')
    # print(f"Декодированный текст: {decoded_text}")

# количество пикселей на букву = 16 / n_channels
# максимальное количество букв = n*m / (16 / n_channels)