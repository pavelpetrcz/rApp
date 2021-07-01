FROM python:3
LABEL description="pavelpetrcz/rApp"
RUN apt-get update && apt-get install -y python-pip
COPY requirements.txt ./
RUN pip install -r requirements.txt
RUN pip install df2gspread
COPY . /rApp
WORKDIR /rApp
CMD python ./app.py