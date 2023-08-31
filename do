#!/usr/bin/env bash

case "$1" in
        shell) 
            pipenv shell
        ;;
        edit) 
            pipenv run $EDITOR .
        ;;
        setup) 
            pipenv install --dev
        ;;
        build)
            rm -rf build
            rm -rf dist
            python setup.py sdist bdist_wheel
        ;;
        distribute)
            twine upload dist/*
        ;;
        *) echo "Use one of the following args: shell, edit, setup, build and distribute"
        ;;
esac