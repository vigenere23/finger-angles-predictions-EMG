#!/bin/sh

echo "Checking formatting with black..."
poetry run black --check .

echo "Checking formatting with flake8..."
poetry run flake8 .

echo "Checking typing with mypy..."
poetry run mypy
