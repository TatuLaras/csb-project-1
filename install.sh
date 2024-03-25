#!/bin/bash

python3 manage.py migrate
python3 create_db.py
