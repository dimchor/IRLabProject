FROM python:3

WORKDIR /usr/src/app
VOLUME  /data
VOLUME /root/nltk_data

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]
