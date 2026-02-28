#!/usr/bin/env bash
pip install code2logic --upgrade
code2logic ./ -f toon --compact --name project -o ./
source venv/bin/activate && python -m code2flow ./ -v -o ./output -m hybrid -f toon
source venv/bin/activate && python -m code2flow ./ -v -o ./output -m dynamic -f toon
source venv/bin/activate && python -m code2flow ./ -v -o ./output -m behavioral -f toon

# Validate TOON format only (since we're not generating YAML anymore)
echo "🔍 Validating TOON format..."
python3 validate_toon.py output/analysis.toon.yaml