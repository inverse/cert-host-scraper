 # AGENTS.md

 This project uses **Python** and **uv** for dependency management.

 ## Running tests

 ```bash
 uv run pytest
```

With coverage:

```bash
uv run pytest --cov
 ```

 ## Dependency management

 Install/resolve dependencies:

 ```bash
 uv sync
```

Add a dependency:

 ```bash
 uv add <pkg>
 ```

 ## Linting

Lint with pre-commit:

 ```bash
  uv run pre-commit run --a
```

 ## Pull requests

Always commit on a branch.

This project uses [commitizen](https://commitizen-tools.github.io/commitizen/) (v4) via pre-commit to enforce
[Conventional Commits](https://www.conventionalcommits.org/) on every commit message.

Commit messages must follow the format:

```text
<type>[optional scope]: <description>

[optional body]
```

Common types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `ci`, `style`.

You can stage and commit as usual -- commitizen validates the message automatically at commit time.

Use `gh` CLI for creating the PR — it will pre-fill the body from `.github/PULL_REQUEST_TEMPLATE.md`.
