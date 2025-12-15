# GitHub Actions Workflows

This document describes the CI/CD workflow architecture for autobahn-python,
including artifact production and consumption flow.

## Workflow Overview

| Workflow | Purpose | Trigger |
|----------|---------|---------|
| `main.yml` | Code quality, tests, documentation | Push, PR |
| `wstest.yml` | WebSocket conformance testing | Push, PR |
| `wheels.yml` | macOS/Windows wheels + source dist | Push, PR, tags |
| `wheels-docker.yml` | Linux x86_64 manylinux wheels | Push, PR, tags |
| `wheels-arm64.yml` | Linux ARM64 manylinux wheels | Push, PR, tags |
| `release.yml` | Collect artifacts, publish releases | workflow_run |

## Artifact Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARTIFACT PRODUCERS                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  main.yml                                                                   │
│  └── documentation                     (docs HTML)                          │
│                                                                             │
│  wstest.yml                                                                 │
│  └── wstest-results                    (WebSocket conformance reports)      │
│                                                                             │
│  wheels.yml (native GitHub runners)                                         │
│  ├── wheels-macos-arm64                (macOS ARM64 wheels)                 │
│  ├── wheels-windows-x86_64             (Windows x64 wheels)                 │
│  ├── linux-wheels-no-nvx               (Linux pure Python wheels)           │
│  └── source-distribution               (*.tar.gz sdist)                     │
│                                                                             │
│  wheels-docker.yml (manylinux_2_28_x86_64 container)                        │
│  └── artifacts-manylinux_2_28_x86_64   (Linux x64 wheels with NVX+flatc)    │
│                                                                             │
│  wheels-arm64.yml (manylinux_2_28_aarch64 container)                        │
│  ├── artifacts-arm64-cpython-3.11-manylinux_2_28_aarch64                    │
│  ├── artifacts-arm64-cpython-3.13-manylinux_2_28_aarch64                    │
│  ├── artifacts-arm64-pypy-3.11-bookworm-manylinux_2_36_aarch64              │
│  └── artifacts-arm64-pypy-3.11-trixie-manylinux_2_38_aarch64                │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           ARTIFACT CONSUMER                                  │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  release.yml                                                                │
│  ├── Downloads all artifacts from above workflows                           │
│  ├── Creates GitHub Release (development or stable)                         │
│  └── Publishes to PyPI (on tags only)                                       │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## Binary Wheel Features

autobahn-python binary wheels include:

1. **NVX Extension** - Native Rust-based acceleration for WebSocket/WAMP
2. **Bundled flatc** - FlatBuffers compiler for schema compilation
3. **reflection.bfbs** - Pre-compiled FlatBuffers reflection schema

## wheels.yml Step Execution Order

