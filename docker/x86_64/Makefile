.PHONY: build

build:
	time docker build \
		--build-arg BUILD_DATE=${BUILD_DATE} \
		--build-arg AUTOBAHN_PYTHON_VCS_REF=${AUTOBAHN_PYTHON_VCS_REF} \
		--build-arg AUTOBAHN_PYTHON_VERSION=${AUTOBAHN_PYTHON_VERSION} \
		-t crossbario/autobahn-python:cpy3 \
		-t crossbario/autobahn-python:cpy3-${AUTOBAHN_PYTHON_VERSION} \
		-f Dockerfile.cpy3 .

	time docker build \
		--build-arg BUILD_DATE=${BUILD_DATE} \
		--build-arg AUTOBAHN_PYTHON_VCS_REF=${AUTOBAHN_PYTHON_VCS_REF} \
		--build-arg AUTOBAHN_PYTHON_VERSION=${AUTOBAHN_PYTHON_VERSION} \
		-t crossbario/autobahn-python:pypy3 \
		-t crossbario/autobahn-python:pypy3-${AUTOBAHN_PYTHON_VERSION} \
		-f Dockerfile.pypy3 .

	# time docker build \
	# 	--build-arg BUILD_DATE=${BUILD_DATE} \
	# 	--build-arg AUTOBAHN_PYTHON_VCS_REF=${AUTOBAHN_PYTHON_VCS_REF} \
	# 	--build-arg AUTOBAHN_PYTHON_VERSION=${AUTOBAHN_PYTHON_VERSION} \
	# 	-t crossbario/autobahn-python:latest \
	# 	-t crossbario/autobahn-python:cpy3-alpine \
	# 	-t crossbario/autobahn-python:cpy3-alpine-${AUTOBAHN_PYTHON_VERSION} \
	# 	-f Dockerfile.cpy3-alpine .

	# time docker build \
	# 	--build-arg BUILD_DATE=${BUILD_DATE} \
	# 	--build-arg AUTOBAHN_PYTHON_VCS_REF=${AUTOBAHN_PYTHON_VCS_REF} \
	# 	--build-arg AUTOBAHN_PYTHON_VERSION=${AUTOBAHN_PYTHON_VERSION} \
	# 	-t crossbario/autobahn-python:cpy3-minimal-aio \
	# 	-t crossbario/autobahn-python:cpy3-minimal-aio-${AUTOBAHN_PYTHON_VERSION} \
	# 	-f Dockerfile.cpy3-minimal-aio .

	# time docker build \
	# 	--build-arg BUILD_DATE=${BUILD_DATE} \
	# 	--build-arg AUTOBAHN_PYTHON_VCS_REF=${AUTOBAHN_PYTHON_VCS_REF} \
	# 	--build-arg AUTOBAHN_PYTHON_VERSION=${AUTOBAHN_PYTHON_VERSION} \
	# 	-t crossbario/autobahn-python:cpy3-minimal-tx \
	# 	-t crossbario/autobahn-python:cpy3-minimal-tx-${AUTOBAHN_PYTHON_VERSION} \
	# 	-f Dockerfile.cpy3-minimal-tx .

version: python_version autobahn_version xbr_version

python_version:
	docker run -it --rm crossbario/autobahn-python:cpy3 python -V
	docker run -it --rm crossbario/autobahn-python:pypy3 python -V
	# docker run -it --rm crossbario/autobahn-python:cpy3-alpine python -V
	# docker run -it --rm crossbario/autobahn-python:cpy3-minimal-aio python -V
	# docker run -it --rm crossbario/autobahn-python:cpy3-minimal-tx python -V

autobahn_version:
	docker run -it --rm crossbario/autobahn-python:cpy3 python -c "import autobahn; print('running autobahn-{}'.format(autobahn.__version__))"
	docker run -it --rm crossbario/autobahn-python:pypy3 python -c "import autobahn; print('running autobahn-{}'.format(autobahn.__version__))"
	# docker run -it --rm crossbario/autobahn-python:cpy3-alpine python -c "import autobahn; print('running autobahn-{}'.format(autobahn.__version__))"
	# docker run -it --rm crossbario/autobahn-python:cpy3-minimal-aio python -c "import autobahn; print('running autobahn-{}'.format(autobahn.__version__))"
	# docker run -it --rm crossbario/autobahn-python:cpy3-minimal-tx python -c "import autobahn; print('running autobahn-{}'.format(autobahn.__version__))"

xbr_version:
	docker run -it --rm crossbario/autobahn-python:cpy3 python -c "from autobahn import xbr; print(xbr.network.address)"
	docker run -it --rm crossbario/autobahn-python:pypy3 python -c "from autobahn import xbr; print(xbr.network.address)"
	# docker run -it --rm crossbario/autobahn-python:cpy3-alpine python -c "from autobahn import xbr; print(xbr.network.address)"


test: test_cpy3 test_pypy3 test_cpy3_alpine test_cpy3_minimal_aio test_cpy3_minimal_tx

test_cpy3:
	docker run -it --rm --link crossbar crossbario/autobahn-python:cpy3

test_pypy3:
	docker run -it --rm --link crossbar crossbario/autobahn-python:pypy3

test_cpy3_alpine:
	docker run -it --rm --link crossbar crossbario/autobahn-python:cpy3-alpine

test_cpy3_minimal_aio:
	docker run -it --rm --link crossbar crossbario/autobahn-python:cpy3-minimal-aio

test_cpy3_minimal_tx:
	docker run -it --rm --link crossbar crossbario/autobahn-python:cpy3-minimal-tx


publish:
	docker push crossbario/autobahn-python:latest
	docker push crossbario/autobahn-python:cpy3
	docker push crossbario/autobahn-python:cpy3-${AUTOBAHN_PYTHON_VERSION}
	docker push crossbario/autobahn-python:pypy3
	docker push crossbario/autobahn-python:pypy3-${AUTOBAHN_PYTHON_VERSION}
	# docker push crossbario/autobahn-python:cpy3-alpine
	# docker push crossbario/autobahn-python:cpy3-alpine-${AUTOBAHN_PYTHON_VERSION}
	# docker push crossbario/autobahn-python:cpy3-minimal-aio
	# docker push crossbario/autobahn-python:cpy3-minimal-aio-${AUTOBAHN_PYTHON_VERSION}
	# docker push crossbario/autobahn-python:cpy3-minimal-tx
	# docker push crossbario/autobahn-python:cpy3-minimal-tx-${AUTOBAHN_PYTHON_VERSION}

list:
	-docker images crossbario/autobahn-python:*

clean:
	./removeall.sh
