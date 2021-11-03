#!/bin/sh

cd ~/jass-remote/

export FLASK_APP=player_service.py
export FLASK_ENV=development
flask run --host=0.0.0.0 --port=8888
