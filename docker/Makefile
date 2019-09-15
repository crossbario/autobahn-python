SUBDIRS = x86_64 armhf aarch64

subdirs: $(SUBDIRS)

BUILDDIRS = $(SUBDIRS:%=build-%)
VERSIONDIRS = $(SUBDIRS:%=version-%)
TESTDIRS = $(SUBDIRS:%=test-%)
PUBLISHDIRS = $(SUBDIRS:%=publish-%)

build: $(BUILDDIRS)
version: $(VERSIONDIRS)
test: $(TESTDIRS)
publish: $(PUBLISHDIRS)

.PHONY: subdirs $(BUILDDIRS) $(VERSIONDIRS) $(TESTDIRS) $(PUBLISHDIRS)
.PHONY: build version test publish

$(BUILDDIRS):
	$(MAKE) -C $(@:build-%=%) build

$(VERSIONDIRS):
	$(MAKE) -C $(@:version-%=%) version

$(TESTDIRS):
	$(MAKE) -C $(@:test-%=%) test

$(PUBLISHDIRS):
	$(MAKE) -C $(@:publish-%=%) publish

list:
	docker images crossbario/autobahn-python*:*

clean:
	-./removeall.sh


#
# Install Qemu (this is needed for cross-building armhf/aarch64 on amd64)
#
qemu_deps:
	mkdir -p ./.qemu
	cp /usr/bin/qemu-aarch64-static ./.qemu
	cp /usr/bin/qemu-arm-static ./.qemu