The `wheels.yml` workflow follows a deliberate 5-phase execution order
with filesystem sync points to ensure artifact integrity in CI environments.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 1: SETUP - Install toolchain (just, uv, rust)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── Checkout code                                                          │
│  ├── Install Just (Linux/macOS)                                             │
│  ├── Install Just (Windows)                                                 │
│  ├── Install uv (Linux/macOS)                                               │
│  ├── Install uv (Windows)                                                   │
│  ├── Install Rust (for NVX extension)                                       │
│  ├── Verify toolchain installation                                          │
│  └── Setup uv cache                                                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 2: BUILD - Build wheels/sdist for each platform                      │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── Build binary wheels with NVX+flatc (macOS)                             │
│  ├── Build binary wheels with NVX+flatc (Windows)                           │
│  ├── Build pure Python wheels without NVX (Linux)                           │
│  └── Build source distribution (Linux x86_64 only)                          │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 3: VALIDATION - Validate artifacts (per-OS with FS sync points)      │
├─────────────────────────────────────────────────────────────────────────────┤
│  │                                                                          │
│  │  --- macOS validation ---                                                │
│  ├── Force file system sync (post-build, pre-validation) - macOS            │
│  ├── Validate wheels integrity (macOS only)                                 │
│  ├── Generate SHA256 checksums (macOS only)                                 │
│  ├── Force file system sync (post-checksum) - macOS                         │
│  │                                                                          │
│  │  --- Windows validation ---                                              │
│  ├── Force file system sync (post-build, pre-validation) - Windows          │
│  ├── Validate wheels integrity (Windows only)                               │
│  ├── Generate SHA256 checksums (Windows only)                               │
│  ├── Force file system sync (post-checksum) - Windows                       │
│  │                                                                          │
│  │  --- Linux validation (source distribution) ---                          │
│  ├── Force file system sync (post-build, pre-validation) - Linux            │
│  ├── Verify source distribution integrity (Linux x86_64 only)               │
│  ├── Verify source distribution installs and works (Linux x86_64 only)      │
│  ├── Generate SHA256 checksums (Linux x86_64 only)                          │
│  └── Force file system sync (post-checksum) - Linux                         │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 4: METADATA - Generate build metadata (after all validations)        │
│  This phase comes AFTER all OS validations/checksums so it can aggregate    │
│  results from VALIDATION.txt and CHECKSUMS.sha256 into build-info.txt       │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── Generate build metadata                                                │
│  ├── Force file system sync (post-metadata) - macOS                         │
│  ├── Force file system sync (post-metadata) - Windows                       │
│  └── Force file system sync (post-metadata) - Linux                         │
└─────────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│  PHASE 5: LIST & UPLOAD - List artifacts and upload                         │
├─────────────────────────────────────────────────────────────────────────────┤
│  ├── List built artifacts (macOS)                                           │
│  ├── List built artifacts (Windows)                                         │
│  ├── List built artifacts (Linux - source distribution only)                │
│  ├── Upload wheel artifacts (macOS and Windows only)                        │
│  └── Upload source distribution (Linux x86_64 only)                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Why Filesystem Sync Points?

CI environments (especially macOS and Windows runners) may buffer filesystem
writes. Without explicit sync points, subsequent steps might read stale data
or incomplete files. The sync points ensure:

1. **Post-build sync** - All build artifacts are fully written before validation
2. **Post-checksum sync** - Checksum files are complete before metadata generation
3. **Post-metadata sync** - All metadata is written before artifact upload

### Smoke Test for Source Distribution

The Linux runner performs a full smoke test of the source distribution:

1. Creates an ephemeral venv with matching Python version
2. Installs build dependencies (cffi, setuptools, wheel, hatchling, maturin)
3. Installs sdist with `--no-build-isolation --no-cache-dir --no-binary autobahn`
4. Runs required smoke tests:
   - Import autobahn and check version
   - Import autobahn.flatbuffers and check version
   - Verify flatc binary is available and executable
   - Verify reflection files are present

All tests are **required** - sdist installs MUST provide identical
functionality to wheel installs including the flatc binary.

## Artifact Details

### 1. Artifact Producers (Upload)

| Workflow | Artifact Name | Contents | Platform |
|----------|--------------|----------|----------|
| **main.yml** | `documentation` | `docs/_build/html/` | N/A |
| **wstest.yml** | `wstest-results` | WebSocket conformance reports | N/A |
| **wheels.yml** | `wheels-macos-arm64` | macOS ARM64 wheels (cpy311-314, pypy311) | macOS arm64 |
| **wheels.yml** | `wheels-windows-x86_64` | Windows x64 wheels (cpy311-314, pypy311) | Windows x86_64 |
| **wheels.yml** | `linux-wheels-no-nvx` | Pure Python wheels (no NVX) | Linux x86_64 |
| **wheels.yml** | `source-distribution` | `*.tar.gz` sdist | Linux (build host) |
| **wheels-docker.yml** | `artifacts-manylinux_2_28_x86_64` | Linux x64 wheels (see below) | Linux x86_64 |
| **wheels-arm64.yml** | `artifacts-arm64-cpython-3.11-manylinux_2_28_aarch64` | CPython 3.11 wheel | Linux aarch64 |
| **wheels-arm64.yml** | `artifacts-arm64-cpython-3.13-manylinux_2_28_aarch64` | CPython 3.13 wheel | Linux aarch64 |
| **wheels-arm64.yml** | `artifacts-arm64-pypy-3.11-bookworm-manylinux_2_36_aarch64` | PyPy 3.11 wheel (Debian 12) | Linux aarch64 |
| **wheels-arm64.yml** | `artifacts-arm64-pypy-3.11-trixie-manylinux_2_38_aarch64` | PyPy 3.11 wheel (Debian 13) | Linux aarch64 |

