# Docker-Based Multi-Architecture Wheel Building

This document describes the Docker-based build system for creating Python wheels with precise ABI control across multiple Linux distributions and architectures.

## Overview

The Docker build system solves several critical issues:

1. **ABI Compatibility**: Build wheels targeting specific glibc versions
2. **ARM64 Support**: Use QEMU emulation instead of waiting for GitHub ARM64 runners  
3. **Customer Requirements**: Match exact OS environments (Rocky Linux 9)
4. **Reproducible Builds**: Identical environments across all builds

## Supported Target Environments

| Distribution | glibc Version | Architecture | Use Case |
|--------------|---------------|--------------|----------|
| **Debian 12** | 2.36 | AMD64, ARM64 | Modern Linux systems, containers |
| **Rocky Linux 9** | 2.34 | AMD64, ARM64 | Enterprise RHEL environments |
| **Ubuntu 24.04** | 2.39 | AMD64, ARM64 | Latest Ubuntu LTS |

## Files

- `Dockerfile.wheels` - Multi-stage Dockerfile for wheel building
- `docker-bake.hcl` - Docker Bake configuration for build orchestration  
- `.github/workflows/wheels-docker.yml` - GitHub Actions workflow
- `test-docker-builds.sh` - Local testing script

## Local Testing

### Test a specific configuration:
```bash
./test-docker-builds.sh debian:12 linux/amd64
./test-docker-builds.sh rockylinux:9 linux/arm64
./test-docker-builds.sh ubuntu:24.04 linux/amd64
```

### Build all architectures for one OS:
```bash
docker buildx bake \
  --set wheel-builder.args.BASE_IMAGE=debian:12 \
  --set wheel-builder.platform=linux/amd64,linux/arm64 \
  wheel-builder
```

### Development build (local Docker image):
```bash
docker buildx bake \
  --set wheel-builder-local.args.BASE_IMAGE=debian:12 \
  wheel-builder-local
```

## Build Process

### 1. Multi-Stage Docker Build

**Base Stage:**
- Install system dependencies (build tools, libraries)
- Install Just, uv, Rust toolchains
- Set up cross-compilation environment

**Wheel Builder Stage:**  
- Copy source code
- Run `just build-all` to build wheels for all Python versions
- Generate build metadata
- Output wheels to `/output` directory

### 2. GitHub Actions Workflow

**Matrix Strategy:**
```yaml
matrix:
  target:
    - { name: "debian12-amd64", base_image: "debian:12", platform: "linux/amd64" }
    - { name: "debian12-arm64", base_image: "debian:12", platform: "linux/arm64" }
    - { name: "rocky9-amd64", base_image: "rockylinux:9", platform: "linux/amd64" }
    # ... etc
```

**Build Steps:**
1. Set up Docker Buildx with QEMU
2. Build wheels using Docker Bake
3. Upload artifacts by target environment
4. Publish to GitHub Releases (on master)
5. Publish to PyPI (on tags)

## Wheel Naming and Compatibility

### Platform Tags
- **linux_x86_64**: Built on AMD64, compatible with glibc 2.34+ systems
- **linux_aarch64**: Built on ARM64, compatible with glibc 2.34+ systems

### ABI Compatibility
- **Debian 12 wheels**: Work on glibc 2.36+ (Debian 12+, Ubuntu 22.04+)
- **Rocky 9 wheels**: Work on glibc 2.34+ (RHEL 9+, CentOS Stream 9+)  
- **Ubuntu 24.04 wheels**: Work on glibc 2.39+ (Ubuntu 24.04+)

## Troubleshooting

### Build Failures

**Check system dependencies:**
```bash
docker buildx bake build-info --set build-info.args.BASE_IMAGE=debian:12
docker run autobahn-build-info:debian:12 ldd --version
```

**Test toolchain installation:**
```bash
docker buildx build --platform linux/amd64 --target base \
  --build-arg BASE_IMAGE=debian:12 \
  -t test-base .
docker run test-base just --version
```

### QEMU Issues

**Enable QEMU emulation:**
```bash
docker run --privileged --rm tonistiigi/binfmt --install all
```

**Check platform support:**
```bash
docker buildx ls
docker buildx inspect --bootstrap
```

### Wheel Installation Issues

**Check glibc compatibility:**
```bash
ldd --version  # Check your system glibc
python -c "import autobahn._extension"  # Test extension loading
```

**Force specific wheel:**
```bash
pip install autobahn --only-binary=autobahn --force-reinstall
```

## Performance Notes

- **Build time**: ~5-10 minutes per target environment
- **QEMU overhead**: ARM64 builds ~2-3x slower than native
- **Caching**: GitHub Actions caches Docker layers for faster rebuilds
- **Parallelization**: All target environments build concurrently

## Migration from Native Builds

The Docker builds replace the previous native GitHub Actions builds:

| Old Approach | New Approach |
|--------------|--------------|
| `ubuntu-24.04` runner | Docker `ubuntu:24.04` image |
| `ubuntu-24.04-arm64` runner | Docker + QEMU emulation |
| GitHub runner dependency | Self-contained Docker builds |
| Variable runner availability | Consistent Docker environment |

## Future Enhancements

1. **musl Support**: Add Alpine Linux targets for static linking
2. **Windows Containers**: Docker-based Windows wheel building  
3. **Build Optimization**: Multi-stage caching, parallel Python builds
4. **Custom Base Images**: Pre-built images with toolchain included