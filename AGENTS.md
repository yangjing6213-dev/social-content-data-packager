# Project Overview

`social-content-data-packager` is a Python 3.10+ CLI that validates and packages user-provided
DATATOOL exports, with optional local Whisper transcription and an authorized browser/CDP collector.

# Repository Structure

- `src/social_content_data_packager/`: package and CLI implementation.
- `tests/`: unit and integration-style local tests.
- `examples/`: synthetic metadata examples only.
- `docs/`: workflow, compatibility, architecture and release standards.
- `.github/`: CI, CodeQL, Dependabot and contribution templates.

# Development Environment

The core CLI is local-first and needs Python 3.10+. FFmpeg/FFprobe are required for media validation
or Whisper transcription. Browser collection additionally needs a user-created isolated Edge/CDP
session and the user-installed DATATOOL extension. No database, GPU or CUDA runtime is required by
the core package. The in-progress `collect` feature is excluded from the current release candidate;
do not describe it as a stable released command.

# Development Commands

Use the project virtual environment when available. Install editable development dependencies with
`python -m pip install -e ".[dev]"`; browser collection additionally needs `.[browser]` and a user-run
isolated Edge/CDP session.

# Build Commands

Run `python -m build` when the `build` package is installed.

# Test Commands

Run `python -m pytest --cov` and retain the exit code and summary.

# Lint / Format Commands

Run `python -m ruff check .` and `python -m mypy`. Do not claim a command passed if it was unavailable.

# Dependency Rules

Respect `pyproject.toml` version bounds and existing lock/provenance evidence. Do not silently upgrade
dependencies or execute unreviewed install scripts.

# Security Rules

Operate only on public or explicitly authorized exports. Browser automation must use a user-created
isolated profile and an already authorized session; never bypass login, CAPTCHA, paywalls or platform
controls.

# Secret Rules

Never commit API keys, tokens, passwords, cookies, signed URLs, private keys, real `.env` values,
personal data or raw collection outputs. Redact findings and rotate exposed credentials before release.

# Documentation Rules

Agents must read `AGENTS.md`, `README.md`, `README.en.md`, `CONTRIBUTING.md` and `SECURITY.md` before
starting work. `README.md` is the Simplified Chinese primary document; `README.en.md` must stay factually
synchronized. Changes to public APIs, installation, configuration, CLI behavior or UI require synchronized docs and
an entry in `CHANGELOG.md`.
Changes to public APIs, installation, configuration, CLI behavior or UI require synchronized docs and
an entry in `CHANGELOG.md`.

# Visual Asset Decision Policy

This repository follows ENHE GitHub Open Source Standard v1.2 and its
`VISUAL_ASSET_POLICY = OPTIONAL_BY_PROJECT` rule. The current project is a Python CLI and data-packaging
tool, so its stable release does not require a Logo or Cover and may use a text-only README header.

```text
CURRENT_PROJECT_VISUAL_ASSETS_REQUIRED = NO
CURRENT_PROJECT_VISUAL_POLICY_REASON = CLI_AND_DATA_PACKAGING_TOOL
VISUAL_ASSETS_STATUS = NOT_REQUIRED_FOR_CURRENT_RELEASE
```

Missing visual assets do not block this Release Candidate and must not be reported as a security or
quality failure. If a future GUI, brand page or product-presentation need makes visuals useful, handle
them as a separate optional task. Any future asset still requires documented provenance, redistribution
rights, truthful content, privacy review and working README references. Never use unknown-source images,
placeholders, broken links, fake interfaces or metrics, unlicensed third-party brands, watermarked files
or unreviewed legacy artwork. This policy does not weaken any secret, privacy, license, test, build,
documentation or GitHub-platform gate.

# Git Rules

Preserve unrelated dirty worktree changes. Inspect `git status`, `git diff`, staged files and history
before any commit. Use focused Conventional Commit prefixes (`feat:`, `fix:`, `docs:`, `test:`,
`ci:`, `security:` and similar). Never force-push `main`.

# Release Rules

Follow `docs/REPOSITORY_STANDARD.md` and `docs/releasing.md`. Complete and retain a local pre-publish evidence report first.
Publishing is blocked unless `READY_TO_PUBLISH=YES` and the user supplies the exact token
`APPROVE_GITHUB_PUBLISH` for the explicitly listed actions.

# Prohibited Actions

No credential submission, unauthorized collection, platform bypass, spam interaction, repository or
release creation, push, force-push, remote settings change, or hidden retry around GitHub restrictions.

# Definition of Done

Relevant tests, lint, typecheck and build commands pass; security and license evidence is recorded;
docs are synchronized; the report states verified facts, unknowns, blockers and publish readiness.
