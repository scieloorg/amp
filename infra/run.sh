#!/bin/sh -e
# Run the server
: ${AMP_HOST:=0.0.0.0}
: ${AMP_PORT:=8000}
python -umsanic main.app --host="$AMP_HOST" --port="$AMP_PORT"
