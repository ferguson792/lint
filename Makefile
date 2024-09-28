LINT_VERSION = 0.2.0-bleeding.0

LOCAL_PYTHON = ./local-venv/bin/python3
MK_INT_DIR = mkdir -p
COPY = cp

SRC_DIR = src
BUILD_DIR = build
BUILD_DIST_DIR = $(BUILD_DIR)/dist
BIN_SUBDIR=bin
BUILD_BIN_DIR = $(BUILD_DIR)/$(BIN_SUBDIR)
BUILD_SRC_PREFIX = py-
BUILD_SRC_DIR = $(BUILD_BIN_DIR)/$(BUILD_SRC_PREFIX)$(SRC_DIR)

SRCS = $(shell find $(SRC_DIR) -type f -name '*.py')	# See: https://unix.stackexchange.com/questions/479349/find-files-in-specific-directories
OBJS = $(addprefix $(BUILD_BIN_DIR)/$(BUILD_SRC_PREFIX),$(SRCS))

VERSION_FILE_PY = $(BUILD_SRC_DIR)/lint/version.py
EXEC_FILE = $(BUILD_BIN_DIR)/lint

# The code for the executable file
define EXEC_CODE
#!/bin/bash

python3 "$$(dirname "$$0")/$(BUILD_SRC_PREFIX)$(SRC_DIR)/main.py"
endef

export EXEC_CODE	# So it is visible in shell; see: https://stackoverflow.com/questions/649246/is-it-possible-to-create-a-multi-line-string-variable-in-a-makefile

LINT_LOCAL_PY = $(LOCAL_PYTHON) $(BUILD_SRC_DIR)/main.py

# See: https://stackoverflow.com/questions/6273608/how-to-pass-argument-to-makefile-from-command-line
run: build local-env
	@echo command line arguments: $(filter-out $@,$(MAKECMDGOALS))
	$(LINT_LOCAL_PY) $(filter-out $@,$(MAKECMDGOALS))

run-sample-dummy: build local-env
	$(LINT_LOCAL_PY) sample/dummy

run-sample-detailed: build local-env
	$(LINT_LOCAL_PY) sample/detailed

# build also generates a version file
# and executable file
build: $(OBJS)
	echo "LINT_VERSION='$(LINT_VERSION)'" > $(VERSION_FILE_PY)
	echo "$$EXEC_CODE" > $(EXEC_FILE)
	chmod +x $(EXEC_FILE)

$(BUILD_SRC_DIR)/%.py: $(SRC_DIR)/%.py
	$(MK_INT_DIR) $(dir $@)
	$(COPY) $^ $@

clean:
	rm -r ${BUILD_DIR}

local-env:
	# TODO Create local build environment (under .local-venv)

dist: build
	$(MK_INT_DIR) $(BUILD_DIST_DIR)
	cd $(BUILD_DIR) && tar -czf ../$(BUILD_DIST_DIR)/lint-$(LINT_VERSION).tar.gz $(BIN_SUBDIR)

.PHONY: run test-rss run-sample-dummy run-sample-detailed build dist clean local-env
