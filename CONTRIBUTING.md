# Contributing

## Development

Use Python 3.10-3.12 and keep changes focused on authorized local exports, validation,
transcription and packaging.

```bash
python -m venv .venv
python -m pip install -e ".[dev]"
python -m ruff check .
python -m mypy
python -m pytest --cov
python -m build
```

## Pull Requests

- Add or update tests for behavior changes.
- Do not commit real collection jobs, media, comments, credentials or browser state.
- Keep external-platform claims tied to reproducible, authorized test evidence.
- Update `CHANGELOG.md` for user-visible changes.

Report security issues privately as described in `SECURITY.md`.
