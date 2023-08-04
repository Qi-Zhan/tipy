.PHONY: refresh build install release test clean

refresh: clean build install

build:
	python -m build

install: build
	pip install dist/*.whl

release:
	python -m twine upload dist/*

test:
	python -m unittest

clean:
	rm -rf __pycache__
	rm -rf tests/__pycache__
	rm -rf src/watchyourself/__pycache__
	rm -rf dist
	rm -rf src/watchyourself.egg-info
	pip uninstall -y watchyourself
