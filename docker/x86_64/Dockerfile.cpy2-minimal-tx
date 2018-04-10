FROM python:2-alpine

MAINTAINER The Crossbar.io Project <support@crossbario.com>

# Metadata
ARG AUTOBAHN_PYTHON_VERSION
ARG BUILD_DATE
ARG AUTOBAHN_PYTHON_VCS_REF

# Metadata labeling
LABEL org.label-schema.build-date=$BUILD_DATE \
      org.label-schema.name="AutobahnPython Starter Template" \
      org.label-schema.description="Quickstart template for application development with AutobahnPython" \
      org.label-schema.url="http://crossbar.io" \
      org.label-schema.vcs-ref=$AUTOBAHN_PYTHON_VCS_REF \
      org.label-schema.vcs-url="https://github.com/crossbario/autobahn-python" \
      org.label-schema.vendor="The Crossbar.io Project" \
      org.label-schema.version=$AUTOBAHN_PYTHON_VERSION \
      org.label-schema.schema-version="1.0"

# Application home
ENV HOME /app
ENV DEBIAN_FRONTEND noninteractive
ENV NODE_PATH /usr/local/lib/node_modules/

# Crossbar.io connection defaults
ENV CBURL ws://crossbar:8080/ws
ENV CBREALM realm1

# until Twisted has fully migrated to CFFI, we need a toolchain =(
RUN apk add --update build-base \
    && rm -rf /var/cache/apk/*

# install Autobahn|Python
RUN    pip install -U pip \
    && pip install autobahn[twisted]==${AUTOBAHN_PYTHON_VERSION}

# add example service
COPY ./app /app
RUN ln -s /app/client_tx.py /app/client.py

# make /app a volume to allow external configuration
VOLUME /app

# set the app component directory as working directory
WORKDIR /app

# run service entry script by default
CMD ["sh", "/app/run"]
