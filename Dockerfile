FROM python:3.8.2-alpine

WORKDIR /code

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update
RUN pip install --upgrade pip
ADD ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

ADD . /code

RUN export FLASK_APP=task_4bill.py
RUN export FLASK_ENV=development
CMD ["flask", "run", "--host=0.0.0.0", "--port=5000"]