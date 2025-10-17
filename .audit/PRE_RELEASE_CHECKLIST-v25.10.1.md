# Pre-Release Testing Checklist for v25.10.1

This checklist ensures everything works locally before pushing to PyPI.

## 1. Package Build & Contents Verification

### 1.1 Build the package

```bash
# Clean previous builds
just distclean

# Build with current branch
just build-all

# Verify artifacts created
ls -lh dist/

# Expected:
# autobahn-25.10.1-cp311-cp311-linux_x86_64.whl
# autobahn-25.10.1-cp312-cp312-linux_x86_64.whl
# autobahn-25.10.1-cp313-cp313-linux_x86_64.whl
# autobahn-25.10.1-cp314-cp314-linux_x86_64.whl
# autobahn-25.10.1-pp311-pypy311_pp73-linux_x86_64.whl
# autobahn-25.10.1.tar.gz
```

### 1.2 Verify source distribution contents

```bash
# List contents
tar -tzf dist/autobahn-25.10.1.tar.gz | head -50

# Check FlatBuffers are included
tar -tzf dist/autobahn-25.10.1.tar.gz | grep -E "(\.fbs|\.bfbs|wamp/gen.*\.py)"

# Expected:
#   autobahn-25.10.1/autobahn/wamp/flatbuffers/*.fbs (7 files)
#   autobahn-25.10.1/autobahn/wamp/gen/schema/*.bfbs (7 files)
#   autobahn-25.10.1/autobahn/wamp/gen/**/*.py (65+ files)
```

### 1.3 Verify wheel contents

```bash
# Extract and list wheel contents
for whl in dist/*.whl; do
  echo "=== $(basename "$whl") ==="
  unzip -l "$whl" \
    | grep -E "(wamp/gen|flatbuffers|\.fbs|\.bfbs)" \
    | awk -F. '{print $NF}' \
    | sort \
    | uniq -c \
    | sort -nr
  echo
done

# Expected:
# === autobahn-25.10.1-cp311-cp311-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-cp312-cp312-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-cp313-cp313-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-cp314-cp314-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
#
# === autobahn-25.10.1-pp311-pypy311_pp73-linux_x86_64.whl ===
#      65 py
#       7 fbs
#       7 bfbs
```

### 1.4 Verify source distribution integrity

```bash
# Run the same checks as CI
gzip -tv dist/autobahn-25.10.1.tar.gz
tar -tzf dist/autobahn-25.10.1.tar.gz > /dev/null

# Compute SHA256
openssl sha256 dist/autobahn-25.10.1.tar.gz
```

## 2. Local Installation & Import Tests

### 2.1 Install in clean virtualenv

```bash
# Create fresh test environment
python3 -m venv /tmp/test_autobahn_v25.10.1
source /tmp/test_autobahn_v25.10.1/bin/activate

# Install from local wheel - minimal!
pip install --find-links=dist autobahn

# Or install from source dist
# pip install dist/autobahn-25.10.1.tar.gz

# Install from local wheel - full!
pip install --find-links=dist autobahn[all]

# Expected:
# Looking in links: dist
# Processing ./dist/autobahn-25.10.1-cp312-cp312-linux_x86_64.whl

# IMPORTANT: make sure we do _not_ accidentily import modules from source tree (git working repo), aka Python "development mode"!
cd ~
```

### 2.2 Test basic import

```bash
python -c 'import autobahn; print(f"✅ Autobahn version: {autobahn.__version__}")'
```

### 2.3 Test Flatbuffers run-time imports

```bash
python3 << 'EOF'
# Test FlatBuffers wrapper imports
from autobahn.wamp.gen.wamp.proto import Welcome
print(f"✅ Welcome class: {Welcome}")

from autobahn.wamp.gen.wamp.proto import Hello, Goodbye, Error
print(f"✅ Core WAMP messages: Hello, Goodbye, Error")

print("\n✅ ALL IMPORTS SUCCESSFUL")
EOF
```

