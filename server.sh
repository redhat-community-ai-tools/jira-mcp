#!/usr/bin/env bash

THIS_DIR=$(dirname "$0")
PYTHON=$THIS_DIR/.venv/bin/python
$PYTHON $THIS_DIR/server.py
