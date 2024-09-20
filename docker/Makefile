include buildinfo.mk

.PHONY: all
all: check build push tag

.PHONY: check
check:
ifeq ($(IMAGE),)
    $(error "Missing IMAGE")
endif
ifeq ($(DEPLOYED),)
    $(error "Missing DEPLOYED")
endif

.PHONY: build
build: check
	cd .. && docker build -t $(IMAGE):$(shell date +%Y-%m-%d) -f docker/Dockerfile .

.PHONY: push
push: check
	docker push $(IMAGE):$(shell date +%Y-%m-%d)
	docker tag $(IMAGE):$(shell date +%Y-%m-%d) $(IMAGE):latest
	docker push $(IMAGE):latest

.PHONY: tag
tag: check
	docker tag $(IMAGE):$(DEPLOYED) $(IMAGE):deployed
	docker push $(IMAGE):deployed
