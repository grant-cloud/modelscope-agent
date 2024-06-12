#!/bin/bash

script_dir=$(dirname "$(readlink -f "$0")")
export PYTHONPATH=$PYTHONPATH:$script_dir
export STATIC_FOLDER=$script_dir/static
WORKERS=${CORES:-7}
HTTP_PORT=${HTTP_PORT:-8090}  # Default to 8090 if no PORT env variable is set
exec gunicorn -w $WORKERS -b 0.0.0.0:$HTTP_PORT main:app -k uvicorn.workers.UvicornWorker --timeout 600 --log-level=info --access-logfile=-