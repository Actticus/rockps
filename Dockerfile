FROM python:3.10

WORKDIR /rockps
COPY . .
RUN pip3 install .[deploy]
