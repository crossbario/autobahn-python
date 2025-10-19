# Copyright (c) typedef int GmbH, Germany, 2025. All rights reserved.
#

# IMPORTANT:
# Ubuntu: sudo apt install gir1.2-girepository-2.0-dev
# Debian: https://pkgs.org/search/?q=girepository


# -----------------------------------------------------------------------------
# -- just global configuration
# -----------------------------------------------------------------------------

set unstable := true
set positional-arguments := true
set script-interpreter := ['uv', 'run', '--script']

# uv env vars
# see: https://docs.astral.sh/uv/reference/environment/

# project base directory = directory of this justfile
PROJECT_DIR := justfile_directory()

# Default recipe: list all recipes
default:
    @echo ""
    @just --list
    @echo ""

# Tell uv to always copy files instead of trying to hardlink them.
# set export UV_LINK_MODE := 'copy'

# Tell uv to use project-local cache directory.
export UV_CACHE_DIR := './.uv-cache'

# Autobahn|Testsuite (https://github.com/crossbario/autobahn-testsuite) Docker image to use.
AUTOBAHN_TESTSUITE_IMAGE := 'crossbario/autobahn-testsuite:25.10.1'

# Default output directory for Autobahn|Testsuite reports (HTML files).
AUTOBAHN_TESTSUITE_OUTPUT_DIR := justfile_directory() / '.wstest'

# Default config directory for Autobahn|Testsuite configuration (JSON files).
AUTOBAHN_TESTSUITE_CONFIG_DIR := justfile_directory() / 'wstest'

# Use this common single directory for all uv venvs.
VENV_DIR := './.venvs'

# Define a justfile-local variable for our environments.
ENVS := 'cpy314 cpy313 cpy312 cpy311 pypy311'

# Internal helper to map Python version short name to full uv version
_get-spec short_name:
    #!/usr/bin/env bash
    set -e
    case {{short_name}} in
        cpy314)  echo "cpython-3.14";;  # cpython-3.14.0b3-linux-x86_64-gnu
        cpy313)  echo "cpython-3.13";;  # cpython-3.13.5-linux-x86_64-gnu
        cpy312)  echo "cpython-3.12";;  # cpython-3.12.11-linux-x86_64-gnu
        cpy311)  echo "cpython-3.11";;  # cpython-3.11.13-linux-x86_64-gnu
        pypy311) echo "pypy-3.11";;     # pypy-3.11.11-linux-x86_64-gnu
        *)       echo "Unknown environment: {{short_name}}" >&2; exit 1;;
    esac

# uv python install pypy-3.11-linux-aarch64-gnu --preview --verbose
# file /home/oberstet/.local/share/uv/python/pypy-3.11.11-linux-aarch64-gnu/bin/pypy3.11
# /home/oberstet/.local/share/uv/python/pypy-3.11.11-linux-aarch64-gnu/bin/pypy3.11: ELF 64-bit LSB executable, ARM aarch64, version 1 (SYSV), dynamically linked, interpreter /lib/ld-linux-aarch64.so.1, BuildID[sha1]=150f642a07dc36d3e465beaa0109e70da76ca67e, for GNU/Linux 3.7.0, stripped

