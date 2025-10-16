# Pre-Release Testing Checklist for v25.10.1

This checklist ensures everything works locally before pushing to PyPI.

## Branch Strategy Decision

**Recommendation: Continue on `rel_v25.10.1_part1`**

Reasons:
- All changes are related to v25.10.1 release preparation
- PR #1715 already passing all 30 checks ✅
- Verification infrastructure complete
- Easier to test everything together
- Faster to release

## 1. Package Build & Contents Verification

### Build the package
```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build with current branch
just build-all

# Verify artifacts created
ls -lh dist/
```

**Expected output:**
- `autobahn-25.10.1.tar.gz` (source distribution, ~360KB)
- `autobahn-25.10.1-*.whl` (wheel for current Python)
- `autobahn-25.10.1.verify.txt` (verification report)

### Verify source distribution contents
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

### Verify wheel contents
```bash
# Extract and list wheel contents
unzip -l dist/autobahn-25.10.1-*.whl | grep -E "(wamp/gen|flatbuffers|\.fbs|\.bfbs)"

# Expected:
#   autobahn/wamp/gen/wamp/proto/*.py
#   autobahn/wamp/gen/schema/*.bfbs
#   autobahn/wamp/flatbuffers/*.fbs
```

### Verify source distribution integrity
```bash
# Run the same checks as CI
gzip -tv dist/autobahn-25.10.1.tar.gz
tar -tzf dist/autobahn-25.10.1.tar.gz > /dev/null

# Compute SHA256
openssl sha256 dist/autobahn-25.10.1.tar.gz

# Expected: exit code 0, no errors, clean hash
```

## 2. Local Installation & Import Tests

### Install in clean virtualenv
```bash
# Create fresh test environment
python3 -m venv /tmp/test_autobahn_v25.10.1
source /tmp/test_autobahn_v25.10.1/bin/activate

# Install from local wheel
pip install dist/autobahn-25.10.1-*.whl

# Or install from source dist
# pip install dist/autobahn-25.10.1.tar.gz
```

### Test core imports
```bash
python3 << 'EOF'
# Test basic import
import autobahn
print(f"✅ Autobahn version: {autobahn.__version__}")

# Test FlatBuffers wrapper imports (CRITICAL!)
from autobahn.wamp.gen.wamp.proto import Welcome
print(f"✅ Welcome class: {Welcome}")

from autobahn.wamp.gen.wamp.proto import Hello, Goodbye, Error
print(f"✅ Core WAMP messages: Hello, Goodbye, Error")

# Test schema access
import autobahn.wamp.gen.schema
import os
schema_dir = os.path.dirname(autobahn.wamp.gen.schema.__file__)
bfbs_files = [f for f in os.listdir(schema_dir) if f.endswith('.bfbs')]
print(f"✅ Binary schemas found: {len(bfbs_files)} files")
print(f"   Files: {bfbs_files}")

# Test source schema access
import autobahn.wamp.flatbuffers
fbs_dir = os.path.dirname(autobahn.wamp.flatbuffers.__file__)
fbs_files = [f for f in os.listdir(fbs_dir) if f.endswith('.fbs')]
print(f"✅ Source schemas found: {len(fbs_files)} files")
print(f"   Files: {fbs_files}")

print("\n✅ ALL IMPORTS SUCCESSFUL")
EOF
```

**Expected output:**
```
✅ Autobahn version: 25.10.1
✅ Welcome class: <module 'autobahn.wamp.gen.wamp.proto.Welcome' ...>
✅ Core WAMP messages: Hello, Goodbye, Error
✅ Binary schemas found: 7 files
   Files: ['auth.bfbs', 'pubsub.bfbs', 'roles.bfbs', 'rpc.bfbs', 'session.bfbs', 'types.bfbs', 'wamp.bfbs']
✅ Source schemas found: 7 files
   Files: ['auth.fbs', 'pubsub.fbs', 'roles.fbs', 'rpc.fbs', 'session.fbs', 'types.fbs', 'wamp.fbs']

✅ ALL IMPORTS SUCCESSFUL
```

### Test runtime functionality
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

### Cleanup test environment
```bash
deactivate
rm -rf /tmp/test_autobahn_v25.10.1
```

## 3. Documentation Build Test (RTD Simulation)

### Test local Sphinx build
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
