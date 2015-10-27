FROM python:2
COPY . /usr/src/mimic
RUN pip install /usr/src/mimic
ENTRYPOINT [ "mimic" ]
