.PHONY: lint build push

DIRNAME = $(shell basename $(CURDIR))

lint:
	poetry run pylint $(shell git ls-files '*.py')

build:
	docker build -t harbor1.fisgeo.unipg.it/uninuvola/$(DIRNAME) .

push: build
	docker push harbor1.fisgeo.unipg.it/uninuvola/$(DIRNAME):latest 