**wheels-docker.yml artifact contents** (`artifacts-manylinux_2_28_x86_64`):
- `cpy311-linux-x86_64-manylinux_2_28`
- `cpy312-linux-x86_64-manylinux_2_28`
- `cpy313-linux-x86_64-manylinux_2_28`
- `cpy314-linux-x86_64-manylinux_2_28`
- `pypy311-linux-x86_64-manylinux_2_28`

### 2. Artifact Consumer (release.yml)

The `release.yml` workflow downloads artifacts using the `wamp-cicd` verified
download action. It maps artifact names via the `check-workflows` job outputs:

| Output Variable | Source Workflow | Artifact Pattern |
|-----------------|-----------------|------------------|
| `artifact_macos_wheels` | wheels.yml | `wheels-macos-arm64` |
| `artifact_windows_wheels` | wheels.yml | `wheels-windows-x86_64` |
| `artifact_source_dist` | wheels.yml | `source-distribution` |
| `artifact_linux_no_nvx` | wheels.yml | `linux-wheels-no-nvx` |
| `artifact_manylinux_x86_64` | wheels-docker.yml | `artifacts-manylinux_2_28_x86_64` |
| `artifact_arm64_cp311` | wheels-arm64.yml | `artifacts-arm64-cpython-3.11-manylinux_2_28_aarch64` |
| `artifact_arm64_cp313` | wheels-arm64.yml | `artifacts-arm64-cpython-3.13-manylinux_2_28_aarch64` |
| `artifact_arm64_pypy_bookworm` | wheels-arm64.yml | `artifacts-arm64-pypy-3.11-bookworm-manylinux_2_36_aarch64` |
| `artifact_arm64_pypy_trixie` | wheels-arm64.yml | `artifacts-arm64-pypy-3.11-trixie-manylinux_2_38_aarch64` |

## Platform Coverage

### Wheels Built

| Platform | Architecture | Python Versions | Manylinux Tag | Workflow |
|----------|--------------|-----------------|---------------|----------|
| Linux | x86_64 | 3.11, 3.12, 3.13, 3.14, PyPy 3.11 | manylinux_2_28 | wheels-docker.yml |
| Linux | aarch64 | 3.11, 3.13 | manylinux_2_28 | wheels-arm64.yml |
| Linux | aarch64 | PyPy 3.11 | manylinux_2_36/2_38 | wheels-arm64.yml |
| macOS | arm64 | 3.11, 3.12, 3.13, 3.14, PyPy 3.11 | N/A | wheels.yml |
| Windows | x86_64 | 3.11, 3.12, 3.13, 3.14, PyPy 3.11 | N/A | wheels.yml |

### Why Manylinux Containers?

Linux wheels are built inside official PyPA manylinux containers to ensure:

1. **ABI Compatibility** - Correct glibc symbol versions for target platforms
2. **ISA Compliance** - Baseline instruction set (no x86_64_v2+ on x86_64)
3. **auditwheel Success** - Clean wheel repair without ISA warnings
4. **Wide Compatibility** - Wheels work on older Linux distributions

The `manylinux_2_28` tag targets glibc 2.28+ (RHEL 8, Ubuntu 20.04+, Debian 11+).

**Important**: We use `manylinux_2_28` instead of `manylinux_2_34` because the
latter uses x86_64_v2 instruction set which causes auditwheel to fail when
bundling flatc binaries.

## Release Process

1. **On every push/PR**: All wheel workflows run and upload artifacts
2. **On workflow completion**: `release.yml` triggers via `workflow_run`
3. **Development releases**: Created automatically from feature branches
4. **Stable releases**: Created when a `v*` tag is pushed, also publishes to PyPI

## Maintenance Notes

When updating Python versions or manylinux tags:

1. Update the matrix in the relevant workflow file
2. Update artifact name patterns in `release.yml` `check-workflows` job
3. Update this README to reflect changes
4. Test with a PR before merging

---

*This documentation is maintained alongside the workflow files.*
