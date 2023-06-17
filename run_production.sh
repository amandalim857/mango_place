#!/usr/bin/env sh

gunicorn 'app:create_app()'