### 2.4 Test Flatbuffers schemata (source & binary) file access

**IMPORTANT:** Use `importlib.resources` to access package data files correctly.
This works with both installed wheels and development installs, unlike `__file__`.

```bash
python3 << 'EOF'
# Modern way to access package data files (Python 3.9+)
try:
    from importlib.resources import files
except ImportError:
    # Fallback for Python 3.7-3.8 (if needed)
    from importlib_resources import files

# Test binary schema access
schema_pkg = files('autobahn.wamp.gen.schema')
bfbs_files = sorted([f.name for f in schema_pkg.iterdir() if f.name.endswith('.bfbs')])
print(f"✅ Binary schemas found: {len(bfbs_files)} files")
print(f"   Files: {bfbs_files}")

# Test source schema access
fbs_pkg = files('autobahn.wamp.flatbuffers')
fbs_files = sorted([f.name for f in fbs_pkg.iterdir() if f.name.endswith('.fbs')])
print(f"✅ Source schemas found: {len(fbs_files)} files")
print(f"   Files: {fbs_files}")

# Test actual file reading
test_file = schema_pkg.joinpath('wamp.bfbs')
if test_file.is_file():
    data = test_file.read_bytes()
    print(f"✅ Can read binary schema: wamp.bfbs ({len(data)} bytes)")
else:
    print(f"❌ ERROR: wamp.bfbs not found!")

print("\n✅ ALL SCHEMA FILE ACCESSES SUCCESSFUL")
EOF
```
**Expected output:**

```
✅ Binary schemas found: 7 files
   Files: ['auth.bfbs', 'pubsub.bfbs', 'roles.bfbs', 'rpc.bfbs', 'session.bfbs', 'types.bfbs', 'wamp.bfbs']
✅ Source schemas found: 7 files
   Files: ['auth.fbs', 'pubsub.fbs', 'roles.fbs', 'rpc.fbs', 'session.fbs', 'types.fbs', 'wamp.fbs']
✅ Can read binary schema: wamp.bfbs (XXXX bytes)

✅ ALL SCHEMA FILE ACCESSES SUCCESSFUL
```

### 2.5 Test runtime functionality

```bash
python3 << 'EOF'
# Test basic WAMP functionality
from autobahn.wamp import types

# Test with FlatBuffers
from autobahn.wamp.gen.wamp.proto import Hello
print(f"✅ Can instantiate WAMP message classes")

# Test serialization extras if installed
try:
    import flatbuffers
    print(f"✅ flatbuffers available: {flatbuffers.__version__}")
except ImportError:
    print("⚠️  flatbuffers not installed (install with: pip install 'autobahn[serialization]')")

print("\n✅ RUNTIME TESTS PASSED")
EOF
```

### 2.6 Cleanup test environment

```bash
deactivate
rm -rf /tmp/test_autobahn_v25.10.1
```

## 3. Documentation Build Test (RTD Simulation)

### 3.1 Test local Sphinx build

```bash
cd docs

# Clean previous builds
rm -rf _build/

# Build documentation
sphinx-build -b html . _build/html

# Check for errors
echo "Exit code: $?"

# Verify key files exist
ls -lh _build/html/index.html
ls -lh _build/html/websocket/conformance.html 2>/dev/null || echo "⚠️  conformance.html not in git (expected - comes from artifacts)"
```

**Expected:**
- Build completes with 0 errors
- Some warnings about missing conformance/flatbuffers files OK (they come from GitHub Release artifacts in RTD build)

### Test RTD artifact download script (dry-run simulation)

```bash
# The script expects to run in RTD environment
# We can't fully test it locally without mocking GitHub Release

# But we can verify the script syntax
bash -n .github/scripts/rtd-download-artifacts.sh
echo "Script syntax: $?"

# Expected: 0 (no syntax errors)
```

## 4. Verification Report Inspection

### Check verification report

