#!/usr/bin/env bash

#
# Echo functions for color output
#

Red="\033[1;31m"
Green="\033[0;32m"
Bold="\033[;1m"
Reset="\033[0;0m"

echo_error () {
   printf "\n${Bold}${Red}.. $1 ${Reset}\n"
}

echo_info () {
   printf "\n${Bold}${Green}=>${Reset}${Bold} $1 ${Reset}\n"
}

case "$1" in
        shell) 
            pipenv shell
        ;;
        edit) 
            pipenv run subl .
        ;;

        setup) 
            pipenv install --dev
        ;;
        *) echo "Use one of the following args: setup, run, shell, edit"
        ;;
esac



#
#            npx tailwindcss-cli@latest build --watch --jit -i ./src/tailwind.css -o ./application/static/style.build.css
#npx tailwindcss-cli@latest build -i ./src/tailwind.css -o ./application/static/style.build.css

