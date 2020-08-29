#!/bin/sh

coverage run -m unittest discover
coverage report
coverage html
black --check canvasaio tests
flake8 canvasaio tests
mdl . .github
python scripts/alphabetic.py
python scripts/find_missing_kwargs.py
