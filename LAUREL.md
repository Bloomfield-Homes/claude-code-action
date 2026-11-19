# Bloomfield Homes fork

`main` mirrors `anthropics/claude-code-action` and is never committed to. The Laurel patch lives on `laurel`, based on an upstream release tag.

## Patch

- `src/branding.ts` reads `AGENT_DISPLAY_NAME`, `AGENT_SIGNATURE` and `AGENT_SPINNER_URL` from the environment.
- `assets/laurel-spinner.gif` is the Laurel spinner, built from the laurel-agent likeness SVG.
- Unset, every string matches upstream, so upstream tests pass unchanged.
- Laurel sets `AGENT_DISPLAY_NAME: Laurel` on the action step.

## Upgrade to a new upstream release

`laurel` is protected (PR review, no force-push), so upgrades merge rather than rebase.

```bash
gh repo sync Bloomfield-Homes/claude-code-action   # fast-forward main
git fetch upstream --tags
git checkout -b upgrade/<new-tag> origin/laurel
git merge <new-tag>
bun run typecheck && bun test
git push origin upgrade/<new-tag>   # open a PR into laurel
```

After it merges, pin the new `laurel` SHA in `org-dotgithub/.github/workflows/laurel.yml`.
