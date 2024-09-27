PYTHON = ./local-venv/bin/python3

run:
	${PYTHON} src/main.py

run-sample-dummy:
	bin/lint sample/dummy

run-sample-detailed:
	bin/lint sample/detailed

test-rss:
	${PYTHON} src/test-rss.py

# build → builds the program and adds the version.py

# dist → same as <lint-version.zip>
# 

.PHONY: run test-rss run-sample-dummy run-sample-detailed
