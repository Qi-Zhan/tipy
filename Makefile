.PHONY: install test clean

install: 
	pip install -e .

test:
	python -m unittest

clean:
	rm -rf **__pycache__**
	rm -rf src/tipy/__pycache__
	rm -rf src/tipy.egg-info
