FROM brenddongontijo/requirements:latest

COPY ./bot /bot
COPY ./scripts /scripts

WORKDIR /bot

EXPOSE 5005

RUN python -m spacy download pt_core_news_sm
RUN python -m spacy link pt_core_news_sm pt

RUN find . | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

CMD make rasa-run-facebook