import wave
import numpy as np
from pydub import AudioSegment



def text_to_bin(text):
    """Преобразует текст в двоичный формат."""
    return ''.join(format(ord(i), '016b') for i in text)


# Функция кодирования сообщения 
def embeded_message_audio(input, message, output):


    # Считываем аудио
    with wave.open(input, 'r') as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_rate = wf.getframerate()
        num_frames = wf.getnframes()
        
        # Читаем данные аудио
        audio_data = wf.readframes(num_frames)

    # Преобразуем аудиоданные в массив NumPy
    dt = np.dtype(f'int{8 * sample_width}')  # int16, int24, int32 в зависимости от sample_width
    audio_array = np.frombuffer(audio_data, dtype=dt)
    audio_array_output = audio_array.copy()


    # Кодируем сообщение
    binary_message = text_to_bin(message) + '1111111111111110'
    mess_index = 0
    for ampl, index_ampl in enumerate(audio_array):
        if mess_index >= len(binary_message):
            break
        if mess_index < len(binary_message):
                audio_array_output[ampl] = (audio_array_output[ampl] & ~1) | int(binary_message[mess_index])
                mess_index +=1


    if input[-3:] == 'mp3':
        audio_data = audio_array_output.tobytes()
        audio_segment = AudioSegment(
            data=audio_data,
            sample_width=sample_width,
            frame_rate=frame_rate,
            channels=num_channels
        )
        audio_segment.export(output, format="mp3", bitrate="192k")
    else:
        # Сохраняем аудио
        with wave.open(output, 'w') as wf:
            wf.setnchannels(num_channels)
            wf.setsampwidth(sample_width)
            wf.setframerate(frame_rate)
            wf.writeframes(audio_array_output)
            print(f'Аудио сохранено в: "{output}"')
    

# Функция декодирования сообщения
def decode_audio(output):

    # Cчитываем аудио
    with wave.open(output, 'r') as wf:
        num_channels = wf.getnchannels()
        sample_width = wf.getsampwidth()
        frame_rate = wf.getframerate()
        num_frames = wf.getnframes()
        audio_data = wf.readframes(num_frames)

    dt = np.dtype(f'int{8 * sample_width}')  # int16, int24, int32 в зависимости от sample_width
    audio_array = np.frombuffer(audio_data, dtype=dt)

    # Получаем сообщение
    binary_secret_text = ''
    for i in range(len(audio_array)):
        binary_secret_text += str(audio_array[i] & 1)

    

    # Разделяем двоичное сообщение на символы
    secret_text = ''
    for i in range(0, len(binary_secret_text), 16):
        byte = binary_secret_text[i:i+16]
        if byte == '1111111111111110':  # Конец сообщения
            break
        secret_text += chr(int(byte, 2))

    return secret_text


if __name__ == '__main__':

    # Начальные данные
    input = 'audio/melodia.wav'
    message = 'Hello'
    output = 'audio/melodia_output.wav'

    # Кодируем сообщение
    embeded_message_audio(input, message, output)

    # Декодируем сообщение
    decoded_text = decode_audio(output)
    print(f"Декодированный текст: {decoded_text}")







    
