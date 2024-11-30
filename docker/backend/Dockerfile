# Используем образ Python 3.7 slim, основанный на Debian
FROM python:3.7-bookworm

# Установка необходимых системных пакетов
RUN apt-get update && apt-get install -y \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Устанавливаем рабочую директорию
WORKDIR /mnt/neural_image
COPY requirements.txt /mnt/requirements.txt


# Устанавливаем зависимости из requirements.txt (если файл находится на хосте)
RUN pip3 install --break-system-packages -r /mnt/requirements.txt

# Команда для запуска приложения
CMD ["python", "app.py"]
