# Contributing

Thank you for your interest in contributing! This project is part of the
[WAMP](https://wamp-proto.org/) group of projects: the protocol specification,
client libraries in several languages, the Crossbar.io router, and supporting
tools. All of them share this contribution guide, so the workflow below is the
same in every repository of the group.

Everything specific to *this* repository — development setup, how to run the
tests, supported platforms, and any additional agreements it requires — is in
[DEVELOPMENT.md](DEVELOPMENT.md).

## Questions, bugs and features

- A **question** is not an issue. Please ask it in this repository's
  **GitHub Discussions**.
- A **bug** is an unexpected or unwanted behavior of the software, or incorrect
  documentation. Please include the project version, the language runtime and
  its version (e.g. CPython or PyPy and version, Node.js, JVM), your operating
  system, a minimal way to reproduce the problem, and the full error output or
  traceback if there is one.
- A **feature** is a wish for new functionality or documentation. Please
  describe your actual use case and goals, *why* it matters to you, and
  optionally a proposed solution.

## The workflow: GitHub issue first

**Every change starts with a GitHub issue.** Before you write code, file an
issue (or find an existing one) and get agreement from a maintainer that the
change is wanted and how it should be approached.

Why this matters:

- It is where the design is agreed *before* effort is spent. A pull request
  that arrives without an issue may be well done and still not be mergeable,
  because it solves a different problem than the one the project has, or
  solves it in a way the project cannot take.
- It is the anchor for the whole change: the branch, the audit file, the
  changelog entry and the pull request all reference the issue number.
- It makes the history reviewable years later: *why* a change was made lives
  in the issue, *what* was changed lives in the pull request.

Then:

1. **Fork** the repository on GitHub.
2. **Create a branch** from the repository's default branch (usually `master`,
   in a few repositories `main`), named after the issue, e.g. `fix_1234`.
3. **Write tests first** — see [Test-driven: red, then green](#test-driven-red-then-green).
4. **Make your change**, following the code style of the surrounding code.
5. **Add a changelog entry** for any user-visible change, referencing the
   issue (e.g. `(#1234)`).
6. **Add the AI-assistance disclosure** audit file — see
   [AI-assistance disclosure](#ai-assistance-disclosure). This is required.
7. **Run the tests** locally, on every runtime this project supports (for
   example both CPython and PyPy for the Python projects).
   [DEVELOPMENT.md](DEVELOPMENT.md) says which runtimes, and how.
8. **Open a pull request** against the default branch that references the issue
   (`Closes #1234`), and fill in the pull request template.

Pull requests are reviewed on GitHub. Maintainers then land approved pull
requests **locally, signed by the maintainer**, rather than with GitHub's merge
button, so that every change on the default branch carries a verifiable
signature. Your commits keep their authorship, and the pull request still shows
as merged once the signed change is pushed.

Git tags and releases are created by maintainers only.

## Test-driven: red, then green

Changes are proven with tests, in two visible steps. This leaves reviewers with
a completely convincing pull request, and the test stays in the suite so the
problem cannot silently come back. (What a "test" is depends on the project -
unit tests, conformance test vectors, a build check; see
[DEVELOPMENT.md](DEVELOPMENT.md). Purely editorial changes skip the red/green
steps, but still start from an issue.)

1. **Agree on the issue.** For a bug: agreement that the current behavior *is*
   wrong. For a feature: agreement on the new behavior.
2. **Red.** Push a test that demonstrates the bug (or specifies the missing
   feature). It must **fail** — locally and in CI. Leave a pull request comment
   with your local failure output and a link to the failing CI run.
3. **Implement** the fix or feature, and push it to the same pull request.
4. **Green.** The test now **passes** — locally and in CI. Leave a pull request
   comment with your local success output and a link to the passing CI run.
5. **Request review**: comment "Ready for review & merge!".

Example comments:

````markdown
## Bug confirmed (red)

```
$ just test
...
FAILED test_foo.py::test_bar - AssertionError: expected X, got Y
```

CI fails as expected: <link to the failing CI run>
````

````markdown
## Fix verified (green)

```
$ just test
...
PASSED test_foo.py::test_bar
```

CI passes: <link to the passing CI run>

Ready for review & merge!
````

## AI-assistance disclosure

Every pull request must include an **audit file** declaring whether
AI-assistance tools (e.g. GitHub Copilot, Claude, ChatGPT, Cursor) were used to
help create it, and confirming you have read and followed the
[AI Policy](https://github.com/wamp-proto/wamp-ai/blob/main/AI_POLICY.md).
Submitting code generated *primarily* by AI, or for which you cannot claim
human authorship, is not permitted.

Add a file at `.audit/<github-username>_<branch>.md` (for example
`.audit/jane_fix_1234.md`) containing exactly this, with the box that applies
ticked:

```markdown
- [ ] I did **not** use any AI-assistance tools to help create this pull request.
- [x] I **did** use AI-assistance tools to *help* create this pull request.
- [x] I have read, understood and followed the project's AI_POLICY.md when creating code, documentation etc. for this pull request.

Submitted by: @<github-username>
Date: <YYYY-MM-DD>
Related issue(s): #<issue-number>
Branch: <github-username>:<branch>
```

Exactly one of the first two boxes must be ticked, and the third box always.
The `Related issue(s):` line must reference the issue the pull request
addresses — which is one more reason the issue comes first.

> **Filename:** use `<github-username>_<branch>.md` with an **underscore**, and
> only cross-platform-safe characters (`A-Z a-z 0-9 . _ -`). Do **not** copy
> GitHub's `owner:branch` label into the filename — a `:` (or `/`) in a filename
> breaks `git checkout` on Windows. The `:` belongs only *inside* the file, on
> the `Branch:` line.

If you use the project's tooling, `just --justfile .ai/justfile generate-audit-file`
creates this file for your current branch.

## License

Your contributions are licensed under the license in this repository's
[LICENSE](LICENSE) file. If this repository requires an additional contributor
agreement, it is described in [DEVELOPMENT.md](DEVELOPMENT.md).
