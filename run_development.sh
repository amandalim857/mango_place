#!/usr/bin/env bash

node_modules/.bin/webpack build --mode development --watch > /dev/null &
node_modules/.bin/sass --watch static/scss:static/css > /dev/null &

FLASK_DEBUG=true flask run

# Terminate webpack and sass when `flask run` exits
# https://stackoverflow.com/a/2173421
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT
