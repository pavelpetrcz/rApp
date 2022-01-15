FROM python:3
LABEL description="pavelpetrcz/rApp"
RUN apt-get update && apt-get install -y python3-pip
COPY requirements.txt ./
RUN pip install -r requirements.txt
COPY . /rApp
WORKDIR /rApp
CMD python ./app.py