FROM python:3.10-slim

WORKDIR /app

# Dependencies
COPY ./stego/frontend/requirements.txt .
RUN python -m pip install -r requirements.txt

RUN mkdir -p /app/stego/frontend

COPY setup.py .

RUN python -m pip install -e .

EXPOSE 8080

CMD ["python", "/app/stego/frontend/run.py"]
