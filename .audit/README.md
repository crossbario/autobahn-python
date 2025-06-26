Audit evidence (disclosure) files (per PR) need to be put here by
human contributor (PR submitter), named `<branch-name>.md`.

The disclosure file must **follow the exact format and content**
as described below.

**Example 1** file contents of a disclosure file
`.audit/<branch-name>.md`:

```
## AI Assistance Disclosure

- [ ] I did **not** use any AI-assistance tools to help create this pull request.
- [x] I **did** use AI-assistance tools to *help* create this pull request.
- [x] I have read, understood and followed the projects' [AI Policy](https://github.com/crossbario/autobahn-python/blob/main/AI_POLICY.md) when creating code, documentation etc. for this pull request.

Submitted by: @your-github-username
Date: YYYY-MM-DD
Related issue(s): #issue-number
Branch: branch-name
```

**OR**

**Example 2** file contents of a disclosure file
`.audit/<branch-name>.md`:

```
## AI Assistance Disclosure

- [x] I did **not** use any AI-assistance tools to help create this pull request.
- [ ] I **did** use AI-assistance tools to *help* create this pull request.
- [x] I have read, understood and followed the projects' [AI Policy](https://github.com/crossbario/autobahn-python/blob/main/AI_POLICY.md) when creating code, documentation etc. for this pull request.

Submitted by: @your-github-username
Date: YYYY-MM-DD
Related issue(s): #issue-number
Branch: branch-name
```

**Example 1 OR Example 2** show the only valid two variants. The
disclosure file cannot have both or none of the first two marks
checked, and you must always have the last tick checked.
