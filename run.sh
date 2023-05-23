#!/usr/bin/zsh

source .venv/bin/activate
export $(grep -v '^#' .env | xargs)
python3 new_bot.py
