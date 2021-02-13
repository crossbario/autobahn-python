SHOW_AUTOBAHN=python -c "import sys; print(sys.version); import autobahn; print('autobahn v{}'.format(autobahn.__version__)); from autobahn import xbr; print('HAS_XBR={}'.format(xbr.HAS_XBR))"
WHEELS=https://crossbarbuilder.s3.eu-central-1.amazonaws.com/wheels

default:
	@echo ""
	@echo "Targets:"
	@echo ""
	@echo "  params                 Print build parameter"
	@echo "  build                  Build images"
	@echo "  version                Print version of images"
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

download_wheels:
	mkdir -p ./.wheels/
	rm -f ./.wheels/*.whl
	curl -o ./.wheels/txaio-latest-py2.py3-none-any.whl 	$(WHEELS)/txaio-latest-py2.py3-none-any.whl
	curl -o ./.wheels/zlmdb-latest-py2.py3-none-any.whl 	$(WHEELS)/zlmdb-latest-py2.py3-none-any.whl
	curl -o ./.wheels/xbr-latest-py2.py3-none-any.whl 		$(WHEELS)/xbr-latest-py2.py3-none-any.whl
	curl -o ./.wheels/autobahn-latest-py2.py3-none-any.whl 	$(WHEELS)/autobahn-latest-py2.py3-none-any.whl
	ls -la ./.wheels


build_cpy: build_cpy_amd64 build_cpy_arm64v8

show_cpy: show_cpy_amd64 show_cpy_arm64v8

publish_cpy: publish_cpy_amd64 publish_cpy_arm64v8


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

show_cpy_amd64:
	docker run --rm -it crossbario/autobahn-python:cpy-amd64 $(SHOW_AUTOBAHN)

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

show_cpy_arm64v8:
	docker run --rm -it crossbario/autobahn-python:cpy-arm64v8 $(SHOW_AUTOBAHN)

publish_cpy_arm64v8:
	docker push crossbario/autobahn-python:cpy-arm64v8
	docker push crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}
	docker push crossbario/autobahn-python:cpy-arm64v8-${AUTOBAHN_VERSION}-${AUTOBAHN_BUILD_ID}
