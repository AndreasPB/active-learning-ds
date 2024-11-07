FROM python:3.10

WORKDIR /app

COPY ./requirements.txt /requirements.txt

RUN pip install --no-cache-dir --upgrade -r /requirements.txt

COPY . /app

CMD ["fastapi", "dev", "main.py", "--host", "0.0.0.0", "--port", "1337"]
