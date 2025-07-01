# === justfile ===

# Define a variable for all your environments
ENVS := 'cpy312 cpy311 cpy310 pypy310 pypy311'

# List of all recipes
default:
    @just --list

# Create a single Python virtual environment (usage: `just venv cpy312`)
venv env:
    #!/usr/bin/env bash
    set -e
    # A simple case statement is much clearer than make's variable magic
    case {{env}} in
        cpy312) python_exe="python3.12";;
        cpy311) python_exe="python3.11";;
        cpy310) python_exe="python3.10";;
        pypy310) python_exe="pypy3.10";;
        pypy311) python_exe="pypy3.11";;
        *) echo "Unknown environment: {{env}}"; exit 1;;
    esac
    echo "==> Creating virtual environment for {{env}}..."
    uv venv --python ${python_exe} .venv-{{env}}

# Get the version of a single virtual environment's Python (usage: `just version cpy312`)
version env: (venv env)
    echo "==> Getting Python version for environment {{env}}..."
    ./.venv-{{env}}/bin/python -V

# Get versions of all Python virtual environments
version-all:
    #!/usr/bin/env bash
    for env in {{ENVS}}; do
        just version ${env}
    done
