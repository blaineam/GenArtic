FROM python:3.7

ADD requirements.txt /

RUN pip install -r  /requirements.txt

ADD genartic.py /

ENV PYTHONUNBUFFERED=1

CMD [ "python", "./genartic.py" ]