# --- Makefile.working ---

# =============================================================================
#  CONFIGURATION
# =============================================================================
ENVS := cpy312 cpy311 cpy310 pypy310 pypy311

PYTHON_INTERPRETER_cpy312 := python3.12
PYTHON_INTERPRETER_cpy311 := python3.11
PYTHON_INTERPRETER_cpy310 := python3.10
PYTHON_INTERPRETER_pypy310 := pypy3.10
PYTHON_INTERPRETER_pypy311 := pypy3.11

# =============================================================================
#  VIRTUAL ENVIRONMENT RULE (The missing piece)
#  This rule is REQUIRED by the version-% rule below.
# =============================================================================
.PHONY: venv-all $(addprefix venv-,$(ENVS))

venv-all: $(addprefix venv-,$(ENVS))

# This is the rule that was missing from your minimal example.
venv-%:
	@echo "==> Creating virtual environment for '$*'..."
	uv venv --python $(PYTHON_INTERPRETER_$(*)) .venv-$(*)

# =============================================================================
#  VERSIONS RULE (Your existing, correct code)
# =============================================================================
.PHONY: version-all $(addprefix version-,$(ENVS))

version-all: $(addprefix version-,$(ENVS))

version-%: venv-%
	@echo "==> Getting Python version for environment '$*'..."
	./.venv-$(*)/bin/python -V
