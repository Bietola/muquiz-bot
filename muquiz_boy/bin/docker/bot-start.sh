#!/bin/sh

REP="$(git rev-parse --show-toplevel)"

cd "$REP/muquiz_boy"
# poetry install
poetry run python main.py
cd -
