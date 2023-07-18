#!/bin/bash
git pull origin main
PWD=`pwd`
. $PWD/venv/bin/activate
cd ..
pip install -r requirements.txt
