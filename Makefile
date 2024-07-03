workflows = $(shell find workflows -type d -depth 1 -not -name ".*")

py_sources = $(filter %.py,$(foreach dir,$(workflows),$(wildcard $(dir)/*)))

changelog = CHANGELOG.md

uppercase = $(shell echo $(1) | tr '[:lower:]' '[:upper:]')
workflow_uid_var = $(addsuffix _WORKFLOW_UID,$(call uppercase,$(subst -,_,$(notdir $(1)))))

$(workflows):
	if test -z "$(ALFRED_PREFERENCES_FOLDER)" ; then echo "ALFRED_PREFERENCES_FOLDER is not defined" ; exit 1 ; fi
	if test -z "$(value $(call workflow_uid_var,$@))" ; then echo "$(call workflow_uid_var,$@) is not defined" ; exit 1 ; fi
	rsync -h --update --executability \
		$(filter-out %.md, $(wildcard $@/*)) \
		"$(ALFRED_PREFERENCES_FOLDER)/workflows/$(value $(call workflow_uid_var,$@))/"

all: $(workflows)  ## install workflows to Alfred directory

prepare:  ## bump version
	$(eval tmpfile = $(shell mktemp -t `basename $(changelog)`))
	awk -f prepare-changelog-for-release.awk $(changelog) > $(tmpfile)
	mv $(tmpfile) $(changelog)

release: prepare  ## publish release
	$(eval tag = $(shell head -1 $(changelog) | tr -d "# "))
	git add $(changelog) && git commit -m "Releases $(tag)" && git push
	awk "/# v[0-9]+/ && NR == 1 {next} /# v[0-9]+/ {exit} {print}" $(changelog) \
		| gh release create -F - $(tag) assets/*.alfredworkflow

format: ## format sources with black
	ruff format $(py_sources)

lint:  ## lint codebase with ruff
	ruff check --output-format pylint $(py_sources)

help: 
	# see https://marmelab.com/blog/2016/02/29/auto-documented-makefile.html
	grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "%-10s %s\n", $$1, $$2}'

.PHONY .SILENT: help format lint prepare release all $(workflows)
.DEFAULT_GOAL := help
