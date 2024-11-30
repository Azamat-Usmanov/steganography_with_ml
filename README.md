# Steganography
# Схема работы
1. в контейнере docker/backend (python3.7) на flask хостится отдельно нейросеть для кодирования текста в изображения
2. всё остальное решение хостится в контейнере docker/frontend (python3.10) с помощью aiohttp
3. связь между контейнерами через docker network

# Содержание:
1. папка `docker` - докерфайлы
2. папка `stego` - весь код проекта
3. папка `stego/backend` - реализация нейронной сети для кодирования текста в изображения
4. папка `stego/frontend` - реализация остальных алгоритмов вместе с сервером

P.S: не обращайте внимания на названия "backend" и "frontend". Смысла в этом мало. Так было изначально запланировано, а потом уже стало сложно переименовать :)

# Установка:
```
git clone https://github.com/Azamat-Usmanov/steganography_with_ml.git
cd steganography_with_ml
docker compose up
```
