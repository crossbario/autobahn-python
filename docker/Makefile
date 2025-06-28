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

clean_docker:
	-docker images | grep "crossbario/autobahn-python" | awk '{print $1}' | xargs docker rmi


download_wheels:
	mkdir -p ./.wheels/
	rm -f ./.wheels/*.whl
	curl -o ./.wheels/txaio-latest-py2.py3-none-any.whl 	$(WHEELS)/txaio-latest-py2.py3-none-any.whl
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


show:
	@echo
	@echo "autobahn build configuration -------------------------------------------------------------------------------------------"
	@echo
	@echo "  AUTOBAHN_BUILD_DATE     = ${AUTOBAHN_BUILD_DATE}"
	@echo "  AUTOBAHN_BUILD_ID       = ${AUTOBAHN_BUILD_ID}"
	@echo "  AUTOBAHN_VCS_REF        = ${AUTOBAHN_VCS_REF}"
	@echo "  AUTOBAHN_VERSION        = ${AUTOBAHN_VERSION}"
	@echo


build: build_cpy build_pypy

test: test_cpy test_pypy

publish: publish_cpy publish_pypy

list: list_cpy list_pypy


build_amd64: build_cpy_amd64 build_pypy_amd64

test_amd64: test_cpy_amd64 test_pypy_amd64

publish_amd64: publish_cpy_amd64 publish_pypy_amd64

list_amd64: list_cpy_amd64 list_pypy_amd64


build_arm64v8: build_cpy_arm64v8 build_pypy_arm64v8

test_arm64v8: test_cpy_arm64v8 test_pypy_arm64v8

publish_arm64v8: publish_cpy_arm64v8 publish_pypy_arm64v8

list_arm64v8: list_cpy_arm64v8 list_pypy_arm64v8


build_cpy: build_cpy_amd64 build_cpy_arm64v8

test_cpy: test_cpy_amd64 test_cpy_arm64v8

publish_cpy: publish_cpy_amd64 publish_cpy_arm64v8

list_cpy: list_cpy_amd64 list_cpy_arm64v8


build_pypy: build_pypy_amd64 build_pypy_arm64v8

test_pypy: test_pypy_amd64 test_pypy_arm64v8

publish_pypy: publish_pypy_amd64 publish_pypy_arm64v8

list_pypy: list_pypy_amd64 list_pypy_arm64v8


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
	docker run --rm crossbario/autobahn-python:cpy-amd64

publish_cpy_amd64:
	docker push crossbario/autobahn-python:cpy-amd64
	docker push crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}

list_cpy_amd64:
	@echo
	@echo "autobahn-python:cpy-amd64 ----------------------------------------------------------------------------------------------"
	@echo
	@docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@echo
	@docker images crossbario/autobahn-python:cpy-amd64
	@docker images crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}
	@docker images crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@docker images `docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}`


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
	docker run --rm crossbario/autobahn-python:cpy-arm64v8

publish_cpy_arm64v8:
	docker push crossbario/autobahn-python:cpy-arm64v8
	docker push crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}

list_cpy_arm64v8:
	@echo
	@echo
	@echo "autobahn-python:cpy-arm64v8 --------------------------------------------------------------------------------------------"
	@echo
	@docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@echo
	@docker images crossbario/autobahn-python:cpy-arm64v8
	@docker images crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}
	@docker images crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@docker images `docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}`


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
	docker run --rm crossbario/autobahn-python:pypy-amd64

publish_pypy_amd64:
	docker push crossbario/autobahn-python:pypy-amd64
	docker push crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}

list_pypy_amd64:
	@echo
	@echo
	@echo "autobahn-python:pypy-amd64 --------------------------------------------------------------------------------------------"
	@echo
	@docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@echo
	@docker images crossbario/autobahn-python:pypy-amd64
	@docker images crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}
	@docker images crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@docker images `docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}`


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
	docker run --rm crossbario/autobahn-python:pypy-arm64v8

publish_pypy_arm64v8:
	docker push crossbario/autobahn-python:pypy-arm64v8
	docker push crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}

list_pypy_arm64v8:
	@echo
	@echo
	@echo "autobahn-python:pypy-arm64v8 ------------------------------------------------------------------------------------------"
	@echo
	@docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@echo
	@docker images crossbario/autobahn-python:pypy-arm64v8
	@docker images crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}
	@docker images crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
	@docker images `docker inspect --format='{{index .RepoDigests 0}}' crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}`

# Docker multi-arch manifest
#
# https://docs.docker.com/engine/reference/commandline/manifest/
# https://docs.docker.com/docker-for-mac/multi-arch/
# https://www.docker.com/blog/multi-arch-build-and-images-the-simple-way/
# https://docs.docker.com/registry/spec/manifest-v2-2/
#
# Use the following options for different CPU archs:
#
#	--os linux --arch amd64
#	--os linux --arch 386
#	--os linux --arch arm64 --variant armv8
#	--os linux --arch arm
#
# Older Docker CLI needs: export DOCKER_CLI_EXPERIMENTAL=enabled
#
publish_manifest: publish_cpy_manifest publish_pypy_manifest

publish_cpy_manifest:
	docker manifest create --amend \
		crossbario/autobahn-python:cpy \
		crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \

	docker manifest annotate \
		crossbario/autobahn-python:cpy \
		crossbario/autobahn-python:cpy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		--os linux --arch amd64

	docker manifest annotate \
		crossbario/autobahn-python:cpy \
		crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		--os linux --arch arm64 --variant armv8

	docker manifest inspect \
		crossbario/autobahn-python:cpy

	docker manifest push --purge \
		crossbario/autobahn-python:cpy

publish_pypy_manifest:
	docker manifest create --amend \
		crossbario/autobahn-python:pypy \
		crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \

	docker manifest annotate \
		crossbario/autobahn-python:pypy \
		crossbario/autobahn-python:pypy-amd64-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		--os linux --arch amd64

	docker manifest annotate \
		crossbario/autobahn-python:pypy \
		crossbario/autobahn-python:pypy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID} \
		--os linux --arch arm64 --variant armv8

	docker manifest inspect \
		crossbario/autobahn-python:pypy

	docker manifest push --purge \
		crossbario/autobahn-python:pypy
