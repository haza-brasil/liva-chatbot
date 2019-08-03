FROM requirements:latest

COPY ./bot /bot
COPY ./scripts /scripts

WORKDIR /bot

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf