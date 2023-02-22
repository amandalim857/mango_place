#!/usr/bin/env sh

node_modules/.bin/webpack build --mode development
node_modules/.bin/sass static/scss:static/css
