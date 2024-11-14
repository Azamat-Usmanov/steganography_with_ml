# Используем образ Python 3.7 slim, основанный на Debian
FROM python:3.7-bookworm

# Устанавливаем pip
# Копируем requirements.txt в контейнер
COPY requirements.txt /mnt/requirements.txt

# Устанавливаем зависимости из requirements.txt
RUN pip3 install --break-system-packages -r /mnt/requirements.txt

# Устанавливаем рабочую директорию
WORKDIR /mnt

# Открываем bash, если необходимо (по умолчанию при запуске)
CMD [ "bash" ]
