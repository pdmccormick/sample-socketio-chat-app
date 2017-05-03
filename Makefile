.PHONY: run pip-freeze

run:
	python chatapp.py

pip-freeze:
	pip freeze | grep -v -E '(pkg-resources|^-e )' | sort -g | tee requirements.pip
