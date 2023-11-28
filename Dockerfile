FROM python:3.9.7-slim

WORKDIR /yt_bot_py

COPY requirements.txt /yt_bot_py/

RUN pip install -r requirements.txt

ENV TZ=Europe/Moscow

RUN cp /usr/share/zoneinfo/$TZ /etc/localtime

COPY bot.py /yt_bot_py/
COPY functions.py /yt_bot_py/

ENTRYPOINT ["python3"]

CMD ["bot.py"]
