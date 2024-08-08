PYTHON = ./local-venv/bin/python3

run:
	${PYTHON} src/main.py

test-rss:
	${PYTHON} src/test-rss.py

.PHONY: run test-rss
