.PHONY: all environment install install-mac install-linux install-windows auto-lint validate test test-example coverage coverage-html coverage-xml coverage-erase generate-sample-data

CODE_COVERAGE ?= 90
OS ?= $(shell python -c 'import platform; print(platform.system())')
IS_64_BIT ?= $(shell python -c 'from sys import maxsize; print(maxsize > 2**32)')

all: environment install validate test

environment:
	@echo 🔧 PIPENV SETUP
	pip3 install pipenv
	pipenv install --dev

install:
	@echo 📦 Install Module
	@echo Operating System identified as $(OS)
ifeq ($(OS), Linux)
	make install-linux
endif
ifeq ($(OS), Darwin)
	make install-mac
endif
ifeq ($(OS), Windows)
	make install-windows
endif
ifeq ($(OS), Windows_NT)
	make install-windows
endif

install-mac:
	@echo 🍎 MACOS INSTALL
# install module
	pipenv run python -m pip install -e .

install-linux:
	@echo 🐧 LINUX INSTALL
# install module
	pipenv run python -m pip install -e .

install-windows:
	@echo 🏁 WINDOWS INSTALL

validate: 
	@echo ✅ VALIDATE
	@pipenv run python -c 'import shoe_backtest; print(shoe_backtest.__package__ + " successfully imported")'

script:
	pipenv run python scripts/$(SCRIPT_NAME) $(ARGS)

test:
	@echo ✅ ALL TESTS
	@date -u
	pipenv run pytest tests -s
	$(MAKE) coverage
