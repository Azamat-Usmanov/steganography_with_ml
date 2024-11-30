from gtts import gTTS
from pydub import AudioSegment

def text_to_speech(secret, text):
    # Указываем язык (например, 'ru' для русского, 'en' для английского)
    language = "ru" if text[0].lower() in "абвгдеёжзийклмнопрстуфхцчшщъыьэюя" else "en"
    
    try:
        # Преобразуем текст в речь
        tts = gTTS(text=text, lang=language, slow=False)
        
        # Сохраняем аудиофайл
        tts.save(secret)
        audio = AudioSegment.from_file(secret)
        audio.export(secret, format="wav")        
    except Exception as e:
        print(f"Произошла ошибка: {e}")