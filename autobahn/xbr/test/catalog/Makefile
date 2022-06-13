BUILD_DIR=./build
FBS_FILES=./src/*.fbs
FBS_OUTPUT=./schema

# https://blog.infura.io/post/ipfs-file-upload-client-tool
setup_ipfs_client_tool:
	wget https://github.com/INFURA/ipfs-upload-client/releases/download/v0.1.1/ipfs-upload-client-v0.1.1-linux-amd64.tar.gz
	tar xvf ipfs-upload-client-v0.1.1-linux-amd64.tar.gz
	sudo cp ipfs-upload-client /usr/local/bin/

# https://github.com/KittyHawkCorp/stripzip
# https://linux.die.net/man/1/zip
setup_stripzip:
	cd /tmp && git clone https://github.com/KittyHawkCorp/stripzip.git && cd stripzip && make && sudo cp ./stripzip /usr/local/bin/

clean:
	rm -rf $(BUILD_DIR)
	@mkdir -p $(BUILD_DIR)/schema
	@mkdir -p $(BUILD_DIR)/img
	find $(BUILD_DIR)

distclean: clean
	rm -rf $(FBS_OUTPUT)
	mkdir $(FBS_OUTPUT)

compile:
	flatc -o $(FBS_OUTPUT) --binary --schema --bfbs-comments --bfbs-builtins $(FBS_FILES)

# demo.bfbs  testsvc1.bfbs  wamp-auth.bfbs  wamp.bfbs  wamp-control.bfbs  wamp-meta.bfbs
describe:
	xbrnetwork describe-schema --schema $(FBS_OUTPUT)/demo.bfbs

# IMPORTANT: note the use of "-X" and stripzip to preserve privacy and support repeatable builds
build: compile
	@cp catalog.yaml $(BUILD_DIR)/
	@cp $(FBS_OUTPUT)/*.bfbs $(BUILD_DIR)/schema/
	@cp LICENSE.txt $(BUILD_DIR)/
	@cp README.md $(BUILD_DIR)/
	@cp img/*.png $(BUILD_DIR)/img/
	@cd $(BUILD_DIR) && zip -9 -X -r demo .
	@stripzip $(BUILD_DIR)/demo.zip
	@du -hs $(BUILD_DIR)/demo.zip
	@openssl sha256 $(BUILD_DIR)/demo.zip

publish:
	ipfs-upload-client --id ${INFURA_IPFS_PROJECT_ID} --secret ${INFURA_IPFS_PROJECT_SECRET} \
		$(BUILD_DIR)/demo.zip

publish_curl:
	curl "https://ipfs.infura.io:5001/api/v0/add?pin=false" \
		-X POST \
		-H "Content-Type: multipart/form-data" \
		-F file=@$(BUILD_DIR)/demo.zip

fetch_catalog:
	@rm -f /tmp/demo.zip
	@curl -X POST --output /tmp/demo.zip \
		https://ipfs.infura.io:5001/api/v0/cat?arg=QmdaWNrsnsQcYxLxMP6bjP2wj5Mjtd7aez8RnnJWZ4uzyJ
	openssl sha256 /tmp/demo.zip
	openssl sha256 $(BUILD_DIR)/demo.zip
