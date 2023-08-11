.PHONY: install test clean coverage

install: 
	pip install -e .

test:
	python -m unittest

coverage:
	coverage run --source=src -m unittest  
	coverage report
	coverage xml -o cov.xml 

clean:
	git clean -Xdf