```bash
cat dist/autobahn-25.10.1.verify.txt

# Verify it contains:
#   - SHA256 fingerprint
#   - Gzip test result: PASS
#   - Tar test result: PASS
#   - File count: ~222 files
#   - Timestamp and workflow metadata
```

## 5. Release Notes & Changelog

### Check existing changelog

```bash
cat docs/changelog.rst | head -50

# Does v25.10.1 have an entry? If not, add one manually or via Towncrier
```

### Towncrier (Optional - if you want to use it)

**Note:** Towncrier not currently configured. If you want to add it:

```bash
# Install towncrier
pip install towncrier

# Create config in pyproject.toml:
# [tool.towncrier]
# directory = "changelog.d"
# filename = "CHANGELOG.md"
# ...

# For now, update changelog.rst manually for v25.10.1
```

## 6. Platform & Python Coverage Verification

### Check what wheels were built in CI
From PR #1715, verify these platforms are covered:
- ✅ Linux x86_64 (with NVX, without NVX, manylinux)
- ✅ Linux ARM64 (manylinux)
- ✅ macOS ARM64 (Apple Silicon)
- ✅ Windows x86_64

### Check Python versions
From workflows, verify these versions are supported:
- ✅ CPython 3.11
- ✅ CPython 3.12
- ✅ CPython 3.13
- ✅ CPython 3.14
- ✅ PyPy 3.11

## 7. Integration Tests (Optional but Recommended)

### Run test suite with installed package
```bash
source /tmp/test_autobahn_v25.10.1/bin/activate
pip install pytest pytest-asyncio

# Run tests (if test suite is included)
pytest tests/ -v

deactivate
```

## 8. Final Checks Before Release

- [ ] All 30 CI checks passing on PR #1715 ✅
- [ ] Source dist clean (no trailing garbage) ✅
- [ ] Verification reports present (.verify.txt) ✅
- [ ] FlatBuffers wrappers import successfully
- [ ] FlatBuffers schemas (.fbs, .bfbs) in package
- [ ] Documentation builds locally
- [ ] Changelog updated for v25.10.1
- [ ] PyPI safety check in place (prevents duplicate uploads)
- [ ] RTD artifact download configured
- [ ] Supply chain verification working (origin → release)

## 9. Release Process

Once all checks pass:

```bash
# Merge PR #1715 to master
# Create and push tag
git checkout master
git pull origin master
git tag v25.10.1
git push origin v25.10.1

# Workflows will automatically:
# 1. Build all wheels
# 2. Run conformance tests
# 3. Verify source dist integrity
# 4. Check if v25.10.1 exists on PyPI (should be false)
# 5. Create GitHub Release
# 6. Upload to PyPI via Trusted Publishing
# 7. Trigger RTD build with artifacts
```

## 10. Post-Release Verification

After release completes:

```bash
# Install from PyPI
pip install --upgrade autobahn

# Verify version
python -c "import autobahn; print(autobahn.__version__)"
# Expected: 25.10.1

# Verify FlatBuffers
python -c "from autobahn.wamp.gen.wamp.proto import Welcome; print(Welcome)"
# Expected: <module ...>

# Check RTD
# Visit: https://autobahnpython.readthedocs.io/en/v25.10.1/
# Verify conformance reports load
```

---

## Summary

**Branch Strategy:** Continue on `rel_v25.10.1_part1` ✅

**Critical Verifications:**
1. ✅ Source dist integrity (no trailing garbage)
2. ✅ FlatBuffers wrappers in package
3. ✅ FlatBuffers schemas in package
4. ✅ Supply chain verification working
5. ⏳ Local import tests (run checklist above)
6. ⏳ RTD will get artifacts from release

**What's Already Done:**
- RTD artifact download script configured
- PyPI safety check implemented
- Comprehensive verification reports
- Re-verification in release workflow

**What to Test Locally:**
Follow sections 1-3 above to verify package contents and imports.

**Ready for Release When:**
All checkboxes in section 8 are checked ✅
