black:
	black -l 88 geomeppy tests docs setup.py

reqs:
	pip-compile --upgrade --output-file ./requirements.txt ./requirements.in
	pip-compile --upgrade --output-file ./test-requirements.txt ./test-requirements.in
	pip-compile --upgrade --output-file ./docs/requirements.txt ./docs/requirements.in

mypy:
	mypy --ignore-missing-imports geomeppy

.PHONY: black reqs mypy
