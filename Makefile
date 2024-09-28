LINT_VERSION = 0.2.0-bleeding.0

LOCAL_PYTHON = ./local-venv/bin/python3
MK_INT_DIR = mkdir -p
COPY = cp

SRC_DIR = src
BUILD_DIR = build
BUILD_SRC_DIR = $(BUILD_DIR)/$(SRC_DIR)

SRCS = $(shell find $(SRC_DIR) -type f -name '*.py')	# See: https://unix.stackexchange.com/questions/479349/find-files-in-specific-directories
OBJS = $(addprefix build/,$(SRCS))

VERSION_FILE_PY = $(BUILD_SRC_DIR)/lint/version.py

run: build local-env
	$(LOCAL_PYTHON) $(BUILD_SRC_DIR)/main.py

run-sample-dummy:
	bin/lint sample/dummy

run-sample-detailed:
	bin/lint sample/detailed

# build also generates a version file
build: $(OBJS)
	echo "LINT_VERSION='$(LINT_VERSION)'" > $(VERSION_FILE_PY)

$(BUILD_SRC_DIR)/%.py: $(SRC_DIR)/%.py
	$(MK_INT_DIR) $(dir $@)
	$(COPY) $^ $@

clean:
	rm -r ${BUILD_DIR}

local-env:
	# TODO Create local build environment (under .local-venv)

# build → builds the program and adds the version.py

# dist → same as <lint-version.zip>
# 

.PHONY: run test-rss run-sample-dummy run-sample-detailed clean local-env
