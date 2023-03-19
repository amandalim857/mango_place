#!/usr/bin/env bash

node_modules/.bin/webpack build --mode development --watch &
node_modules/.bin/sass --watch static/scss:static/css &

FLASK_DEBUG=true flask run

# Terminate webpack and sass when `flask run` exits
# https://stackoverflow.com/a/2173421
trap 'kill "$(jobs -p)" 2> /dev/null' SIGINT SIGTERM EXIT
