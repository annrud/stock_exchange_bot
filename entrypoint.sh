#! /bin/sh
python3.12 -m alembic upgrade head
exec python3.12 main.py
