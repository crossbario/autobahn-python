WHEELS=https://crossbarbuilder.s3.eu-central-1.amazonaws.com/wheels

default:
	@echo ""
	@echo "Targets:"
	@echo ""
	@echo "  params                 Print build parameters"
	@echo "  build                  Build images"
	@echo "  test                   Test images"
	@echo "  publish                Publish images"
	@echo ""

params:
	@echo ""
	@echo "Build environment configured:"
	@echo ""
	@echo "${AUTOBAHN_BUILD_DATE}"
	@echo "${AUTOBAHN_BUILD_ID}"
	@echo "${AUTOBAHN_VCS_REF}"
	@echo "${AUTOBAHN_VERSION}"
	@echo ""


install_qemu:
	sudo apt-get update
	sudo apt-get install -y qemu qemu-kvm qemu-system qemu-system-x86 qemu-system-arm
	sudo apt-get install -y --no-install-recommends qemu-user-static binfmt-support
	sudo update-binfmts --enable qemu-arm
	sudo update-binfmts --enable qemu-aarch64
	sudo update-binfmts --display qemu-arm
	sudo update-binfmts --display qemu-aarch64

copy_qemu:
	mkdir -p ./.qemu
	cp /usr/bin/qemu-aarch64-static ./.qemu
	cp /usr/bin/qemu-arm-static ./.qemu


clean_wheels:
	rm -rf ./.wheels
	mkdir -p ./.wheels/

