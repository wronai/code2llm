#!/usr/bin/env bash
pip install code2logic --upgrade
code2logic ./ -f toon --compact --name project -o ./
code2flow ./ -v -o ./output -m hybrid
code2flow ./ -v -o ./output -m dynamic
code2flow ./ -v -o ./output -m behavioral