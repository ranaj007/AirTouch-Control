# syntax=docker/dockerfile:1.7-labs

FROM node:22-alpine AS builder

WORKDIR /app

COPY airtouch_frontend .

RUN npm install turbo --global
RUN npm install

RUN turbo build


FROM python:3.11-alpine

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY --from=builder /app/dist /app/airtouch_frontend/dist

COPY *.py .

EXPOSE 5000

ENV PYTHONUNBUFFERED=1

CMD ["python", "airtouch_flask.py"]