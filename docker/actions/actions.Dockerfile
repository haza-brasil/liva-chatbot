FROM brenddongontijo/requirements:latest

ADD ./bot/actions /bot/actions
ADD ./bot/Makefile /bot/Makefile

WORKDIR bot/

EXPOSE 5055

CMD make run-actions