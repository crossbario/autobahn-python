# AI Disclosure Process

## AI Disclosure Process: Purpose

This document defines a robust, tamper-evident, and
cryptographically verifiable process for contributors to disclose
their use of AI assistance and acknowledgment of the project's AI
policy as part of every Pull Request (PR). The process ensures
permanent, auditable records that can withstand legal and
regulatory scrutiny.

---

## 1. Issue Disclosures

- When creating an issue (feature request or bug report),
  contributors **disclose AI assistance** via GitHub issue
  templates.
- This disclosure is tracked within GitHub’s platform (metadata,
  comments).
- **Note:** This method provides “good evidence” but is not
  cryptographically hard evidence, as issue metadata can be
  modified or deleted by users with appropriate permissions.

---

## 2. Pull Request (PR) Disclosures

- Every PR **must include exactly one disclosure file** in the
  form: `.audit/<branch-name>.md`
  - The `<branch-name>` must be identical to the branch used for
    the PR.
- This file is committed on the contributor’s branch, before
  opening the PR.
- The file becomes part of the main repository’s history upon
  merge, providing immutable, permanent, and
  cryptographically-verifiable evidence.

---

## 3. Disclosure File Format and Content

**Filename:** `.audit/<branch-name>.md`

- `<branch-name>` must exactly match the Git branch for the PR.

**File format:** Markdown

**Required content:** (Replace placeholders with actual values as
appropriate.)

```
## AI Assistance Disclosure

- [x] I did **not** use AI-assisted tools to help create this pull request.
- [ ] I used AI-assisted tools to help create this pull request.

- [x] I have read, understood and followed the projects' [AI Policy](../AI_POLICY.rst) when creating this pull request.

Submitted by: @<your-github-username>
Date: <YYYY-MM-DD>
Related issue(s): #<issue-number>
Branch: <branch-name>
```

**Rules:**

- **Exactly one option** (AI/no AI) must be checked (`[x]`), the
  other unchecked (`[ ]`).
- The **AI Policy acknowledgment** box must be present and
  checked.
- The three footer fields must be filled:
  - `Submitted by`: your GitHub username
  - `Date`: the UTC date (YYYY-MM-DD) the PR was initially opened
    (not when the file was last updated!)
  - `Related issue(s)`: at least one linked issue (use
    `#<issue-number>`)
  - `Branch`: the exact branch name used for the PR

---

## 4. Enforcement and Automation

A GitHub Action will enforce these requirements by running on the
following PR events:

- `opened`
- `synchronize` (new commits pushed)
- `edited`
- `reopened`

**The Action will check:**

- The presence of exactly one `.audit/<branch-name>.md` file.
- That the filename matches the PR branch name.
- That the file is valid Markdown and matches the required
  template/format.
- That exactly one AI disclosure option is checked.
- That the AI Policy acknowledgment is present and checked.
- That the footer fields are present and valid.
- That the `Date:` in the file matches the UTC date the PR was
  first opened (as recorded by GitHub).

**If any check fails,** the PR will be marked as failed and
cannot proceed until corrected.

---

## 5. Git and Organizational Security

- The `.audit/` folder is tracked in Git and must **not** be
  listed in `.gitignore`.
- All contributors and maintainers **must** use 2FA (preferably
  hardware security keys) for GitHub accounts.
- Only humans (not bots) with 2FA may merge PRs.
- All commits (including on forked branches/PRs) **must be
  signed** using GPG, SSH, or S/MIME. Hardware security keys
  (such as Nitrokey) are recommended for signing.
  - The main branch is protected with “require signed commits.”
  - PRs with unsigned commits will not be mergeable.
- Commits are cryptographically verifiable and, together with the
  disclosure file, provide a hard, immutable audit trail.

---

## 6. Example Contributor Workflow

1. **Fork** the repository and create your feature/fix branch
   (e.g., `my-feature-branch`).
2. Implement your changes.
3. Create a file `.audit/my-feature-branch.md` in your branch,
   using the required template above.
4. Ensure all your commits are signed with your hardware security
   key (or other secure method).
5. Open a PR from your fork/branch to the main repository.
6. Update the `Date:` field in your disclosure file to the UTC
   date the PR is opened.
7. Push any changes as needed.
8. The GitHub Action will validate your disclosure file and
   commit signatures.
9. When all checks are green and human review is complete, a
   maintainer with 2FA will merge your PR.

---

## 7. Rationale

- **Immutability & Tamper-Evidence:** All disclosures are part of
  the Git history, cryptographically signed and permanently
  linked to code changes.
- **Traceability:** Each disclosure is explicitly tied to a
  specific PR, branch, author, and date.
- **Human-in-the-Loop:** Only verified humans can merge PRs.
- **Portability:** The process is not GitHub-specific and can be
  migrated to other platforms.
- **Compliance:** Satisfies strict requirements for legal,
  regulatory, and ethical review.

---

## 8. Frequently Asked Questions

**Q: Can `.audit/` be in `.gitignore`?** **A:** No. The `.audit/`
folder must be tracked to include disclosure files in PRs.

**Q: How do I ensure my commits are signed with a hardware key?**
**A:** Set up GPG (or SSH/S/MIME) with your hardware security
key, and configure git to sign all commits.
[See GitHub’s documentation.](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits)

**Q: What if my disclosure file fails validation?** **A:** Update
the file according to the template and push again. The Action
will rerun and revalidate.

**Q: Why not just use GitHub’s PR template or comments?** **A:**
Only files tracked in Git history are cryptographically immutable
and serve as “hard evidence.”

---

## 9. Example Disclosure File

```
## AI Assistance Disclosure

- [x] I did **not** use AI-assisted tools to help create this pull request.
- [ ] I used AI-assisted tools to help create this pull request.

- [x] I have read, understood and followed the projects' [AI Policy](../AI_POLICY.rst) when creating this pull request.

Submitted by: @oberstet
Date: 2025-06-26
Related issue(s): #123
Branch: my-feature-branch
```

---

**This process ensures that every code change merged into the
project is accompanied by a cryptographically secure, immutable,
and auditable disclosure of AI assistance and policy compliance,
providing hard evidence for all future audits, legal inquiries,
and compliance needs.**
