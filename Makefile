.PHONY: build upload

build:
	python setup.py sdist bdist_wheel

upload: build
	twine upload --skip-existing dist/*
