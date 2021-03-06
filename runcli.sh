#!/bin/sh -e
cd `dirname $0`
if ! which python | grep -q "`pwd`"; then
  virtualenv venv -p python3 || true
fi
. venv/bin/activate
pip install -r requirements.txt --upgrade
python ChatClient $@
