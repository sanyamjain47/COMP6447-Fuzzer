#!/bin/sh
python3 -m pip install --user virtualenv
virtualenv venv
source venv/bin/activate
python3 -m pip install -r requirements.txt
