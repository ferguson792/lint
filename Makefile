PYTHON = ./local-venv/bin/python3

run:
	${PYTHON} src/main.py

sample-dummy:
	bin/lint sample/dummy

sample-detailed:
	bin/lint sample/detailed

test-rss:
	${PYTHON} src/test-rss.py

# build → builds the program and adds the version.py

# dist → same as <lint-version.zip>
# 

.PHONY: run test-rss sample-dummy
