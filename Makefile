LINT_VERSION = 0.2.0-bleeding.0

PYTHON = python3

LOCAL_VENV = ./local-venv
LOCAL_PYTHON = $(LOCAL_VENV)/bin/python3
LOCAL_PIP = $(LOCAL_VENV)/bin/pip
MK_INT_DIR = mkdir -p
COPY = cp

LICENSE_FILE = LICENSE.txt

# Dependencies are installed in the local venv in the order given here:
DEPENDENCIES_A = result requests feedparser
DEPENDENCIES_U = sentence_transformers
DEPENDENCIES_B = matplotlib numpy scikit-learn
DEPENDENCIES_C = mistralai

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
run: build $(LOCAL_VENV)
	@echo command line arguments: $(filter-out $@,$(MAKECMDGOALS))
	$(LINT_LOCAL_PY) $(filter-out $@,$(MAKECMDGOALS))

run-sample-dummy: build $(LOCAL_VENV)
	$(LINT_LOCAL_PY) sample/dummy

run-sample-detailed: build $(LOCAL_VENV)
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

# Creates a local Python virtual environment (venv) and installs necessary dependencies
$(LOCAL_VENV):
	$(PYTHON) -m venv $(LOCAL_VENV)
	$(LOCAL_PIP) install $(DEPENDENCIES_A)
	$(LOCAL_PIP) install -U $(DEPENDENCIES_U)
	$(LOCAL_PIP) install $(DEPENDENCIES_B)
	$(LOCAL_PIP) install $(DEPENDENCIES_C)

purge-venv:
	rm -r $(LOCAL_VENV)

# Creates a copy to distribute, including the LICENSE.txt
dist: build
	$(MK_INT_DIR) $(BUILD_DIST_DIR)
	cd $(BUILD_DIR) && tar -czf ../$(BUILD_DIST_DIR)/lint-$(LINT_VERSION).tar.gz $(BIN_SUBDIR) ../$(LICENSE_FILE)

.PHONY: run test-rss run-sample-dummy run-sample-detailed build dist clean purge-venv
