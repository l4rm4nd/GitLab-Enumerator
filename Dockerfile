FROM python:3.12.4-alpine
LABEL Maintainer="LRVT"

COPY requirements.txt gnum.py gitlab_versions.py /app/.
RUN pip3 install -r /app/requirements.txt

WORKDIR /app
ENTRYPOINT [ "python", "gnum.py"]

CMD [ "python", "gnum.py", "--help"]
