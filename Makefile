.PHONY: install test clean

install: 
	pip install -e .

test:
	python -m unittest

clean:
	git clean -Xdf
