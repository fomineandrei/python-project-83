#!/usr/bin/env bash

curl -LsSf https://astral.sh/uv/install.sh | sh
source $HOME/hexlet/python-project-83/.env
make install && psql -a -d $DATABASE_URL -f database.sql