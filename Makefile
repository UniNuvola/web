.SHELL := /bin/bash
EXENAME = server

$(EXENAME): $(shell find ./ -type f -name '*.go')
	go build -o $(EXENAME) cmd/main.go

run: $(EXENAME)
	./$(EXENAME)

.PHONY: watch
watch:
	reflex -s -r '\.go$$' make run
