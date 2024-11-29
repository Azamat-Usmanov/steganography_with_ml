import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct

def dct2(block):
    return dct(dct(block.T, norm='ortho').T, norm='ortho')

def idct2(block):
    return idct(idct(block.T, norm='ortho').T, norm='ortho')

def encoder(image_path, message, output_path):
    image = Image.open(image_path)
    image_data = np.array(image, dtype=np.uint8)

    blue_channel = image_data[:, :, 2]

    height, width = blue_channel.shape
    blocks = [
        blue_channel[i:i + 8, j:j + 8]
        for i in range(0, height, 8)
        for j in range(0, width, 8)
    ]

    message_bits = ''.join(format(ord(char), '011b') for char in message)
    bit_idx = 0
    P = 25
    for block_idx, block in enumerate(blocks):
        if bit_idx >= len(message_bits):
            break

        dct_block = dct2(block)
        w1 = abs(dct_block[4, 4])
        w2 = abs(dct_block[4, 5])
        if w1 >= 0:
            z1 = 1
        else:
            z1 = -1
        if w2 >= 0:
            z2 = 1
        else:
            z2 = -1

        if message_bits[bit_idx] == '0':
            if w1 - w2 <= P:
                w1 = P + w2 + 1
        else:
            if w1 - w2 >= -P:
                w2 = P + w1 + 1
        dct_block[4, 4] = z1 * w1
        dct_block[4, 5] = z2 * w2
        bit_idx += 1

        blocks[block_idx] = idct2(dct_block)

    embedded_image = np.zeros_like(blue_channel)
    cnt = 0
    for i in range(0, height, 8):
        for j in range(0, width, 8):
            embedded_image[i:i + 8, j:j + 8] = blocks[cnt]
            cnt += 1

    image_data[:, :, 2] = embedded_image

    Image.fromarray(image_data).save(output_path)

def decoder(image_path, message_length):
    image = Image.open(image_path)
    image_data = np.array(image, dtype=np.uint8)
    blue_channel = image_data[:, :, 2]
    
    height, width = blue_channel.shape
    blocks = [
        blue_channel[i:i + 8, j:j + 8]
        for i in range(0, height, 8)
        for j in range(0, width, 8)
    ]

    message_bits = []

    for block in blocks:
        if len(message_bits) >= message_length * 11:
            break

        dct_block = dct2(block)
        w1 = abs(dct_block[4, 4])
        w2 = abs(dct_block[4, 5])
        if w1 > w2:
            message_bits.append(0)
        elif w2 > w1:
            message_bits.append(1)

    message_bits = message_bits[:message_length * 11]
    message = ''.join(
        chr(int(''.join(map(str, message_bits[i:i + 11])), 2))
        for i in range(0, len(message_bits), 11)
    )
    return message

input_image = 'lenna.png'
output_image = 'test.png'
message = 'хуй'

encoder(input_image, message, output_image)

extracted_message = decoder(output_image, len(message))
print('Извлечённое сообщение:', extracted_message)
