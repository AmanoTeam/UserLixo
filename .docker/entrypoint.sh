#!/usr/bin/env bash

cd /usr/src/userlixo;
sed '/-e/d' requirements.lock > _requirements.txt && pip install -r _requirements.txt;
rm _requirements.txt;

find . -type d -wholename "./userlixo/plugins/*/venv" | xargs rm -rf
find . -type f -wholename "./userlixo/plugins/*/requirements.txt" | xargs rm

python3 -m userlixo
