#!/bin/bash

curdir=$( cd `dirname $0` && pwd)
export PYTHONPATH="$curdir":"$PYTHONPATH"

cmd="$1"; shift

case "$cmd" in
	import)
		python3 bin/xigt-import.py "$@"
		;;
	export)
		python3 bin/xigt-export.py "$@"
		;;
	process)
		python3 bin/xigt-process.py "$@"
		;;
	query)
		python3 bin/xigt-query.py "$@"
		;;
	validate)
		python3 bin/xigt-validate.py "$@"
		;;
	*)
		echo "usage: xigt.sh (import|export|process|query|validate) OPTIONS"
		;;
esac