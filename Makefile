VENV := .venv
PYTHON := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

WORDS ?= words.json
LANG ?= norwegian
OUT ?= generated.txt

.PHONY: install install-dev test run run-fake clean

install:
	$(PIP) install -e .

install-dev:
	$(PIP) install -e ".[dev]"

test:
	$(PYTHON) -m pytest tests/

run:
	$(PYTHON) main.py $(WORDS) $(LANG) -o $(OUT)

run-fake:
	$(PYTHON) main.py $(WORDS) $(LANG) -o $(OUT) --fake

clean:
	find . -type d -name '__pycache__' -not -path './$(VENV)/*' -exec rm -rf {} +
	rm -rf .pytest_cache src/anki_writer.egg-info
