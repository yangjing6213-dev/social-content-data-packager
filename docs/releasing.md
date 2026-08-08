# Releasing

This repository is release-preparation only until a human approves a specific GitHub write.

1. Read `AGENTS.md`, `README.md`, `CONTRIBUTING.md` and `SECURITY.md`.
2. Inspect status, diff, current commit, branch and remote.
3. Run Secret/history, large-file, provenance/license, README-link and GitHub read-only checks.
4. Run the real test, lint, typecheck (if configured), dependency audit and build commands.
5. Generate and retain a local pre-publish evidence report with exact evidence and proposed actions.
6. Stop when `READY_TO_PUBLISH=NO`, or when the user has not supplied the exact approval token.

No release workflow in this repository may publish, create a repository, alter settings or create
issues/PRs/comments implicitly. After explicit approval, perform only the listed minimum action and
recheck state after each step. Stop immediately on GitHub restrictions, rate limits or authentication
conflicts.
