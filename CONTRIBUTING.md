# Contributing

## Branching

Branch from `dev`, not from `main`.

```bash
git checkout dev
git pull origin dev
git checkout -b feature/your-description
```

## Commits

Use [Conventional Commits](https://www.conventionalcommits.org/):

| Prefix | When to use |
|---|---|
| `feat` | New functionality |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code restructure, no behavior change |
| `chore` | Tooling, manifests, config |

Keep subject lines ≤ 72 characters.

## Pull requests

- Target branch: `dev`
- One logical change per PR
- Squash before merging if the branch has noisy intermediate commits

## Code style

- Python: follow Odoo conventions (`_name`, `_description`, `_rec_name`)
- XML views: one file per model, sorted by view type
- No trailing whitespace, no Windows line endings
