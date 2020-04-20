.PHONY: docker

REQS := requirements.txt
# Used for colorizing output of echo messages
BLUE := "\\033[1\;36m"
NC := "\\033[0m" # No color/default

define PRINT_HELP_PYSCRIPT
import re, sys

for line in sys.stdin:
  match = re.match(r'^([a-zA-Z_-]+):.*?## (.*)$$', line)
  if match:
    target, help = match.groups()
    print("%-20s %s" % (target, help))
    endef

export PRINT_HELP_PYSCRIPT

help: 
	@python3 -c "$$PRINT_HELP_PYSCRIPT" < $(MAKEFILE_LIST)

clean: ## Cleanup all the things
	find . -name '*.pyc' | xargs rm -rf
	find . -name '__pycache__' | xargs rm -rf
	rm -rf myvenv
	rm -rf .tox/

dev: ## local dev/test environment
	@echo "Building test env with docker-compose"
	@if [ -f /.dockerenv ]; then echo "Don't run make docker inside docker container" && exit 1; fi;
	docker-compose -f docker/docker-compose.yml up asscan_dev
	@docker-compose -f docker/docker-compose.yml run asscan_dev /bin/bash

docker: ## build docker container for testing
	@echo "Building test env with docker-compose"
	@if [ -f /.dockerenv ]; then echo "Don't run make docker inside docker container" && exit 1; fi;
	docker-compose -f docker/docker-compose.yml up --build asscan

python: ## setup python3
	if [ -f $(REQS) ]; then python3 -m pip install -r$(REQS); fi

test: python ## run tests in container
	if [ -f 'python/requirements-test.txt' ]; then python3 -m pip install -rpython/requirements-test.txt; fi
	tox
