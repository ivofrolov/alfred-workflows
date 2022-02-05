workflows = currency-converter passphrase-generator wolfram-answers yandex-translate

py_sources = $(filter %.py,$(foreach dir,$(workflows),$(wildcard $(dir)/*)))

uppercase = $(shell echo $(1) | tr '[:lower:]' '[:upper:]')
workflow_uid_var = $(addsuffix _WORKFLOW_UID,$(call uppercase,$(subst -,_,$(1))))

$(workflows):
	if test -z "$(ALFRED_PREFERENCES_FOLDER)" ; then echo "ALFRED_PREFERENCES_FOLDER is not defined" ; exit 1 ; fi
	if test -z "$(value $(call workflow_uid_var,$@))" ; then echo "$(call workflow_uid_var,$@) is not defined" ; exit 1 ; fi
	rsync -h --update --executability \
		$(filter-out %.md, $(wildcard $@/*)) \
		"$(ALFRED_PREFERENCES_FOLDER)/workflows/$(value $(call workflow_uid_var,$@))/"

all: $(workflows) ## install workflows to Alfred directory

help: 
	# see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

format: ## format sources with black
	black -S $(py_sources)

lint:  ## lint codebase with flake8
	pylint --disable="C0326,C0330" --max-line-length=88 $(py_sources)

.PHONY .SILENT: help format lint all $(workflows)
.DEFAULT_GOAL := help
