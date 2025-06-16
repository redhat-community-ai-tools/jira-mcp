.venv:
	python -m venv .venv

.PHONY: setup
setup: .venv
	.venv/bin/pip install -r requirements.txt
