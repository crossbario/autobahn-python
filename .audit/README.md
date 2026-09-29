# AI-assistance disclosure files

Every pull request adds one file here, named `<github-username>_<branch>.md` (for example
`jane_fix_1234.md`), declaring whether AI-assistance tools were used to help create it. The pull
request is not accepted without it. The full rules are in
[CONTRIBUTING.md](../CONTRIBUTING.md#ai-assistance-disclosure).

The file must contain exactly this, with the box that applies ticked:

```markdown
- [ ] I did **not** use any AI-assistance tools to help create this pull request.
- [x] I **did** use AI-assistance tools to *help* create this pull request.
- [x] I have read, understood and followed the project's AI_POLICY.md when creating code, documentation etc. for this pull request.

Submitted by: @<github-username>
Date: <YYYY-MM-DD>
Related issue(s): #<issue-number>
Branch: <github-username>:<branch>
```

- Exactly one of the first two boxes, and always the third.
- `Related issue(s):` references the issue the pull request addresses. Every change starts with an issue.
- **Filename:** an underscore between user name and branch, and only `A-Z a-z 0-9 . _ -`. A `:` or `/`
  in a filename breaks `git checkout` on Windows. The `:` belongs only inside the file, on the
  `Branch:` line.

With the project tooling, `just --justfile .ai/justfile generate-audit-file` creates this file for
the current branch.

This README is deployed from wamp-proto/wamp-cicd (`templates/audit-README.md`) and kept
byte-identical by a drift check. Change it there, not here.