# Internal helper that calculates and prints the system-matching venv name.
_get-system-venv-name:
    #!/usr/bin/env bash
    set -e
    SYSTEM_VERSION=$(/usr/bin/python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    ENV_NAME="cpy$(echo ${SYSTEM_VERSION} | tr -d '.')"

    if ! echo "{{ ENVS }}" | grep -q -w "${ENV_NAME}"; then
        echo "Error: System Python (${SYSTEM_VERSION}) maps to '${ENV_NAME}', which is not a supported environment in this project." >&2
        exit 1
    fi
    # The only output of this recipe is the name itself.
    echo "${ENV_NAME}"

# Helper recipe to get the python executable path for a venv
_get-venv-python venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        VENV_NAME=$(just --quiet _get-system-venv-name)
    fi
    VENV_PATH="{{VENV_DIR}}/${VENV_NAME}"

    # In your main recipes, replace direct calls to python with:
    # VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    # ${VENV_PYTHON} -V
    # ${VENV_PYTHON} -m pip -V

    if [[ "$OS" == "Windows_NT" ]]; then
        echo "${VENV_PATH}/Scripts/python.exe"
    else
        echo "${VENV_PATH}/bin/python3"
    fi

# -----------------------------------------------------------------------------
# -- General/global helper recipes
# -----------------------------------------------------------------------------

# Setup bash tab completion for the current user (to activate: `source ~/.config/bash_completion`).
setup-completion:
    #!/usr/bin/env bash
    set -e

    COMPLETION_FILE="${XDG_CONFIG_HOME:-$HOME/.config}/bash_completion"
    MARKER="# --- Just completion ---"

    echo "==> Setting up bash tab completion for 'just'..."

    # Check if we have already configured it.
    if [ -f "${COMPLETION_FILE}" ] && grep -q "${MARKER}" "${COMPLETION_FILE}"; then
        echo "--> 'just' completion is already configured."
        exit 0
    fi

    echo "--> Configuration not found. Adding it now..."

    # 1. Ensure the directory exists.
    mkdir -p "$(dirname "${COMPLETION_FILE}")"

    # 2. Add our marker comment to the file.
    echo "" >> "${COMPLETION_FILE}"
    echo "${MARKER}" >> "${COMPLETION_FILE}"

    # 3. CRITICAL: Run `just` and append its raw output directly to the file.
    #    No `echo`, no `eval`, no quoting hell. Just run and redirect.
    just --completions bash >> "${COMPLETION_FILE}"

    echo "--> Successfully added completion logic to ${COMPLETION_FILE}."

    echo ""
    echo "==> Setup complete. Please restart your shell or run the following command:"
    echo "    source \"${COMPLETION_FILE}\""

# Remove ALL generated files, including venvs, caches, and build artifacts. WARNING: This is a destructive operation.
distclean:
    #!/usr/bin/env bash
    set -e

    echo "==> Performing a deep clean (distclean)..."

    # 1. Remove top-level directories known to us.
    #    This is fast for the common cases.
    echo "--> Removing venvs, cache, and build/dist directories..."
    rm -rf {{UV_CACHE_DIR}} {{VENV_DIR}} build/ dist/ wheelhouse/ .pytest_cache/ .ruff_cache/ .mypy_cache/
    rm -rf .wstest docs/_build/

    rm -f ./*.so
    rm -f ./.coverage.*
    rm -rf ./_trial_temp

    # 2. Use `find` to hunt down and destroy nested artifacts that can be
    #    scattered throughout the source tree. This is the most thorough part.
    echo "--> Searching for and removing nested Python caches..."
    find . -type d -name "__pycache__" -exec rm -rf {} +

    echo "--> Searching for and removing compiled Python files..."
    find . -type f -name "*.pyc" -delete
    find . -type f -name "*.pyo" -delete

    echo "--> Searching for and removing setuptools egg-info directories..."
    find . -type d -name "*.egg-info" -exec rm -rf {} +

    echo "--> Searching for and removing coverage data..."
    rm -f .coverage
    find . -type f -name ".coverage.*" -delete

    echo "==> Distclean complete. The project is now pristine."

# -----------------------------------------------------------------------------
# -- Python virtual environments
# -----------------------------------------------------------------------------

# List all Python virtual environments
list-all:
    #!/usr/bin/env bash
    set -e
    echo
    echo "Available CPython run-times:"
    echo "============================"
    echo
    uv python list --all-platforms cpython
    echo
    echo "Available PyPy run-times:"
    echo "========================="
    echo
    uv python list --all-platforms pypy
    echo
    echo "Mapped Python run-time shortname => full version:"
    echo "================================================="
    echo
    # This shell loop correctly uses a SHELL variable ($env), not a just variable.
    for env in {{ENVS}}; do
        # We call our helper recipe to get the spec for the current env.
        # The `--quiet` flag is important to only capture the `echo` output.
        spec=$(just --quiet _get-spec "$env")
        echo "  - $env => $spec"
    done
    echo
    echo "Create a Python venv using: just create <shortname>"

# Create a single Python virtual environment (usage: `just create cpy314` or `just create`)
create venv="":
    #!/usr/bin/env bash
    set -e

    VENV_NAME="{{ venv }}"

    # This is the "default parameter" logic.
    # If VENV_NAME is empty (because `just create` was run), calculate the default.
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi

    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")

    # Only create the venv if it doesn't already exist
    if [ ! -d "${VENV_PATH}" ]; then
        # Get the Python spec just-in-time
        PYTHON_SPEC=$(just --quiet _get-spec "${VENV_NAME}")

        echo "==> Creating Python virtual environment '${VENV_NAME}' using ${PYTHON_SPEC} in ${VENV_PATH}..."
        mkdir -p "{{ VENV_DIR }}"
        uv venv --seed --python "${PYTHON_SPEC}" "${VENV_PATH}"
        echo "==> Successfully created venv '${VENV_NAME}'."
    else
        echo "==> Python virtual environment '${VENV_NAME}' already exists in ${VENV_PATH}."
    fi

    ${VENV_PYTHON} -V
    ${VENV_PYTHON} -m pip -V

    echo "==> Activate Python virtual environment with: source ${VENV_PATH}/bin/activate"

# Meta-recipe to run `create` on all environments
create-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just create ${venv}
    done

# Get the version of a single virtual environment's Python (usage: `just version cpy314`)
version venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"

    # This is the "default parameter" logic.
    # If VENV_NAME is empty (because `just create` was run), calculate the default.
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi

    if [ -d "{{ VENV_DIR }}/${VENV_NAME}" ]; then
        echo "==> Python virtual environment '${VENV_NAME}' exists:"
        "{{VENV_DIR}}/${VENV_NAME}/bin/python" -V
    else
        echo "==>  Python virtual environment '${VENV_NAME}' does not exist."
    fi
    echo ""

# Get versions of all Python virtual environments
version-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just version ${venv}
    done

# Make Python packages installed by the OS package manager available in a managed venv. Usage: `just link-system-packages "" "/usr/lib/kicad-nightly/lib/python3/dist-packages"`
link-system-packages venv="" vendors="": (create venv)
    #!/usr/bin/env bash
    set -euo pipefail

    VENV_NAME="{{ venv }}"
    VENDOR_PATHS="{{ vendors }}"

    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi

    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    if [ ! -d "${VENV_PATH}" ] || [ ! -f "${VENV_PATH}/bin/python" ]; then
        echo "✗ Error: Virtual environment '${VENV_NAME}' not found at '${VENV_PATH}'." >&2
        exit 1
    fi
    echo "✓ Found virtual environment: ${VENV_PATH}"

    SYSTEM_PYTHON="/usr/bin/python3"
    SYSTEM_VERSION=$(${SYSTEM_PYTHON} -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")

    # Collect all relevant site-packages directories (Debian + Ubuntu quirks)
    SYSTEM_SITE_PACKAGES=$(${SYSTEM_PYTHON} -c "import sysconfig, site, os, sys; paths={sysconfig.get_path('purelib')}; [paths.add(p) for p in site.getsitepackages() if os.path.isdir(p)]; print('\n'.join(sorted(paths)))")

    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    VENV_VERSION=$(${VENV_PYTHON} -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
    VENV_SITE_PACKAGES=$(${VENV_PYTHON} -c "import sysconfig; print(sysconfig.get_path('purelib'))")

    echo "  - System Python ${SYSTEM_VERSION} site-packages: ${SYSTEM_SITE_PACKAGES}"
    echo "  - Venv   Python ${VENV_VERSION} site-packages: ${VENV_SITE_PACKAGES}"

    if [ "${VENV_VERSION}" != "${SYSTEM_VERSION}" ]; then
        echo "✗ Error: Python version mismatch!" >&2
        echo "  System is ${SYSTEM_VERSION}, but venv is ${VENV_VERSION}." >&2
        echo "  Cannot link system packages due to risk of binary incompatibility." >&2
        # exit 1
    fi
    echo "✓ Python versions match."

    PTH_FILE="${VENV_SITE_PACKAGES}/__system_packages.pth"
    echo "==> Writing link file: ${PTH_FILE}"

    {
        # system paths (multi-line safe)
        while IFS= read -r sp; do
            if [ -d "$sp" ]; then
                echo "$sp"
            else
                echo "⚠ Warning: system path not found: $sp" >&2
            fi
        done <<< "${SYSTEM_SITE_PACKAGES}"

        # vendor paths (comma/space separated)
        if [ -n "${VENDOR_PATHS}" ]; then
            IFS=', ' read -ra VENDOR_ARRAY <<< "${VENDOR_PATHS}"
            for vp in "${VENDOR_ARRAY[@]}"; do
                if [ -d "${vp}" ]; then
                    echo "${vp}"
                else
                    echo "⚠ Warning: vendor path not found: ${vp}" >&2
                fi
            done
        fi
    } > "${PTH_FILE}"

    echo "✓ Done."
    echo
    echo "Linked paths in $(basename "${PTH_FILE}"):"
    echo
    cat "${PTH_FILE}"
    echo

# -----------------------------------------------------------------------------
# -- Installation and Test
# -----------------------------------------------------------------------------

# Install this package and its run-time dependencies in a single environment (usage: `just install cpy314` or `just install`)
install venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing package with package runtime dependencies in ${VENV_NAME}..."
    # uv pip install --python "{{VENV_DIR}}/${VENV_NAME}/bin/python" .[all]
    ${VENV_PYTHON} -m pip install .[all]

# Install this package in development (editable) mode and its run-time dependencies in a single environment (usage: `just install-dev cpy314` or `just install-dev`)
install-dev venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing package - in editable mode - with package runtime dependencies in ${VENV_NAME}..."
    # uv pip install --python "{{VENV_DIR}}/${VENV_NAME}/bin/python" -e .[all]
    ${VENV_PYTHON} -m pip install -e .[all]

# Meta-recipe to run `install` on all environments
install-all:
    #!/usr/bin/env bash
    set -e
    for venv in {{ENVS}}; do
        just install ${venv}
    done

# Meta-recipe to run `install-dev` on all environments
install-dev-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just install-dev ${venv}
    done

# -----------------------------------------------------------------------------
# -- Installation: Tools (Ruff, Sphinx, etc)
# -----------------------------------------------------------------------------

# Install minimal build tools for building wheels (usage: `just install-build-tools cpy314`)
# This is lighter than install-tools as it excludes dependencies like twine
# (which depends on nh3, a Rust package that segfaults under QEMU ARM64 emulation)
install-build-tools venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing minimal build tools in ${VENV_NAME}..."

    ${VENV_PYTHON} -V
    ${VENV_PYTHON} -m pip -V

    ${VENV_PYTHON} -m pip install -e .[build-tools]

# Install the development tools for this Package in a single environment (usage: `just install-tools cpy314`)
install-tools venv="": (create venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Installing package development tools in ${VENV_NAME}..."

    ${VENV_PYTHON} -V
    ${VENV_PYTHON} -m pip -V

    # uv pip install --python "{{VENV_DIR}}/${VENV_NAME}/bin/python" -e .[dev]
    ${VENV_PYTHON} -m pip install -e .[dev]

# Meta-recipe to run `install-tools` on all environments
install-tools-all:
    #!/usr/bin/env bash
    set -e
    for venv in {{ENVS}}; do
        just install-tools ${venv}
    done

# Install Rust (rustc & cargo) from upstream via rustup.
install-rust:
    #!/usr/bin/env bash
    set -e
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
    . "$HOME/.cargo/env"
    which rustc
    rustc --version
    which cargo
    cargo --version

# Install Autobahn WebSocket Testsuite (Docker image).
install-wstest:
    #!/usr/bin/env bash
    set -e
    sudo docker pull {{AUTOBAHN_TESTSUITE_IMAGE}}

# -----------------------------------------------------------------------------
# -- Linting, Static Typechecking, .. the codebase
# -----------------------------------------------------------------------------

# Automatically fix all formatting and code style issues.
autoformat venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    echo "==> Automatically formatting code with ${VENV_NAME}..."

    # 1. Run the FORMATTER first. This will handle line lengths, quotes, etc.
    "${VENV_PATH}/bin/ruff" format --exclude ./tests ./autobahn

    # 2. Run the LINTER'S FIXER second. This will handle things like
    #    removing unused imports, sorting __all__, etc.
    "${VENV_PATH}/bin/ruff" check --fix --exclude ./tests ./autobahn
    echo "--> Formatting complete."

# Lint code using Ruff in a single environment
check-format venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    echo "==> Linting code with ${VENV_NAME}..."
    "${VENV_PATH}/bin/ruff" check .

# Run static type checking with mypy
check-typing venv="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    echo "==> Running static type checks with ${VENV_NAME}..."
    "${VENV_PATH}/bin/mypy" autobahn/

# Run coverage for Twisted tests only
check-coverage-twisted venv="" use_nvx="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")

    # Handle NVX configuration
    USE_NVX="{{ use_nvx }}"
    if [ "${USE_NVX}" = "1" ]; then
        export AUTOBAHN_USE_NVX=1
        echo "==> Running Twisted tests with coverage in ${VENV_NAME} (WITH NVX)..."
    elif [ "${USE_NVX}" = "0" ]; then
        export AUTOBAHN_USE_NVX=0
        echo "==> Running Twisted tests with coverage in ${VENV_NAME} (WITHOUT NVX)..."
    else
        echo "==> Running Twisted tests with coverage in ${VENV_NAME} (AUTO NVX)..."
    fi

    # Clean previous coverage data
    rm -f .coverage .coverage.*

    # Run Twisted tests with coverage
    USE_TWISTED=1 "${VENV_PATH}/bin/coverage" run \
        --source=autobahn \
        --parallel-mode \
        -m twisted.trial --no-recurse \
        autobahn.test \
        autobahn.twisted.test \
        autobahn.websocket.test \
        autobahn.rawsocket.test \
        autobahn.wamp.test \
        autobahn.nvx.test

# Run coverage for asyncio tests only
check-coverage-asyncio venv="" use_nvx="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    # Handle NVX configuration
    USE_NVX="{{ use_nvx }}"
    if [ "${USE_NVX}" = "1" ]; then
        export AUTOBAHN_USE_NVX=1
        echo "==> Running asyncio tests with coverage in ${VENV_NAME} (WITH NVX)..."
    elif [ "${USE_NVX}" = "0" ]; then
        export AUTOBAHN_USE_NVX=0
        echo "==> Running asyncio tests with coverage in ${VENV_NAME} (WITHOUT NVX)..."
    else
        echo "==> Running asyncio tests with coverage in ${VENV_NAME} (AUTO NVX)..."
    fi

    # Run asyncio tests with coverage (parallel mode to combine later)
    USE_ASYNCIO=1 "${VENV_PATH}/bin/coverage" run \
        --source=autobahn \
        --parallel-mode \
        -m pytest -s -v -rfP \
        --ignore=./autobahn/twisted ./autobahn

# Combined coverage report from both Twisted and asyncio tests
check-coverage-combined venv="" use_nvx="": (check-coverage-twisted venv use_nvx) (check-coverage-asyncio venv use_nvx)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    # Determine NVX suffix for report naming
    USE_NVX="{{ use_nvx }}"
    if [ "${USE_NVX}" = "1" ]; then
        NVX_SUFFIX="-with-nvx"
        echo "==> Combining coverage data from Twisted and asyncio tests (WITH NVX)..."
    elif [ "${USE_NVX}" = "0" ]; then
        NVX_SUFFIX="-without-nvx"
        echo "==> Combining coverage data from Twisted and asyncio tests (WITHOUT NVX)..."
    else
        NVX_SUFFIX=""
        echo "==> Combining coverage data from Twisted and asyncio tests (AUTO NVX)..."
    fi

    # Combine all coverage data files
    "${VENV_PATH}/bin/coverage" combine

    # Generate reports with NVX-specific naming
    mkdir -p docs/_build/html
    "${VENV_PATH}/bin/coverage" html -d docs/_build/html/coverage-combined${NVX_SUFFIX}
    "${VENV_PATH}/bin/coverage" report --show-missing

    echo ""
    echo "✅ Combined coverage report generated:"
    echo "   HTML: docs/_build/html/coverage-combined${NVX_SUFFIX}/index.html"
    echo "   Text: above summary"

# Legacy coverage recipe (DEPRECATED - use check-coverage-combined instead)
check-coverage venv="" use_nvx="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    echo "⚠️  DEPRECATED: Use 'just check-coverage-combined' for comprehensive coverage"
    echo "⚠️  This recipe only runs pytest coverage and misses Twisted-specific code paths"
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    # Handle NVX configuration
    USE_NVX="{{ use_nvx }}"
    if [ "${USE_NVX}" = "1" ]; then
        export AUTOBAHN_USE_NVX=1
        NVX_SUFFIX="-with-nvx"
        echo "==> Running tests with coverage with ${VENV_NAME} (WITH NVX)..."
    elif [ "${USE_NVX}" = "0" ]; then
        export AUTOBAHN_USE_NVX=0
        NVX_SUFFIX="-without-nvx"
        echo "==> Running tests with coverage with ${VENV_NAME} (WITHOUT NVX)..."
    else
        NVX_SUFFIX=""
        echo "==> Running tests with coverage with ${VENV_NAME} (AUTO NVX)..."
    fi

    mkdir -p docs/_build/html
    # for now, ignore any non-zero exit code by prefixing with hyphen (FIXME: remove later)
    "${VENV_PATH}/bin/pytest" \
        --cov=autobahn \
        --cov-report=html:docs/_build/html/coverage${NVX_SUFFIX}

    echo "--> Coverage report generated in docs/_build/html/coverage${NVX_SUFFIX}/index.html"

# Run all checks in single environment (usage: `just check cpy314`)
check venv="": (check-format venv) (check-typing venv) (check-coverage-combined venv)

# -----------------------------------------------------------------------------
# -- Unit tests
# -----------------------------------------------------------------------------

# Run the test suite for Twisted/trial and asyncio/pytest (usage: `just test cpy314`)
test venv="" use_nvx="": (test-twisted venv use_nvx) (test-asyncio venv use_nvx)

# Run the test suite for Twisted using trial (usage: `just test-twisted cpy314`)
test-twisted venv="" use_nvx="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")

    # Handle NVX configuration
    USE_NVX="{{ use_nvx }}"
    if [ "${USE_NVX}" = "1" ]; then
        export AUTOBAHN_USE_NVX=1
        echo "==> Running test suite for Twisted using trial in ${VENV_NAME} (WITH NVX)..."
    elif [ "${USE_NVX}" = "0" ]; then
        export AUTOBAHN_USE_NVX=0
        echo "==> Running test suite for Twisted using trial in ${VENV_NAME} (WITHOUT NVX)..."
    else
        echo "==> Running test suite for Twisted using trial in ${VENV_NAME} (AUTO NVX)..."
    fi

    # IMPORTANT: Twisted trial doesn't allow to recurse-and-exclude, and hence we
    # need this looong explicit list of tests to run because we must exclude "asyncio"
    #
    # AUTOBAHN_CI_ENABLE_RNG_DEPLETION_TESTS=1:
    #   This enables "autobahn/test/test_rng.py" (on Linux), which tests entropy depletion,
    #   and tests how to correctly read _real_ entropy and block if not enough _real_ entropy
    #   is currently available (see: https://github.com/crossbario/autobahn-python/issues/1275)

    USE_TWISTED=1 ${VENV_PYTHON} -m twisted.trial --no-recurse \
        autobahn.test \
        autobahn.twisted.test \
        autobahn.websocket.test \
        autobahn.rawsocket.test \
        autobahn.wamp.test \
        autobahn.nvx.test

# Run the test suite for asyncio using pytest (usage: `just test-asyncio cpy314`)
test-asyncio venv="" use_nvx="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")

    # Handle NVX configuration
    USE_NVX="{{ use_nvx }}"
    if [ "${USE_NVX}" = "1" ]; then
        export AUTOBAHN_USE_NVX=1
        echo "==> Running test suite for asyncio using pytest in ${VENV_NAME} (WITH NVX)..."
    elif [ "${USE_NVX}" = "0" ]; then
        export AUTOBAHN_USE_NVX=0
        echo "==> Running test suite for asyncio using pytest in ${VENV_NAME} (WITHOUT NVX)..."
    else
        echo "==> Running test suite for asyncio using pytest in ${VENV_NAME} (AUTO NVX)..."
    fi

    # IMPORTANT: we need to exclude all twisted tests
    USE_ASYNCIO=1 ${VENV_PYTHON} -m pytest -s -v -rfP \
        --ignore=./autobahn/twisted ./autobahn

# -----------------------------------------------------------------------------
# -- Documentation
# -----------------------------------------------------------------------------

# Build the HTML documentation using Sphinx
docs venv="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    if [ ! -d "${VENV_PATH}" ]; then
        just install-tools ${VENV_NAME}
    fi
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Building documentation..."
    "${VENV_PATH}/bin/sphinx-build" -b html docs/ docs/_build/html

docs-view venv="": (docs venv)
    echo "==> Opening documentation in viewer ..."
    open docs/_build/html/index.html

# Clean the generated documentation
docs-clean:
    echo "==> Cleaning documentation build artifacts..."
    rm -rf docs/_build

# -----------------------------------------------------------------------------
# -- Building and Publishing
# -----------------------------------------------------------------------------

# Build distribution packages (wheels and source tarball)
build venv="": (install-build-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Building distribution packages..."
    # Set environment variable for NVX acceleration
    AUTOBAHN_USE_NVX=1 ${VENV_PYTHON} -m build
    ls -la dist/

# Meta-recipe to run `build` on all environments
build-all:
    #!/usr/bin/env bash
    for venv in {{ENVS}}; do
        just build ${venv}
    done
    ls -la dist/

# Download release artifacts from GitHub and publish to PyPI
publish-pypi venv="" tag="":
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    # Determine which tag to use
    TAG="{{ tag }}"
    if [ -z "${TAG}" ]; then
        echo "==> No tag specified. Using latest git tag..."
        TAG=$(git describe --tags --abbrev=0)
        echo "==> Using tag: ${TAG}"
    fi

    # Verify tag looks like a version tag
    if [[ ! "${TAG}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "❌ Error: Tag '${TAG}' doesn't look like a version tag (expected format: vX.Y.Z)"
        exit 1
    fi

    # Create temp directory for downloads
    TEMP_DIR=$(mktemp -d)
    echo "==> Downloading release artifacts from GitHub release ${TAG}..."
    echo "    Temp directory: ${TEMP_DIR}"

    # Download all release assets
    gh release download "${TAG}" --repo crossbario/autobahn-python --dir "${TEMP_DIR}"

    echo ""
    echo "==> Downloaded files:"
    ls -lh "${TEMP_DIR}"
    echo ""

    # Count wheels and source distributions
    WHEEL_COUNT=$(find "${TEMP_DIR}" -name "*.whl" | wc -l)
    SDIST_COUNT=$(find "${TEMP_DIR}" -name "*.tar.gz" | wc -l)

    echo "Found ${WHEEL_COUNT} wheel(s) and ${SDIST_COUNT} source distribution(s)"

    if [ "${WHEEL_COUNT}" -eq 0 ] || [ "${SDIST_COUNT}" -eq 0 ]; then
        echo "❌ Error: Expected at least 1 wheel and 1 source distribution"
        echo "    Wheels found: ${WHEEL_COUNT}"
        echo "    Source dist found: ${SDIST_COUNT}"
        rm -rf "${TEMP_DIR}"
        exit 1
    fi

    # Ensure twine is installed
    if [ ! -f "${VENV_PATH}/bin/twine" ]; then
        echo "==> Installing twine in ${VENV_NAME}..."
        "${VENV_PATH}/bin/pip" install twine
    fi

    echo "==> Publishing to PyPI using twine..."
    "${VENV_PATH}/bin/twine" upload "${TEMP_DIR}"/*.whl "${TEMP_DIR}"/*.tar.gz

    # Cleanup
    rm -rf "${TEMP_DIR}"
    echo "✅ Successfully published ${TAG} to PyPI"

# Trigger Read the Docs build for a specific tag
publish-rtd tag="":
    #!/usr/bin/env bash
    set -e

    # Determine which tag to use
    TAG="{{ tag }}"
    if [ -z "${TAG}" ]; then
        echo "==> No tag specified. Using latest git tag..."
        TAG=$(git describe --tags --abbrev=0)
        echo "==> Using tag: ${TAG}"
    fi

    # Verify tag looks like a version tag
    if [[ ! "${TAG}" =~ ^v[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
        echo "❌ Error: Tag '${TAG}' doesn't look like a version tag (expected format: vX.Y.Z)"
        exit 1
    fi

    # Check if RTD_TOKEN is set
    if [ -z "${RTD_TOKEN}" ]; then
        echo "❌ Error: RTD_TOKEN environment variable is not set"
        echo ""
        echo "To trigger RTD builds, you need to:"
        echo "1. Get an API token from https://readthedocs.org/accounts/tokens/"
        echo "2. Export it: export RTD_TOKEN=your_token_here"
        echo ""
        exit 1
    fi

    echo "==> Triggering Read the Docs build for ${TAG}..."
    echo ""

    # Trigger build via RTD API
    # See: https://docs.readthedocs.io/en/stable/api/v3.html#post--api-v3-projects-(string-project_slug)-versions-(string-version_slug)-builds-
    RTD_PROJECT="autobahnpython"
    RTD_API_URL="https://readthedocs.org/api/v3/projects/${RTD_PROJECT}/versions/${TAG}/builds/"

    echo "==> Calling RTD API..."
    echo "    Project: ${RTD_PROJECT}"
    echo "    Version: ${TAG}"
    echo "    URL: ${RTD_API_URL}"
    echo ""

    # Trigger the build
    HTTP_CODE=$(curl -X POST \
        -H "Authorization: Token ${RTD_TOKEN}" \
        -w "%{http_code}" \
        -s -o /tmp/rtd_response.json \
        "${RTD_API_URL}")

    echo "==> API Response (HTTP ${HTTP_CODE}):"
    cat /tmp/rtd_response.json | python3 -m json.tool 2>/dev/null || cat /tmp/rtd_response.json
    echo ""

    if [ "${HTTP_CODE}" = "202" ] || [ "${HTTP_CODE}" = "201" ]; then
        echo "✅ Read the Docs build triggered successfully!"
        echo ""
        echo "Check build status at:"
        echo "  https://readthedocs.org/projects/${RTD_PROJECT}/builds/"
        echo ""
        echo "Documentation will be available at:"
        echo "  https://${RTD_PROJECT}.readthedocs.io/en/${TAG}/"
        echo "  https://${RTD_PROJECT}.readthedocs.io/en/stable/ (if marked as stable)"
        echo ""
    else
        echo "❌ Error: Failed to trigger RTD build (HTTP ${HTTP_CODE})"
        echo ""
        echo "Common issues:"
        echo "- Invalid RTD_TOKEN"
        echo "- Version/tag doesn't exist in RTD project"
        echo "- Network/API connectivity problems"
        echo ""
        exit 1
    fi

    rm -f /tmp/rtd_response.json

# Publish to both PyPI and Read the Docs (meta-recipe)
publish venv="" tag="": (publish-pypi venv tag) (publish-rtd tag)
    #!/usr/bin/env bash
    set -e
    TAG="{{ tag }}"
    if [ -z "${TAG}" ]; then
        TAG=$(git describe --tags --abbrev=0)
    fi
    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "✅ Successfully published version ${TAG}"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "📦 PyPI: https://pypi.org/project/autobahn/${TAG#v}/"
    echo "📚 RTD:  https://autobahnpython.readthedocs.io/en/${TAG}/"
    echo ""

# -----------------------------------------------------------------------------
# -- FlatBuffers Schema Generation
# -----------------------------------------------------------------------------

# Install latest FlatBuffers compiler (flatc) to /usr/local/bin
install-flatc:
    #!/usr/bin/env bash
    set -e
    FLATC_VERSION="25.9.23"
    FLATC_URL="https://github.com/google/flatbuffers/releases/download/v${FLATC_VERSION}/Linux.flatc.binary.g++-13.zip"
    TEMP_DIR=$(mktemp -d)

    echo "==> Installing FlatBuffers compiler v${FLATC_VERSION}..."
    echo "    URL: ${FLATC_URL}"
    echo "    Temp dir: ${TEMP_DIR}"

    # Download and extract
    cd "${TEMP_DIR}"
    curl -L -o flatc.zip "${FLATC_URL}"
    unzip flatc.zip

    # Install to /usr/local/bin (requires sudo)
    echo "==> Installing flatc to /usr/local/bin (requires sudo)..."
    sudo mv flatc /usr/local/bin/flatc
    sudo chmod +x /usr/local/bin/flatc

    # Cleanup
    rm -rf "${TEMP_DIR}"

    # Verify installation
    echo "==> Verification:"
    flatc --version
    echo "✅ FlatBuffers compiler v${FLATC_VERSION} installed successfully!"

# Clean generated FlatBuffers files
clean-fbs:
    echo "==> Cleaning FlatBuffers generated files..."
    rm -rf ./autobahn/wamp/gen/

# Build FlatBuffers schema files and Python bindings
build-fbs venv="": (install-tools venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"

    FBSFILES="./autobahn/wamp/flatbuffers/*.fbs"
    FLATC="flatc"
    echo "==> Generating FlatBuffers binary schema and Python wrappers using $(${FLATC} --version)..."

    # Generate schema binary type library (*.bfbs files)
    ${FLATC} -o ./autobahn/wamp/gen/schema/ --binary --schema --bfbs-comments --bfbs-builtins ${FBSFILES}
    echo "--> Generated $(find ./autobahn/wamp/gen/schema/ -name '*.bfbs' | wc -l) .bfbs files"

    # Generate schema Python bindings (*.py files)
    ${FLATC} -o ./autobahn/wamp/gen/ --python ${FBSFILES}
    touch ./autobahn/wamp/gen/__init__.py
    echo "--> Generated $(find ./autobahn/wamp/gen/ -name '*.py' | wc -l) .py files"

    echo "Auto-formatting code using ruff after flatc code generation .."
    "${VENV_PATH}/bin/ruff" format ./autobahn/wamp/gen/
    "${VENV_PATH}/bin/ruff" check --fix ./autobahn/wamp/gen/

# -----------------------------------------------------------------------------
# -- File Management Utilities
# -----------------------------------------------------------------------------

# Rename audit files to replace ':' with '_' for Windows compatibility
fix-audit-filenames:
    #!/usr/bin/env bash
    set -e

    echo "==> Renaming audit files to replace ':' with '_' for Windows compatibility..."

    # Check if .audit directory exists
    if [ ! -d ".audit" ]; then
        echo "No .audit directory found, nothing to rename."
        exit 0
    fi

    # Count files that need renaming
    FILES_TO_RENAME=$(find .audit -name "*:*" -type f | wc -l)

    if [ "$FILES_TO_RENAME" -eq 0 ]; then
        echo "No files with ':' characters found in .audit directory."
        exit 0
    fi

    echo "Found $FILES_TO_RENAME files to rename:"
    find .audit -name "*:*" -type f
    echo ""

    # Rename files
    find .audit -name "*:*" -type f | while read -r file; do
        # Get directory and filename
        dir=$(dirname "$file")
        filename=$(basename "$file")

        # Replace : with _
        new_filename="${filename//:/_}"
        new_file="$dir/$new_filename"

        echo "Renaming: $filename -> $new_filename"
        mv "$file" "$new_file"
    done

    echo ""
    echo "==> Renaming complete! Updated files:"
    ls -la .audit/
    echo ""
    echo "These files are now Windows-compatible."

# -----------------------------------------------------------------------------
# -- WebSocket compliance testing
# -----------------------------------------------------------------------------

# Run Autobahn WebSocket Testsuite in fuzzingserver mode.
wstest-fuzzingserver config_dir="" output_dir="" mode="quick":
    #!/usr/bin/env bash
    set -e
    CONFIG_DIR="{{ config_dir }}"
    if [ -z "${CONFIG_DIR}" ]; then
        echo "==> No wstest config directory specified. Using default {{AUTOBAHN_TESTSUITE_CONFIG_DIR}}..."
        CONFIG_DIR="{{AUTOBAHN_TESTSUITE_CONFIG_DIR}}"
    fi
    OUTPUT_DIR="{{ output_dir }}"
    if [ -z "${OUTPUT_DIR}" ]; then
        echo "==> No wstest output directory specified. Using default {{AUTOBAHN_TESTSUITE_OUTPUT_DIR}}..."
        OUTPUT_DIR="{{AUTOBAHN_TESTSUITE_OUTPUT_DIR}}"
    fi
    TEST_MODE="{{ mode }}"
    if [ "${TEST_MODE}" != "quick" ] && [ "${TEST_MODE}" != "full" ]; then
        echo "Error: mode must be 'quick' or 'full', got: ${TEST_MODE}"
        exit 1
    fi
    echo ""
    echo "Using Docker image: {{AUTOBAHN_TESTSUITE_IMAGE}}"
    echo "Using config directory: ${CONFIG_DIR}"
    echo "Using output directory: ${OUTPUT_DIR}"
    echo "Using test mode: ${TEST_MODE}"
    echo ""
    sudo docker run -i --rm \
        -v "${CONFIG_DIR}:/config" \
        -v "${OUTPUT_DIR}:/reports" \
        -p 9001:9001 \
        --name fuzzingserver \
        "{{AUTOBAHN_TESTSUITE_IMAGE}}" \
        wstest -m fuzzingserver -s /config/fuzzingserver-${TEST_MODE}.json

# Run Autobahn|Testsuite in fuzzingclient mode (tests autobahn-python servers)
wstest-fuzzingclient config_dir="" output_dir="" mode="quick":
    #!/usr/bin/env bash
    set -e
    CONFIG_DIR="{{ config_dir }}"
    if [ -z "${CONFIG_DIR}" ]; then
        echo "==> No wstest config directory specified. Using default {{AUTOBAHN_TESTSUITE_CONFIG_DIR}}..."
        CONFIG_DIR="{{AUTOBAHN_TESTSUITE_CONFIG_DIR}}"
    fi
    OUTPUT_DIR="{{ output_dir }}"
    if [ -z "${OUTPUT_DIR}" ]; then
        echo "==> No wstest output directory specified. Using default {{AUTOBAHN_TESTSUITE_OUTPUT_DIR}}..."
        OUTPUT_DIR="{{AUTOBAHN_TESTSUITE_OUTPUT_DIR}}"
    fi
    TEST_MODE="{{ mode }}"
    if [ "${TEST_MODE}" != "quick" ] && [ "${TEST_MODE}" != "full" ]; then
        echo "Error: mode must be 'quick' or 'full', got: ${TEST_MODE}"
        exit 1
    fi
    echo "==> Creating wstest output directory: ${OUTPUT_DIR}"
    mkdir -p "${OUTPUT_DIR}"
    echo "==> Pulling Autobahn|Testsuite Docker image..."
    sudo docker pull "{{AUTOBAHN_TESTSUITE_IMAGE}}"
    echo "==> Running Autobahn|Testsuite in fuzzingclient mode..."
    echo "==> Using test mode: ${TEST_MODE}"
    # for now, ignore any non-zero exit code by prefixing with hyphen (FIXME: remove later)
    sudo docker run -i --rm \
        --network host \
        -v "${CONFIG_DIR}":/config \
        -v "${OUTPUT_DIR}":/reports \
        --name fuzzingclient \
        "{{AUTOBAHN_TESTSUITE_IMAGE}}" \
        wstest -m fuzzingclient -s /config/fuzzingclient-${TEST_MODE}.json

# Run Autobahn|Python WebSocket client on Twisted
wstest-testeeclient-twisted venv="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Running Autobahn|Python WebSocket client on Twisted in ${VENV_NAME}..."

    ${VENV_PYTHON} ./wstest/testee_client_tx.py

# Run Autobahn|Python WebSocket client on asyncio
wstest-testeeclient-asyncio venv="": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Running Autobahn|Python WebSocket client on asyncio in ${VENV_NAME}..."

    ${VENV_PYTHON} ./wstest/testee_client_aio.py

# Run Autobahn|Python WebSocket server on Twisted
wstest-testeeserver-twisted venv="" url="ws://127.0.0.1:9011": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Running Autobahn|Python WebSocket server on Twisted in ${VENV_NAME} at {{ url }}..."
    ${VENV_PYTHON} ./wstest/testee_server_tx.py --url "{{ url }}"

# Run Autobahn|Python WebSocket server on asyncio
wstest-testeeserver-asyncio venv="" url="ws://127.0.0.1:9012": (install-tools venv) (install venv)
    #!/usr/bin/env bash
    set -e
    VENV_NAME="{{ venv }}"
    if [ -z "${VENV_NAME}" ]; then
        echo "==> No venv name specified. Auto-detecting from system Python..."
        VENV_NAME=$(just --quiet _get-system-venv-name)
        echo "==> Defaulting to venv: '${VENV_NAME}'"
    fi
    VENV_PATH="{{ VENV_DIR }}/${VENV_NAME}"
    VENV_PYTHON=$(just --quiet _get-venv-python "${VENV_NAME}")
    echo "==> Running Autobahn|Python WebSocket server on asyncio in ${VENV_NAME} at {{ url }}..."
    ${VENV_PYTHON} ./wstest/testee_server_aio.py --url "{{ url }}"

# Consolidate WebSocket test reports for local documentation
wstest-consolidate-reports:
    #!/usr/bin/env bash
    set -e
    echo "==> Consolidating WebSocket conformance test reports for documentation..."

    # Ensure target directories exists
    mkdir -p docs/_static/websocket/conformance
    mkdir -p docs/_static/websocket/conformance/clients
    mkdir -p docs/_static/websocket/conformance/servers

    # Copy client and server HTML reports to docs/_static
    if [ -d ".wstest/clients" ]; then
        echo "==> Copying client test reports..."
        cp -r .wstest/clients/* docs/_static/websocket/conformance/clients/ || true
    else
        echo "⚠️  No client test reports found in .wstest/clients"
    fi

    if [ -d ".wstest/servers" ]; then
        echo "==> Copying server test reports..."
        cp -r .wstest/servers/* docs/_static/websocket/conformance/servers/ || true
    else
        echo "⚠️  No server test reports found in .wstest/servers"
    fi

    # Create ZIP archive of all clients JSON test reports
    echo "==> Creating clients JSON reports archive..."
    find docs/_static/websocket/conformance/clients -name "*.json" -type f > json_files.txt
    if [ -s json_files.txt ]; then
        json_count=$(wc -l < json_files.txt)
        echo "Found ${json_count} clients JSON test report files"
        zip -r "docs/_static/websocket/conformance/autobahn-python-websocket-client-conformance.zip" -@ < json_files.txt
        echo "✅ Created autobahn-python-websocket-client-conformance.zip with ${json_count} JSON files"
        rm json_files.txt
    else
        echo "⚠️  No clients JSON test report files found"
        rm -f json_files.txt
    fi

    # Create ZIP archive of all servers JSON test reports
    echo "==> Creating servers JSON reports archive..."
    find docs/_static/websocket/conformance/servers -name "*.json" -type f > json_files.txt
    if [ -s json_files.txt ]; then
        json_count=$(wc -l < json_files.txt)
        echo "Found ${json_count} servers JSON test report files"
        zip -r "docs/_static/websocket/conformance/autobahn-python-websocket-server-conformance.zip" -@ < json_files.txt
        echo "✅ Created autobahn-python-websocket-server-conformances.zip with ${json_count} JSON files"
        rm json_files.txt
    else
        echo "⚠️  No servers JSON test report files found"
        rm -f json_files.txt
    fi

    echo "✅ Test reports consolidated for documentation"
    echo "📄 HTML reports: docs/_static/websocket/conformance/"

    sync docs/_static/websocket/conformance/
    du -hs docs/_static/websocket/conformance/

# Download GitHub release artifacts (usage: `just download-github-release` for nightly, or `just download-github-release stable`)
download-github-release release_type="nightly":
    #!/usr/bin/env bash
    set -e

    RELEASE_TYPE="{{ release_type }}"
    echo "==> Downloading GitHub release artifacts for: ${RELEASE_TYPE}"
    echo ""

    # Determine which release tag to download
    case "${RELEASE_TYPE}" in
        nightly)
            echo "==> Finding latest nightly release (tagged as master-YYYYMMDDHHMM)..."
            RELEASE_TAG=$(curl -s "https://api.github.com/repos/crossbario/autobahn-python/releases" \
              | grep '"tag_name":' \
              | grep -o 'master-[0-9]*' \
              | head -1)
            if [ -z "$RELEASE_TAG" ]; then
                echo "❌ ERROR: No nightly release found"
                exit 1
            fi
            echo "✅ Found nightly release: $RELEASE_TAG"
            ;;

        stable|latest)
            echo "==> Finding latest stable release..."
            RELEASE_TAG=$(curl -s "https://api.github.com/repos/crossbario/autobahn-python/releases/latest" \
              | grep '"tag_name":' \
              | sed 's/.*"tag_name": "\([^"]*\)".*/\1/')
            if [ -z "$RELEASE_TAG" ]; then
                echo "❌ ERROR: No stable release found"
                exit 1
            fi
            echo "✅ Found stable release: $RELEASE_TAG"
            ;;

        development|dev)
            echo "==> Finding latest development release (tagged as fork-*)..."
            RELEASE_TAG=$(curl -s "https://api.github.com/repos/crossbario/autobahn-python/releases" \
              | grep '"tag_name":' \
              | grep -o 'fork-[^"]*' \
              | head -1)
            if [ -z "$RELEASE_TAG" ]; then
                echo "❌ ERROR: No development release found"
                exit 1
            fi
            echo "✅ Found development release: $RELEASE_TAG"
            ;;

        *)
            # Treat as explicit tag name
            RELEASE_TAG="${RELEASE_TYPE}"
            echo "==> Using explicit release tag: $RELEASE_TAG"
            ;;
    esac

    BASE_URL="https://github.com/crossbario/autobahn-python/releases/download/${RELEASE_TAG}"

    # Create temporary directory for artifacts
    DOWNLOAD_DIR="/tmp/autobahn-release-artifacts-${RELEASE_TAG}"
    mkdir -p "${DOWNLOAD_DIR}"
    cd "${DOWNLOAD_DIR}"

    echo ""
    echo "==> Downloading WebSocket conformance reports..."
    if curl -fL "${BASE_URL}/autobahn-python-websocket-conformance-${RELEASE_TAG}.tar.gz" \
        -o conformance.tar.gz; then
        echo "✅ Downloaded: autobahn-python-websocket-conformance-${RELEASE_TAG}.tar.gz"
    else
        echo "⚠️  Failed to download conformance reports (may not exist for this release)"
    fi

    echo ""
    echo "==> Downloading FlatBuffers schemas..."
    if curl -fL "${BASE_URL}/flatbuffers-schema.tar.gz" \
        -o flatbuffers-schema.tar.gz; then
        echo "✅ Downloaded: flatbuffers-schema.tar.gz"
    else
        echo "⚠️  Failed to download FlatBuffers schemas (may not exist for this release)"
    fi

    echo ""
    echo "==> Extracting artifacts..."
    if [ -f conformance.tar.gz ]; then
        tar -xzf conformance.tar.gz
        echo "✅ Extracted conformance reports"
    fi
    if [ -f flatbuffers-schema.tar.gz ]; then
        tar -xzf flatbuffers-schema.tar.gz
        echo "✅ Extracted FlatBuffers schemas"
    fi

    echo ""
    echo "==> Downloaded and extracted artifacts:"
    ls -lh

    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "✅ Artifacts downloaded to: ${DOWNLOAD_DIR}"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Release: ${RELEASE_TAG}"
    echo "Location: ${DOWNLOAD_DIR}"
    echo ""
    echo "To use these artifacts:"
    echo "  - Conformance reports: ${DOWNLOAD_DIR}/with-nvx/, ${DOWNLOAD_DIR}/without-nvx/"
    echo "  - FlatBuffers schemas: ${DOWNLOAD_DIR}/*.fbs, ${DOWNLOAD_DIR}/*.bfbs"
    echo ""