download_wheels:
	mkdir -p ./.wheels/
	rm -f ./.wheels/*.whl
	curl -o ./.wheels/txaio-latest-py2.py3-none-any.whl 	$(WHEELS)/txaio-latest-py2.py3-none-any.whl
	curl -o ./.wheels/zlmdb-latest-py2.py3-none-any.whl 	$(WHEELS)/zlmdb-latest-py2.py3-none-any.whl
	curl -o ./.wheels/xbr-latest-py2.py3-none-any.whl 		$(WHEELS)/xbr-latest-py2.py3-none-any.whl
	curl -o ./.wheels/autobahn-latest-py2.py3-none-any.whl 	$(WHEELS)/autobahn-latest-py2.py3-none-any.whl
	ls -la ./.wheels

build_this_wheel:
	mkdir -p ./.wheels/
	rm -f ./.wheels/autobahn*.whl
	pip3 wheel --no-deps --wheel-dir=./.wheels ..
	mv .wheels/autobahn*.whl .wheels/autobahn-latest-py2.py3-none-any.whl
	ls -la ./.wheels


# WARNING: this will stop and remove all containers on the local host!
docker_stop_rm:
	-docker stop $(docker ps -a -q)
	-docker rm $(docker ps -a -q -f)


build: build_cpy build_pypy

test: test_cpy test_pypy

publish: publish_cpy publish_pypy


build_amd64: build_cpy_amd64 build_pypy_amd64

test_amd64: test_cpy_amd64 test_pypy_amd64

publish_amd64: publish_cpy_amd64 publish_pypy_amd64


build_arm64v8: build_cpy_arm64v8 build_pypy_arm64v8

test_arm64v8: test_cpy_arm64v8 test_pypy_arm64v8

publish_arm64v8: publish_cpy_arm64v8 publish_pypy_arm64v8


build_cpy: build_cpy_amd64 build_cpy_arm64v8

test_cpy: test_cpy_amd64 test_cpy_arm64v8

publish_cpy: publish_cpy_amd64 publish_cpy_arm64v8


build_pypy: build_pypy_amd64 build_pypy_arm64v8

test_pypy: test_pypy_amd64 test_pypy_arm64v8

publish_pypy: publish_pypy_amd64 publish_pypy_arm64v8


build_cpy_amd64:
	docker build \
		--build-arg AUTOBAHN_ARCH=amd64 \
		--build-arg AUTOBAHN_BUILD_ID=${AUTOBAHN_BUILD_ID} \
		--build-arg AUTOBAHN_BUILD_DATE=${AUTOBAHN_BUILD_DATE} \
		--build-arg AUTOBAHN_VCS_REF=${AUTOBAHN_VCS_REF} \
		--build-arg AUTOBAHN_VERSION=${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:cpy-amd64 \
		-t crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		-f Dockerfile.cpy-slim .
	docker images crossbario/autobahn-python:cpy-amd64

test_cpy_amd64:
	docker run --rm -it crossbario/autobahn-python:cpy-amd64

publish_cpy_amd64:
	docker push crossbario/autobahn-python:cpy-amd64
	docker push crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}


build_cpy_arm64v8:
	docker build \
		--build-arg AUTOBAHN_ARCH=arm64v8 \
		--build-arg AUTOBAHN_BUILD_ID=${AUTOBAHN_BUILD_ID} \
		--build-arg AUTOBAHN_BUILD_DATE=${AUTOBAHN_BUILD_DATE} \
		--build-arg AUTOBAHN_VCS_REF=${AUTOBAHN_VCS_REF} \
		--build-arg AUTOBAHN_VERSION=${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:cpy-arm64v8 \
		-t crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		-f ./Dockerfile.cpy-slim .
	docker images crossbario/autobahn-python:cpy-arm64v8

test_cpy_arm64v8:
	docker run --rm -it crossbario/autobahn-python:cpy-arm64v8

publish_cpy_arm64v8:
	docker push crossbario/autobahn-python:cpy-arm64v8
	docker push crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}


build_pypy_amd64:
	docker build \
		--build-arg AUTOBAHN_ARCH=amd64 \
		--build-arg AUTOBAHN_BUILD_ID=${AUTOBAHN_BUILD_ID} \
		--build-arg AUTOBAHN_BUILD_DATE=${AUTOBAHN_BUILD_DATE} \
		--build-arg AUTOBAHN_VCS_REF=${AUTOBAHN_VCS_REF} \
		--build-arg AUTOBAHN_VERSION=${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:pypy-amd64 \
		-t crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		-f Dockerfile.pypy-slim .
	docker images crossbario/autobahn-python:pypy-amd64

test_pypy_amd64:
	docker run --rm -it crossbario/autobahn-python:pypy-amd64

publish_pypy_amd64:
	docker push crossbario/autobahn-python:pypy-amd64
	docker push crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}


build_pypy_arm64v8:
	docker build \
		--build-arg AUTOBAHN_ARCH=arm64v8 \
		--build-arg AUTOBAHN_BUILD_ID=${AUTOBAHN_BUILD_ID} \
		--build-arg AUTOBAHN_BUILD_DATE=${AUTOBAHN_BUILD_DATE} \
		--build-arg AUTOBAHN_VCS_REF=${AUTOBAHN_VCS_REF} \
		--build-arg AUTOBAHN_VERSION=${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:pypy-arm64v8 \
		-t crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION} \
		-t crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		-f ./Dockerfile.pypy-slim .
	docker images crossbario/autobahn-python:pypy-arm64v8

test_pypy_arm64v8:
	docker run --rm -it crossbario/autobahn-python:pypy-arm64v8

publish_pypy_arm64v8:
	docker push crossbario/autobahn-python:pypy-arm64v8
	docker push crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}


# docker manifest create --amend {multi-arch-tag} {os-specific-tag-1} {os-specific-tag-2}
# docker manifest annotate {multi-arch-tag} {os-specific-tag-1} --os {os-1} --arch {arch-1}
# docker manifest annotate {multi-arch-tag} {os-specific-tag-2} --os {os-2} --arch {arch-2}
# docker manifest push --purge {multi-arch-tag}

# export DOCKER_CLI_EXPERIMENTAL=enabled
publish_docker_manifest:
	docker manifest create crossbario/crossbarfx:latest \
		crossbario/crossbarfx:pypy-slim-amd64-${CROSSBARFX_VERSION} \
		crossbario/crossbarfx:pypy-slim-i386-${CROSSBARFX_VERSION} \
		crossbario/crossbarfx:pypy-slim-arm64v8-${CROSSBARFX_VERSION} \
		crossbario/crossbarfx:cpy-slim-arm32v7-${CROSSBARFX_VERSION}

	# docker manifest create crossbario/crossbarfx:latest \
	# 	crossbario/crossbarfx:pypy-slim-amd64-${CROSSBARFX_VERSION} \
	# 	crossbario/crossbarfx:pypy-slim-i386-${CROSSBARFX_VERSION} \
	# 	crossbario/crossbarfx:pypy-slim-arm64v8-${CROSSBARFX_VERSION} \
	# 	crossbario/crossbarfx:cpy-slim-amd64-${CROSSBARFX_VERSION} \
	# 	crossbario/crossbarfx:cpy-slim-i386-${CROSSBARFX_VERSION} \
	# 	crossbario/crossbarfx:cpy-slim-arm64v8-${CROSSBARFX_VERSION} \
	# 	crossbario/crossbarfx:cpy-slim-arm32v7-${CROSSBARFX_VERSION}

	docker manifest annotate crossbario/crossbarfx:latest crossbario/crossbarfx:pypy-slim-amd64-${CROSSBARFX_VERSION} --os linux --arch amd64
	docker manifest annotate crossbario/crossbarfx:latest crossbario/crossbarfx:pypy-slim-i386-${CROSSBARFX_VERSION} --os linux --arch 386
	docker manifest annotate crossbario/crossbarfx:latest crossbario/crossbarfx:pypy-slim-arm64v8-${CROSSBARFX_VERSION}  --os linux --arch arm64 --variant armv8
	docker manifest annotate crossbario/crossbarfx:latest crossbario/crossbarfx:cpy-slim-arm32v7-${CROSSBARFX_VERSION}  --os linux --arch arm

	docker manifest inspect crossbario/crossbarfx:latest

	docker manifest push --purge crossbario/crossbarfx:latest
