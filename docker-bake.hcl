# Docker Bake configuration for multi-arch wheel building
# https://docs.docker.com/build/bake/

variable "BASE_IMAGE" {
  default = "debian:12"
}

variable "PLATFORMS" {
  default = ["linux/amd64", "linux/arm64"]
}

group "default" {
  targets = ["wheel-builder"]
}

target "wheel-builder" {
  dockerfile = "Dockerfile.wheels"
  target = "wheel-builder"
  platforms = "${PLATFORMS}"
  args = {
    BASE_IMAGE = "${BASE_IMAGE}"
  }
  output = ["type=local,dest=./dist"]
  
  # Cache configuration for faster builds
  cache-from = [
    "type=gha,scope=wheel-builder-${BASE_IMAGE}"
  ]
  cache-to = [
    "type=gha,scope=wheel-builder-${BASE_IMAGE},mode=max"
  ]
}

# Development target for local testing
target "wheel-builder-local" {
  inherits = ["wheel-builder"]
  platforms = ["linux/amd64"]
  tags = ["autobahn-wheel-builder:local"]
  output = ["type=docker"]
}

# Test target with build info only
target "build-info" {
  dockerfile = "Dockerfile.wheels"
  target = "base"
  platforms = ["linux/amd64"]
  args = {
    BASE_IMAGE = "${BASE_IMAGE}"
  }
  output = ["type=docker"]
  tags = ["autobahn-build-info:${BASE_IMAGE}"]
}