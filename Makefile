.PHONY: build validate deploy deploy-ci local-invoke local-api test clean \
        build-S3ProcessorFunction

# ── SAM targets ──────────────────────────────────────────────────────────────

build:
	sam build

validate:
	sam validate --lint

deploy: build
	sam deploy --guided

deploy-ci: build
	sam deploy

local-invoke: build
	sam local invoke S3ProcessorFunction --event events/s3-event.json

local-api:
	sam local start-api

# ── SAM makefile build hook (called by `sam build` for each function) ─────────
# ARTIFACTS_DIR is set by SAM to the staging directory for the function package.
# https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/building-custom-runtimes.html

build-S3ProcessorFunction:
	poetry export -f requirements.txt --without-hashes -o $(ARTIFACTS_DIR)/requirements.txt
	pip install -r $(ARTIFACTS_DIR)/requirements.txt -t $(ARTIFACTS_DIR) --quiet
	cp -r s3_notification_process $(ARTIFACTS_DIR)/
	cp -r src/handlers $(ARTIFACTS_DIR)/

# ── Development ───────────────────────────────────────────────────────────────

install:
	poetry install

test:
	poetry run pytest tests/unit/ -v --cov=src --cov-report=term-missing

clean:
	rm -rf .aws-sam/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -name "*.pyc" -delete
