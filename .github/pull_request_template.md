<!--
Thank you for contributing! Please read CONTRIBUTING.md first - in particular:
GitHub issue first, red -> green tests, and the AI-assistance disclosure file.
-->

## Description

<!-- What does this pull request change, and why? -->

## Related issue

Closes #

<!-- Every change starts with a GitHub issue where the approach was agreed (see CONTRIBUTING.md). -->

## Checklist

- [ ] The issue above exists, and the approach was agreed there
- [ ] Red, then green: a failing test first, then the change that makes it pass, with links to both
      CI runs in pull request comments (purely editorial changes skip this)
- [ ] Tests pass locally on every runtime this project supports (see DEVELOPMENT.md)
- [ ] Changelog entry referencing the issue, for any user-visible change
- [ ] AI-assistance disclosure file added at `.audit/<github-username>_<branch>.md`

## AI-assistance disclosure

**Required.** Add `.audit/<github-username>_<branch>.md` with exactly this content, ticking the box
that applies:

```markdown
- [ ] I did **not** use any AI-assistance tools to help create this pull request.
- [x] I **did** use AI-assistance tools to *help* create this pull request.
- [x] I have read, understood and followed the project's AI_POLICY.md when creating code, documentation etc. for this pull request.

Submitted by: @<github-username>
Date: <YYYY-MM-DD>
Related issue(s): #<issue-number>
Branch: <github-username>:<branch>
```

Exactly one of the first two boxes must be ticked, and always the third. In the **filename**, use an
underscore, never `:` or `/` (those break `git checkout` on Windows). Details are in CONTRIBUTING.md.
