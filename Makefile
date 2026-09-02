WORDS ?= words.json
LANG ?= norwegian
OUT ?= generated.txt

.PHONY: install install-dev test run run-fake clean

install:
	uv sync

install-dev:
	uv sync --extra dev

test:
	uv run pytest tests/

run: export OUTPUT = $(OUT)
run:
	uv run python main.py $(WORDS) $(LANG)

run-fake: export OUTPUT = $(OUT)
run-fake:
	uv run python main.py $(WORDS) $(LANG) --fake

clean:
	find . -type d -name '__pycache__' -not -path './.venv/*' -exec rm -rf {} +
	rm -rf .pytest_cache src/anki_writer.egg-info
