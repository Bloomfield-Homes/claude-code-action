# Bloomfield Homes fork

`main` mirrors `anthropics/claude-code-action` and is never committed to. The Laurel patch lives on `laurel`, based on an upstream release tag.

## Patch

- `src/branding.ts` reads `AGENT_DISPLAY_NAME` and `AGENT_SIGNATURE` from the environment.
- Unset, every string matches upstream, so upstream tests pass unchanged.
- Laurel sets `AGENT_DISPLAY_NAME: Laurel` on the action step.

## Upgrade to a new upstream release

```bash
gh repo sync Bloomfield-Homes/claude-code-action   # fast-forward main
git fetch upstream --tags
git rebase --onto <new-tag> <old-tag> laurel
bun run typecheck && bun test
git push --force-with-lease origin laurel
```

Then pin the new `laurel` SHA in `org-dotgithub/.github/workflows/laurel.yml`.
