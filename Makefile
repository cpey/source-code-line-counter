test:
	python3 -m unittest discover -s tests -v

clean:
	find . -name "*.pyc" -delete
	find . -name "__pycache__" -delete
