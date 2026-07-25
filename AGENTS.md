 # AGENTS.md

 This project uses **Python** and **uv** for dependency management.

 ## Running tests

 ```bash
 uv run pytest
 ```

 ## Common commands

 ```bash
 uv sync          # Install/resolve dependencies
 uv run pytest    # Run the test suite
 uv add <pkg>     # Add a dependency
 uv run pre-commit run --all-files  # Run pre-commit hooks on all files
 ```

 ## Committing

 This project uses [commitizen](https://commitizen-tools.github.io/commitizen/) (v4) via pre-commit to enforce
 [Conventional Commits](https://www.conventionalcommits.org/) on every commit message.

 Commit messages must follow the format:

 ```text
 <type>[optional scope]: <description>

 [optional body]
 ```

 Common types: `feat`, `fix`, `refactor`, `chore`, `docs`, `test`, `ci`, `style`.

 You can stage and commit as usual -- commitizen validates the message automatically at commit time.

 ### Commit quickly with cz (recommended)

 ```bash
 uv run cz commit   # Interactive commit with commitizen prompt
 ```
