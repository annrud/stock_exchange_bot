FROM python:3.12.3-alpine

WORKDIR /code

COPY ./requirements.txt ./

RUN set -eux \
    && python3.12 -m pip install --upgrade pip \
    && pip3 install -r ./requirements.txt

COPY ./app ./app
COPY ./alembic ./alembic
COPY ./main.py ./main.py
COPY ./alembic.ini ./alembic.ini
COPY ./local ./local

COPY entrypoint.sh ./

RUN chmod u+x ./entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
