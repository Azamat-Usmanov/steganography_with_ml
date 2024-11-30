import numpy as np
from PIL import Image
from scipy.fftpack import dct, idct


class ImageDCT:
    def __init__(self):
        pass

    def dct2(self, block):
        return dct(dct(block.T, norm='ortho').T, norm='ortho')

    def idct2(self, block):
        return idct(idct(block.T, norm='ortho').T, norm='ortho')

    def encoder(self, message, output_path=None, image_path=None, img=None):
        if img is None:
            image = Image.open(image_path)
            need_save = True
        else:
            image = img
            need_save = False
        image_data = np.array(image, dtype=np.uint8)

        blue_channel = image_data[:, :, 2]

        height, width = blue_channel.shape
        pad_height = int(8 * np.ceil(height/8))
        pad_width = int(8 * np.ceil(width/8))
        pad_blue_channel = np.pad(blue_channel, ((0, pad_height), (0, pad_width)), mode='constant')

        blocks = [
            pad_blue_channel[i:i + 8, j:j + 8]
            for i in range(0, pad_height, 8)
            for j in range(0, pad_width, 8)
        ]

        message_bits = ''.join(format(ord(char), '011b') for char in message)
        end_message = '00000000000'
        message_bits = message_bits + end_message
        
        # print(message_bits)
        # exit()
        bit_idx = 0
        P = 152
        for block_idx, block in enumerate(blocks):
            if bit_idx >= len(message_bits):
                break

            dct_block = self.dct2(block)
            # print(dct_block[4, 4])
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

            blocks[block_idx] = self.idct2(dct_block)

        embedded_image = np.zeros_like(pad_blue_channel)
        cnt = 0
        for i in range(0, height, 8):
            for j in range(0, width, 8):
                embedded_image[i:i + 8, j:j + 8] = blocks[cnt]
                cnt += 1

        embedded_image = embedded_image[:height, :width]

        image_data[:, :, 2] = embedded_image

        out_img = Image.fromarray(image_data)
        if need_save:
            out_img.save(output_path)
        else:
            return out_img

    def decoder(self, image_path=None, image=None):
        if image is None:
            if image_path is None:
                raise "Image is not received"
            image = Image.open(image_path)
        
        image_data = np.array(image, dtype=np.uint8)
        blue_channel = image_data[:, :, 2]
        
        height, width = blue_channel.shape
        pad_height = int(8 * np.ceil(height/8))
        pad_width = int(8 * np.ceil(width/8))
        pad_blue_channel = np.pad(blue_channel, ((0, pad_height), (0, pad_width)), mode='constant')

        blocks = [
            pad_blue_channel[i:i + 8, j:j + 8]
            for i in range(0, pad_height, 8)
            for j in range(0, pad_width, 8)
        ]

        message_bits = []
        end_message = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

        for block in blocks:
            
            dct_block = self.dct2(block)
            w1 = abs(dct_block[4, 4])
            w2 = abs(dct_block[4, 5])
            if w1 > w2:
                message_bits.append(0)
            elif w2 > w1:
                message_bits.append(1)

            if len(message_bits) >= 11:
                if message_bits[-11:] == end_message:
                    break

        message = ''.join(
            chr(int(''.join(map(str, message_bits[i:i + 11])), 2))
            for i in range(0, len(message_bits)-11, 11)
        )
        return message

if __name__ == '__main__':
    input_image = 'lenna.png'
    output_image = 'test.png'
    message = 'hello'

    image_dct = ImageDCT()

    image_dct.encoder(input_image, message, output_image)

    extracted_message = image_dct.decoder(output_image)
    print('Извлечённое сообщение:', extracted_message)