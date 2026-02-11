# Contributing

Thanks for your interest in contributing to P2PP.

If this is your first contribution, this page walks you through the process from code changes to review.

## First contribution checklist

1. Fork this repository to your own GitHub account.
2. Create a branch for your change.
3. Implement your change in small, reviewable commits.
4. Add tests:
   - Include unit tests for changed behavior.
   - Add an end-to-end (e2e) test when the change affects a full user workflow and an e2e test is practical.
5. Update docs when behavior, configuration, or usage changes.
6. Push your branch and open a Pull Request (PR).
7. Ask for review and address feedback.

Example branch setup:

```sh
git checkout -b yourname/short-change-description
```

## Testing expectations

Before opening a PR:

- Run the relevant unit tests and confirm they pass.
- Add or update unit tests for bug fixes and new features.
- If possible, include e2e coverage for user-facing flows impacted by your change.
- Mention what you tested in the PR description (for example: "unit tests passed", "manual validation", "e2e added/skipped with reason").

If you are not sure which tests to run, open the PR anyway and call that out explicitly so maintainers can guide you.

## Opening a Pull Request

When your branch is ready:

1. Push your branch to your fork.
2. Open a PR to `vhspace/p2pp:master`.
3. In the PR description, include:
   - What changed and why.
   - Screenshots/logs for UI or output changes (if applicable).
   - Test evidence (unit tests, e2e tests, or why e2e was not feasible).
   - Any follow-up work or known limitations.
4. Mark the PR ready for review.

After review starts:

- Respond to comments and push follow-up commits.
- Keep discussion focused on behavior and correctness.
- Re-run tests after substantial updates.

## Documentation updates

When you've implemented a new feature, please document it in our docs. This helps maintain the project and helps others use your feature.

The documentation content is in `docs/`. MkDocs is configured via `docs/_p2pp/mkdocs.yml`.

### Local preview

```sh
python3 -m venv .venv-mkdocs
source .venv-mkdocs/bin/activate
python -m pip install -r docs/_p2pp/mkdocs-requirements.txt
mkdocs serve -f docs/_p2pp/mkdocs.yml
```

### Deploy to GitHub Pages

Docs are automatically deployed to GitHub Pages from GitHub Actions when changes to docs are merged into `master`.

If you need to deploy manually, MkDocs can still push the generated site to the `gh-pages` branch:

```sh
source .venv-mkdocs/bin/activate
mkdocs gh-deploy -f docs/_p2pp/mkdocs.yml --clean
```

If deployment fails due to GitHub API rate limits in `git-committers` / `git-authors`, set `GITHUB_TOKEN=...` and retry.
