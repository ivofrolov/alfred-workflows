SOURCES=currency-converter/ passphrase-generator/ wolfram-answers/ yandex-translate/

help: 
	# see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

format: ## format sources with black
	black -S $(SOURCES)

lint:  ## lint codebase with flake8
	pylint --disable="C0326,C0330" --max-line-length=88 $(SOURCES)

.PHONY .SILENT: help format lint
.DEFAULT_GOAL := help
