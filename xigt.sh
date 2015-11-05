#!/bin/bash

curdir=$( cd `dirname $0` && pwd)
export PYTHONPATH="$curdir":"$PYTHONPATH"
python xigt/main.py "$@"

