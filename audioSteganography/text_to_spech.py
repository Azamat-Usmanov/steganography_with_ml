from gtts import gTTS
import whisper
from pydub import AudioSegment

def text_to_speech():
    # Запрашиваем ввод текста
    text = input("Введите секретный текст: ")
    
    # Указываем язык (например, 'ru' для русского, 'en' для английского)
    language = "ru" if text[0].lower() in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" else "en"
    
    try:
        # Преобразуем текст в речь
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Сохраняем аудиофайл
        secret = 'input_secret.wav'
        tts.save(secret)
        audio = AudioSegment.from_file(secret)
        audio.export(secret, format="wav")
        
        # print("Голосовое сообщение сохранено.")
        return secret
    except Exception as e:
        print(f"Произошла ошибка: {e}")

# def speech_to_text(file_name):
#     # Загружаем модель Whisper
#     model = whisper.load_model("medium")

#     # Распознаем речь с помощью Whisper
#     result = model.transcribe(file_name)

#     # Текст, полученный от Whisper
#     recognized_text = result['text']

#     # Выводим распознанный текст
#     print("Recognized Text:", recognized_text)

# speech_to_text('sss.wav')
# text_to_speech('vlad.wav')