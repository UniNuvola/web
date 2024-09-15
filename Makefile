.PHONY: lint build push

DIRNAME = $(shell basename $(CURDIR))

lint:
	poetry run pylint $(shell git ls-files '*.py')

build:
	# harbor1.fisgeo.unipg.it/uninuvola/$(DIRNAME)
	docker build -t $(DIRNAME) .

push: build
	docker push harbor1.fisgeo.unipg.it/uninuvola/$(DIRNAME):latest 
