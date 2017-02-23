FROM python:3-alpine
COPY . /usr/src/mimic
RUN pip install /usr/src/mimic
ENTRYPOINT [ "mimic" ]
