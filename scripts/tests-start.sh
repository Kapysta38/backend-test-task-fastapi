#! /usr/bin/env bash
set -e
set -x

export TESTING=1

python app/backend_pre_start.py

bash scripts/test.sh "$@"
