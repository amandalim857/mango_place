#!/usr/bin/env sh

node_modules/.bin/webpack build --mode production
node_modules/.bin/sass static/scss:static/css