# Integrate downloaded GitHub release artifacts into docs build (usage: `just docs-integrate-github-release` or `just docs-integrate-github-release master-202510180103`)
docs-integrate-github-release release_tag="":
    #!/usr/bin/env bash
    set -e

    RELEASE_TAG="{{ release_tag }}"

    # Check that docs have been built first
    if [ ! -d "docs/_build/html" ]; then
        echo "❌ ERROR: Documentation not built yet"
        echo ""
        echo "Please build documentation first using:"
        echo "  just docs"
        echo ""
        echo "Then integrate artifacts with:"
        echo "  just docs-integrate-github-release"
        echo ""
        exit 1
    fi

    # If no tag specified, find the most recently downloaded artifacts
    if [ -z "${RELEASE_TAG}" ]; then
        echo "==> No release tag specified. Finding latest downloaded artifacts..."
        LATEST_DIR=$(find /tmp -maxdepth 1 -type d -name "autobahn-release-artifacts-*" -printf "%T@ %p\n" 2>/dev/null \
          | sort -rn \
          | head -1 \
          | cut -d' ' -f2-)

        if [ -z "${LATEST_DIR}" ]; then
            echo "❌ ERROR: No downloaded release artifacts found in /tmp/"
            echo ""
            echo "Please download artifacts first using:"
            echo "  just download-github-release"
            echo ""
            exit 1
        fi

        RELEASE_TAG=$(basename "${LATEST_DIR}" | sed 's/autobahn-release-artifacts-//')
        echo "✅ Found latest downloaded artifacts: ${RELEASE_TAG}"
    fi

    DOWNLOAD_DIR="/tmp/autobahn-release-artifacts-${RELEASE_TAG}"

    if [ ! -d "${DOWNLOAD_DIR}" ]; then
        echo "❌ ERROR: Release artifacts not found at: ${DOWNLOAD_DIR}"
        echo ""
        echo "Please download artifacts first using:"
        echo "  just download-github-release ${RELEASE_TAG}"
        echo ""
        exit 1
    fi

    echo "==> Integrating GitHub release artifacts into built documentation..."
    echo "    Release: ${RELEASE_TAG}"
    echo "    Source: ${DOWNLOAD_DIR}"
    echo "    Target: docs/_build/html/_static/"
    echo ""

    # Create target directories in the BUILT docs
    echo "==> Creating target directories in docs/_build/html/_static/..."
    mkdir -p docs/_build/html/_static/websocket/conformance/with-nvx
    mkdir -p docs/_build/html/_static/websocket/conformance/without-nvx
    mkdir -p docs/_build/html/_static/flatbuffers

    # Copy conformance reports (with-nvx)
    if [ -d "${DOWNLOAD_DIR}/with-nvx" ]; then
        echo "==> Copying conformance reports (with NVX)..."
        cp -r "${DOWNLOAD_DIR}/with-nvx"/* docs/_build/html/_static/websocket/conformance/with-nvx/ 2>/dev/null || true
        FILE_COUNT=$(find docs/_build/html/_static/websocket/conformance/with-nvx -type f | wc -l)
        echo "✅ Copied ${FILE_COUNT} files to docs/_build/html/_static/websocket/conformance/with-nvx/"
    else
        echo "⚠️  No with-nvx conformance reports found in ${DOWNLOAD_DIR}"
    fi

    # Copy conformance reports (without-nvx)
    if [ -d "${DOWNLOAD_DIR}/without-nvx" ]; then
        echo "==> Copying conformance reports (without NVX)..."
        cp -r "${DOWNLOAD_DIR}/without-nvx"/* docs/_build/html/_static/websocket/conformance/without-nvx/ 2>/dev/null || true
        FILE_COUNT=$(find docs/_build/html/_static/websocket/conformance/without-nvx -type f | wc -l)
        echo "✅ Copied ${FILE_COUNT} files to docs/_build/html/_static/websocket/conformance/without-nvx/"
    else
        echo "⚠️  No without-nvx conformance reports found in ${DOWNLOAD_DIR}"
    fi

    # Copy FlatBuffers schemas (source .fbs files)
    echo "==> Copying FlatBuffers source schemas (.fbs)..."
    if [ -d "${DOWNLOAD_DIR}/flatbuffers" ]; then
        # New structure: .fbs files are in flatbuffers/ subdirectory
        FBS_COUNT=$(find "${DOWNLOAD_DIR}/flatbuffers" -name "*.fbs" -type f 2>/dev/null | wc -l)
        if [ "${FBS_COUNT}" -gt 0 ]; then
            cp "${DOWNLOAD_DIR}/flatbuffers"/*.fbs docs/_build/html/_static/flatbuffers/ 2>/dev/null || true
            echo "✅ Copied ${FBS_COUNT} .fbs files to docs/_build/html/_static/flatbuffers/"
        else
            echo "⚠️  No .fbs files found in ${DOWNLOAD_DIR}/flatbuffers"
        fi
    else
        # Legacy structure: .fbs files in top-level directory
        FBS_COUNT=$(find "${DOWNLOAD_DIR}" -maxdepth 1 -name "*.fbs" -type f 2>/dev/null | wc -l)
        if [ "${FBS_COUNT}" -gt 0 ]; then
            cp "${DOWNLOAD_DIR}"/*.fbs docs/_build/html/_static/flatbuffers/ 2>/dev/null || true
            echo "✅ Copied ${FBS_COUNT} .fbs files to docs/_build/html/_static/flatbuffers/"
        else
            echo "⚠️  No .fbs files found in ${DOWNLOAD_DIR}"
        fi
    fi

    # Copy FlatBuffers binary schemas (.bfbs files)
    echo "==> Copying FlatBuffers binary schemas (.bfbs)..."
    if [ -d "${DOWNLOAD_DIR}/gen/schema" ]; then
        # New structure: .bfbs files are in gen/schema/ subdirectory
        BFBS_COUNT=$(find "${DOWNLOAD_DIR}/gen/schema" -name "*.bfbs" -type f 2>/dev/null | wc -l)
        if [ "${BFBS_COUNT}" -gt 0 ]; then
            cp "${DOWNLOAD_DIR}/gen/schema"/*.bfbs docs/_build/html/_static/flatbuffers/ 2>/dev/null || true
            echo "✅ Copied ${BFBS_COUNT} .bfbs files to docs/_build/html/_static/flatbuffers/"
        else
            echo "⚠️  No .bfbs files found in ${DOWNLOAD_DIR}/gen/schema"
        fi
    else
        # Legacy structure: .bfbs files in top-level directory
        BFBS_COUNT=$(find "${DOWNLOAD_DIR}" -maxdepth 1 -name "*.bfbs" -type f 2>/dev/null | wc -l)
        if [ "${BFBS_COUNT}" -gt 0 ]; then
            cp "${DOWNLOAD_DIR}"/*.bfbs docs/_build/html/_static/flatbuffers/ 2>/dev/null || true
            echo "✅ Copied ${BFBS_COUNT} .bfbs files to docs/_build/html/_static/flatbuffers/"
        else
            echo "⚠️  No .bfbs files found in ${DOWNLOAD_DIR}"
        fi
    fi

    echo ""
    echo "════════════════════════════════════════════════════════════"
    echo "✅ GitHub release artifacts integrated into built documentation"
    echo "════════════════════════════════════════════════════════════"
    echo ""
    echo "Integrated artifacts from: ${RELEASE_TAG}"
    echo "Target location: docs/_build/html/_static/"
    echo ""
    echo "Next steps:"
    echo "  1. View documentation: just docs-view"
    echo "  2. Check conformance reports at: http://localhost:8000/websocket/conformance.html"
    echo "  3. Check FlatBuffers schemas at: http://localhost:8000/wamp/serialization.html"
    echo ""
