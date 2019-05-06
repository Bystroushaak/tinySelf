.PHONY: all docker_build

all: run

docker_build:
	mkdir -p build
	mkdir -p release
	chmod 777 build
	chmod 777 release
	docker build -t tinyself_ubuntu .

run: docker_build
	docker run -ti --rm \
		-e EXTRA_ARGS="-O 3" \
		-e DISPLAY=$DISPLAY \
		-e LC_CTYPE=en_US.UTF-8 \
		-v $(shell echo `pwd`/build):/build \
		-v $(shell echo `pwd`/release):/release \
		--network="host" \
		tinyself_ubuntu
	chmod -R 777 release

jit: docker_build
	docker run -ti --rm \
		-e EXTRA_ARGS="--jit -O 3" \
		-e LC_CTYPE=en_US.UTF-8 \
		-v $(shell echo `pwd`/build):/build \
		-v $(shell echo `pwd`/release):/release \
		--network="host" \
		tinyself_ubuntu
	chmod -R 777 release

help:
	@echo "Parameters:"
	@echo "\trun"
	@echo "\t\tFor default build."
	@echo "\tjit"
	@echo "\t\tFor default build with --jit."
